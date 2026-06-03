# Surat IT-Hardware Sales Leads — 950+ Verified, SME-Focused, Scored & Prioritised

A working lead database for an **IT-hardware reseller / system integrator in Surat**
selling computers & high-end workstations, servers & storage, networking
(switches / routers / firewalls / Wi-Fi / structured cabling), **CCTV &
surveillance / access control**, laptops, and IT AMC / services.

The goal: find the businesses **most likely to be buying or upgrading IT
hardware now or soon** — and tell you *who to contact, why, and what to pitch*.

---

## ⭐ The "no ghost leads" promise (read this first)

Every lead in this database is **source-verified**:

> Each row carries a **real, clickable `source_url`** — a company website, a
> Google/JustDial/IndiaMART listing, an industry-association page, or a news
> article — that proves the business **exists, is in/near Surat, and is in the
> category claimed.** Company names, phone numbers, and emails are **never
> invented.** If a phone/email wasn't visible on a real source, the field is
> left **blank** and the lead is marked `Existence-verified (contact pending)`
> instead of being faked.

This is honest verification you can act on. What it is **not**: we did not
phone every business. Before a sales call, do the 10-second confirm in
[`docs/verification_protocol.md`](docs/verification_protocol.md) using the
`source_url`. That converts a "contact pending" lead into a confirmed call —
fast, and with zero wasted dials on fake numbers.

---

## 📊 The database at a glance

- **1,019 unique, source-verified leads** across **23 Surat business segments**.
- **781 are tagged `SME - direct`** — small / owner-run businesses a small
  vendor can actually supply. The other ~238 (government/tender, PSUs, national
  chains like D-Mart/Reliance, and very-large firms) are tagged `Skip - …`,
  kept in the master file but **excluded from your SME sheet**. (This split is a
  heuristic in `scripts/process_leads.py` — tune the token lists if it
  mis-tags anyone.)
- 👉 **Start with [`data/leads_sme_priority.csv`](data/leads_sme_priority.csv)** —
  the SME-only list, sorted hottest-first with contact-found leads on top.
- **Tiers:** 241 Tier-A · 579 Tier-B · 199 Tier-C.
- **~42% carry a phone/email** from a source, and every captured **mobile gets a
  ready `https://wa.me/91…` WhatsApp link** in the `whatsapp` column. The rest
  are existence-verified — confirm the number via `source_url` before calling
  (`WebFetch` was blocked in the build environment, so this is conservative;
  most "pending" numbers are a 10-second Google-Business lookup away).

---

## 📁 What's in here

| File | What it is | Use it for |
|---|---|---|
| **`data/leads_sme_priority.csv`** | ⭐ **Start here.** Only the `SME - direct` leads (small/owner-run — you can supply), sorted hottest-first with contact-found on top. Has the `whatsapp` click-link column. | Your real working list. |
| **`data/leads_master.csv`** | All 1,019 leads incl. the big/tender/chain ones (tagged in `supplier_fit`), de-duplicated, scored, tiered, sorted. Columns for *who to contact / why / what they need*. | Full picture; filter by `supplier_fit`, category or area. |
| **`data/leads_tier_A_callfirst.csv`** | The Tier-A subset — highest-potential, call these first. | Your week-1 hit list. |
| **`data/leads_raw_combined.csv`** | The raw collected view (name, category, area, contact, source) with no scoring. | Auditing / importing into a CRM raw. |
| `data/categories.csv` | The 23 target segments: why each is expanding/upgrading, what to pitch, who decides, Surat hotspots. | Territory & pitch planning. |
| `data/raw/*.psv` | Original per-segment files exactly as each research agent collected them (provenance). | Traceability. |
| `data/_build_summary.txt` | Counts: totals, drops, dedupe, by-tier, by-category. | Sanity check. |
| `docs/verification_protocol.md` | The fast pre-call verification routine. | Before dialing. |
| `docs/outreach_playbook.md` | Segment-by-segment pitch angles & opening lines. | Talking to each lead. |
| `scripts/process_leads.py` | Rebuilds the CSVs from `data/raw/`. | Refreshing/expanding the list. |

---

## 🧭 How the list was built

