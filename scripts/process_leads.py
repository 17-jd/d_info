#!/usr/bin/env python3
"""
process_leads.py — Aggregate, clean, de-duplicate, score, and tier the raw
lead files produced by the research agents.

Input : data/raw/*.psv   (pipe-delimited, 19 columns, one business per line)
Output: data/leads_master.csv            (organised: scored, tiered, sorted)
        data/leads_tier_A_callfirst.csv   (hottest leads — call these first)
        data/leads_raw_combined.csv       (raw collected view, minimal columns)
        data/_build_summary.txt           (counts + QA notes)

NO-GHOST-LEAD RULE: any row without a real source_url is DROPPED. We never
invent data; blanks stay blank.
"""
import csv
import glob
import os
import re
import sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
RAW_DIR = os.path.join(ROOT, "data", "raw")
OUT_DIR = os.path.join(ROOT, "data")

# The 19 fields each agent emits, in order.
FIELDS = [
    "company_name", "category", "sub_category", "area", "address", "website",
    "phone", "email", "source_url", "source_type", "size_hint", "hardware_need",
    "buying_trigger", "expansion_signal", "lead_score", "priority_tier",
    "contact_approach", "verification_status", "notes",
]

# Fallback base score per category (used only if an agent left lead_score blank
# or unpar. Reflects hardware-spend + recurring potential for an
# IT-hardware reseller in Surat. Agent-supplied scores take precedence.
CATEGORY_BASE = {
    "Lab-Grown Diamond": 82,
    "Diamond & Bourse": 80,
    "IT & Software": 73,
    "GIDC Manufacturing": 74,
    "Healthcare": 74,
    "Education": 72,
    "Media/Video/Photo": 70,
    "Architecture & CAD/Engineering": 70,
    "Textile Manufacturing": 70,
    "Jewellery": 70,
    "Textile Trade & Design": 66,
    "Hospitality & Real Estate": 66,
    "BPO/Logistics/Print": 66,
    "Finance & Professional": 64,
    "Government & PSU": 70,
    "Automobile Dealership": 68,
    "Retail & Supermarket": 66,
}

SUFFIX_TOKENS = {
    "pvt", "private", "ltd", "limited", "llp", "inc", "co", "company",
    "the", "and", "&", "india", "surat", "enterprise", "enterprises",
    "technologies", "technology", "solutions", "infotech", "industries",
}


def normalize_name(s: str) -> str:
    """Normalise a company name for de-duplication."""
    s = (s or "").lower()
    s = re.sub(r"[^a-z0-9\s]", " ", s)
    toks = [t for t in s.split() if t and t not in SUFFIX_TOKENS]
    return " ".join(toks).strip()


def parse_score(raw: str, category: str, has_contact: bool, has_signal: bool) -> int:
    """Extract an integer score; fall back to a category heuristic."""
    m = re.search(r"\d{1,3}", raw or "")
    if m:
        val = int(m.group())
    else:
        val = CATEGORY_BASE.get(category, 60)
        if has_signal:
            val += 8
        if has_contact:
            val += 4
    return max(0, min(100, val))


def tier_for(score: int) -> str:
    if score >= 75:
        return "A"
    if score >= 60:
        return "B"
    return "C"


def looks_like_url(u: str) -> bool:
    return bool(re.match(r"https?://", (u or "").strip(), re.I))


def split_line(line: str):
    """Split a pipe line into exactly len(FIELDS) parts (best-effort)."""
    parts = line.rstrip("\n").split("|")
    if len(parts) == len(FIELDS):
        return parts
    if len(parts) > len(FIELDS):
        # Extra pipes leaked into a field; fold the overflow into notes (last).
        head = parts[: len(FIELDS) - 1]
        tail = " ".join(parts[len(FIELDS) - 1:])
        return head + [tail]
    # Too few fields: pad with blanks.
    return parts + [""] * (len(FIELDS) - len(parts))


