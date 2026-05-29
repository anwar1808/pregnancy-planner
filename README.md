# The Pregnancy Planner

A week-by-week pregnancy planner PDF, designed for use in GoodNotes and similar iPad annotation apps.

> "A place to plan and prepare, week-by-week."

## What it is

A calm, hyperlinked pregnancy planning PDF covering Weeks 4–40. 88 pages. Designed to reduce mental load and give a sense of structure without overwhelm.

### Versions

| Version | Generator | Output |
|---|---|---|
| v1 | `generate_planner_v1.py` | `pregnancy_planner_2026_v1.pdf` |
| v2 | `generate_planner.py` | `pregnancy_planner_2026_v2.pdf` |
| v3 | `generate_planner_v3.py` | `pregnancy_planner_2026_v3.pdf` |
| v4 (current) | `generate_planner_v4.py` | `pregnancy_planner_2026_v4.pdf` |

### What changed in v4 (review notes on v3)

- Removed the horizontal icon nav strip (side tabs kept).
- Reference-inspired refresh: letter-spaced serif display titles, muted
  sage / navy / rose accents, and a single delicate botanical sprig
  replacing every old decorative graphic (cover + all title pages).
- Weekly pages: title is now "Weekly Planner"; the seven days stretch the
  full page height (no "Daily Planner" header); larger section titles
  close to their blocks; portrait "Progress Photo" box; the to-do column
  carries Actions + Research + Consider from the Excel.
- Bullets aligned to text throughout; appointment "Questions to ask" is
  bulleted; scan photo boxes are square; hospital-bag and baby-essentials
  pages fill the sheet; signs-of-labour uses bullets, not checkboxes.
- Removed the two "questions" checklist pages (now 86 pages).
- Birth plan: subtitle "Vaginal or C-Section"; Environment is free-write;
  "ice chips" removed; free lines after every section; C-section spaced.

## What's in v3

**Navigation**
- 9 full-height side tabs, full names (1st Trimester, 2nd Trimester, 3rd Trimester, Appointments, Checklists, Birth Plan, Journal, Notes)
- Top icon nav strip on every content page — one tap to any major section
- Inline hyperlinks: tap "dating scan", "hospital bag", "birth preferences", "postpartum" etc. in any weekly to-do to jump to the relevant page
- Colour-coded trimesters: sage (T1), warm clay (T2), dusty terracotta (T3)

**Weekly pages (Weeks 4–40)**
- Daily Planner spreading the full page height on the left
- Action-only to-do list (UK NHS-anchored, sourced from `pregnancy_planner_reference_lists.xlsx`)
- Weekly bump photo placeholder
- Habits tracker (Mon–Sun)
- Notes section filling remaining space

**Trimester section** (each)
- Title page with big trimester name + week range + decorative motif
- Monthly overview — clean 7-column grid, no separate boxes per day
- Preamble page with Priorities (3 bullets) and Habits to Build

**Appointments**
- Booking appointment (8–12 weeks)
- Dating scan (11–14 weeks) — includes estimated due date and photo box
- Anatomy scan (18–21 weeks) — photo box
- Additional scan template (duplicate as needed)
- Midwife appointments at 25, 28, 31, 34, 36, 38, 40, 41, 42 weeks (with first-time-mum flags where appropriate)
- Midwife appointment template
- Next steps as bulleted list on every appointment page

**Checklists**
- Hospital bag (you / baby / partner / post-birth)
- Baby essentials (sleeping, feeding, clothing, bathing, changing, out and about)
- Admin & work (during pregnancy + after birth)
- Postpartum care (recovery, breastfeeding, rest, C-section recovery)
- Signs of labour (early signs / active labour / when to call in)
- Questions for your midwife (per trimester)
- Questions at scan appointments (dating, anatomy, general)

**Birth Plan**
- Vaginal birth plan — overview, in-labour preferences, pain relief, monitoring, second stage
- Post-delivery preferences — cord clamping, skin-to-skin, placenta, feeding, vitamin K, NICU
- C-section-specific birth plan — in theatre, as baby is born, recovery

**Closing**
- A note acknowledging the transformation

## How to generate

```bash
pip install reportlab openpyxl pypdf
python3 generate_planner_v3.py
```

Output: `pregnancy_planner_2026_v3.pdf`

## Design

- Style: Clean & Minimal × Neutral & Earthy
- Palette: sage green, warm clay, dusty terracotta, oat
- Page size: iPad portrait (210 × 280 mm, 3:4 ratio)
- Font: Helvetica

## Source data

`pregnancy_planner_reference_lists.xlsx` holds the source data for the weekly tasks, hospital bag, baby essentials, and work & admin checklists. Edit the sheet and re-run to update.

## Roadmap

- [ ] Android app
- [ ] Web app
- [ ] Custom due date input (auto-calculates current week)
- [ ] Partner access / shared lists
