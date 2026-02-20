# Pregnancy Planner

A week-by-week pregnancy planner PDF, designed for use in GoodNotes and similar iPad annotation apps.

## What it is

A calm, minimal pregnancy planning PDF covering Weeks 4–40. Designed to reduce mental load and give a sense of structure without overwhelm.

**Each weekly page includes:**
- 3 pre-suggested tasks for the week
- 3 blank checkboxes to add your own
- Habit tracker (Mon–Sun, free-entry)
- "How are you feeling?" journalling lines
- Notes section (fills remaining page space)

**Also includes:**
- Cover page + About page
- First, Second, and Third Trimester preambles
- 4 Appointment tracker pages
- Hospital bag checklist
- Baby essentials checklist
- Admin & work checklist
- 4 blank notes pages

## How to generate

```bash
pip install reportlab
python3 generate_planner.py
```

Output: `pregnancy_planner_2026.pdf`

## Design

- Style: Clean & Minimal × Neutral & Earthy
- Palette: sage green, warm clay, oat white
- Page size: iPad portrait (210 × 280mm, 3:4 ratio)
- Font: Helvetica

## Roadmap

- [ ] Android app
- [ ] Web app
- [ ] Custom due date input (auto-calculates current week)
- [ ] Partner access / shared lists