def main():
    files = sorted(glob.glob(os.path.join(RAW_DIR, "*.psv")))
    if not files:
        print(f"No .psv files found in {RAW_DIR}. Run the research agents first.")
        sys.exit(1)

    records = []
    stats = defaultdict(int)
    per_file = {}

    for fp in files:
        name = os.path.basename(fp)
        kept_here = 0
        with open(fp, encoding="utf-8", errors="replace") as fh:
            for i, line in enumerate(fh):
                if not line.strip():
                    continue
                # Skip header lines (the first line, or any repeated header).
                if line.startswith("company_name|category|"):
                    continue
                parts = split_line(line)
                rec = dict(zip(FIELDS, (p.strip() for p in parts)))
                stats["rows_read"] += 1

                if not rec["company_name"]:
                    stats["dropped_no_name"] += 1
                    continue
                if not looks_like_url(rec["source_url"]):
                    stats["dropped_no_source"] += 1
                    continue

                has_contact = bool(rec["phone"] or rec["email"])
                has_signal = bool(rec["expansion_signal"] or rec["buying_trigger"])
                rec["lead_score"] = parse_score(
                    rec["lead_score"], rec["category"], has_contact, has_signal
                )
                rec["priority_tier"] = tier_for(rec["lead_score"])
                rec["_src_file"] = name
                records.append(rec)
                kept_here += 1
        per_file[name] = kept_here

    # ---- De-duplicate on normalised company name; merge to enrich. ----
    merged = {}
    for rec in records:
        key = normalize_name(rec["company_name"])
        if not key:
            key = rec["company_name"].lower().strip()
        if key not in merged:
            merged[key] = rec
            continue
        stats["duplicates_merged"] += 1
        keep = merged[key]
        other = rec
        # Keep the higher-scoring record as the base.
        if other["lead_score"] > keep["lead_score"]:
            keep, other = other, keep
        # Fill blank fields on the base from the other record.
        for f in FIELDS:
            if not keep.get(f) and other.get(f):
                keep[f] = other[f]
        # Preserve the secondary source for provenance.
        if other["source_url"] and other["source_url"] != keep["source_url"]:
            extra = f"alt source: {other['source_url']}"
            keep["notes"] = (keep["notes"] + "; " + extra).strip("; ") if keep["notes"] else extra
        merged[key] = keep

    final = list(merged.values())
    # Sort: tier (A,B,C) then score desc then category then name.
    tier_rank = {"A": 0, "B": 1, "C": 2}
    final.sort(key=lambda r: (
        tier_rank.get(r["priority_tier"], 9),
        -r["lead_score"],
        r["category"],
        r["company_name"].lower(),
    ))
    for idx, rec in enumerate(final, 1):
        rec["lead_id"] = f"L{idx:04d}"

    # ---- Write master (organised) CSV. ----
    master_cols = [
        "lead_id", "priority_tier", "lead_score", "company_name", "category",
        "sub_category", "area", "phone", "email", "website", "hardware_need",
        "buying_trigger", "expansion_signal", "contact_approach",
        "verification_status", "address", "source_type", "source_url",
        "size_hint", "notes",
    ]
    master_path = os.path.join(OUT_DIR, "leads_master.csv")
    with open(master_path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=master_cols, extrasaction="ignore")
        w.writeheader()
        for rec in final:
            w.writerow(rec)

    # ---- Write Tier-A call-first CSV. ----
    tierA = [r for r in final if r["priority_tier"] == "A"]
    tierA_path = os.path.join(OUT_DIR, "leads_tier_A_callfirst.csv")
    with open(tierA_path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=master_cols, extrasaction="ignore")
        w.writeheader()
        for rec in tierA:
            w.writerow(rec)

    # ---- Write raw combined (as-collected, minimal) CSV. ----
    raw_cols = ["company_name", "category", "sub_category", "area", "address",
                "website", "phone", "email", "source_url", "source_type"]
    raw_path = os.path.join(OUT_DIR, "leads_raw_combined.csv")
    with open(raw_path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=raw_cols, extrasaction="ignore")
        w.writeheader()
        for rec in final:
            w.writerow(rec)

    # ---- Summary. ----
    by_cat = defaultdict(int)
    by_tier = defaultdict(int)
    with_contact = 0
    for r in final:
        by_cat[r["category"]] += 1
        by_tier[r["priority_tier"]] += 1
        if r["phone"] or r["email"]:
            with_contact += 1

    lines = []
    lines.append("=== LEAD BUILD SUMMARY ===")
    lines.append(f"Source files       : {len(files)}")
    lines.append(f"Rows read          : {stats['rows_read']}")
    lines.append(f"Dropped (no source): {stats['dropped_no_source']}")
    lines.append(f"Dropped (no name)  : {stats['dropped_no_name']}")
    lines.append(f"Duplicates merged  : {stats['duplicates_merged']}")
    lines.append(f"FINAL UNIQUE LEADS : {len(final)}")
    lines.append(f"  with phone/email : {with_contact} ({100*with_contact//max(1,len(final))}%)")
    lines.append("")
    lines.append("By tier:")
    for t in ("A", "B", "C"):
        lines.append(f"  Tier {t}: {by_tier.get(t,0)}")
    lines.append("")
    lines.append("By category:")
    for c in sorted(by_cat, key=lambda k: -by_cat[k]):
        lines.append(f"  {c:<34} {by_cat[c]}")
    lines.append("")
    lines.append("Per source file (kept):")
    for n in sorted(per_file):
        lines.append(f"  {n:<34} {per_file[n]}")
    summary = "\n".join(lines)
    with open(os.path.join(OUT_DIR, "_build_summary.txt"), "w", encoding="utf-8") as fh:
        fh.write(summary + "\n")
    print(summary)
    print(f"\nWrote:\n  {master_path}\n  {tierA_path}\n  {raw_path}")


if __name__ == "__main__":
    main()