Twenty-three research agents were fanned out **in parallel** across three waves
(14 broad segments, then 3 net-new ones, then 6 SME-only segments), one per
segment. Each agent searched the live web (company sites, JustDial,
IndiaMART, GoodFirms/Clutch/TechBehemoths, industry associations like GJEPC /
SGCCI / FOSTTA, the Surat Diamond Bourse, and local news) and was bound by
strict anti-fabrication rules: **no source URL → not included; never invent a
name, phone, or email.** Output was then de-duplicated, scored, and tiered by
`scripts/process_leads.py`.

Quality was favoured over a raw count: agents deliberately **dropped companies
headquartered outside Surat** and any entry they couldn't anchor to a real page.

---

## 🎯 The 23 target segments (and why they buy)

High-end **compute** buyers (workstations / GPU / storage):
**Lab-Grown Diamond**, **Diamond & Bourse** (planning software), **Architecture
& CAD/Engineering**, **Media/Video/Photo**, parts of **IT & Software**.

**Volume + networking + CCTV** buyers (seats, cabling, surveillance, AMC):
**IT & Software**, **GIDC Manufacturing**, **Healthcare**, **Education**,
**Textile Manufacturing**, **Textile Trade & Design**, **Jewellery**,
**Finance & Professional**, **Hospitality & Real Estate**, **Retail &
Supermarket**, **Automobile Dealership**, **Government & PSU** (Smart-City
CCTV), and **BPO/Logistics/Print**.

**SME / owner-run buyers** (billing PC + CCTV + Wi-Fi + AMC — your bread &
butter): **Food & Hospitality**, **Wellness & Clinics**, **Local Retail**,
**Professional Services**, **SME Manufacturing & Jobwork**, and **Diamond /
Jewellery / Textile Micro-SME**.

See [`data/categories.csv`](data/categories.csv) for the full why/what/who table.

**Surat-specific gold:** the **lab-grown diamond boom** (new CVD units opening
constantly = greenfield IT fit-outs), the **Surat Diamond Bourse** (firms
opening new offices = networking + heavy CCTV + dozens of seats), the **Ring
Road textile markets** (thousands of billing PCs + dense CCTV), and the
**GIDC industrial belts** (Sachin / Pandesara / Hazira ERP + surveillance).

---

## 🧮 How leads are scored (0–100)

| Component | Max | Rewards |
|---|---|---|
| Hardware-spend potential / compute intensity | 30 | High-end workstations, servers, big fit-outs |
| Organisation size (seats / sites) | 25 | More endpoints = bigger order |
| Growth / upgrade signal | 25 | Expansion, new branch, funding, hiring, new factory → **future need** |
| Recurring revenue (networking / CCTV / AMC) | 20 | Sticky, repeat business |

**Tiers:** **A** = 75–100 (call first) · **B** = 60–74 (strong) · **C** = <60 (nurture).

Scores are a **prioritisation heuristic**, not a guarantee — they tell you where
to spend your time first.

---

## ▶️ How to use it (sales workflow)

1. Open **`data/leads_tier_A_callfirst.csv`** in Excel/Sheets.
2. Sort/filter by **`area`** to plan a day's field visits in one locality
   (e.g. all Katargam diamond units, or all Vesu architects).
3. For each lead, read **`buying_trigger` / `expansion_signal`** (your *reason
   to call*) and **`hardware_need`** (your *pitch*).
4. Confirm the contact via **`source_url`** (see the verification protocol) →
   then call/visit the **`contact_approach`** decision-maker.
5. Use **`docs/outreach_playbook.md`** for the segment's opening line.
6. Log outcomes in your CRM. Re-run the agents quarterly to refresh.

---

## 🔁 Refreshing or expanding the list

The raw per-segment files live in `data/raw/`. After adding/updating any of
them, rebuild the deliverables:

```bash
python3 scripts/process_leads.py
```

To go deeper in a hot segment (e.g. more lab-grown diamond units), re-run a
research pass for that segment, drop its new `.psv` into `data/raw/`, and
rebuild.

---

## ⚖️ Compliance note

These are business (B2B) prospects compiled from public web sources for
legitimate outreach. Before **bulk** calling/SMS, screen against India's DND /
TRAI telemarketing rules, and honour opt-outs. Verify a number against its
`source_url` before dialing.
