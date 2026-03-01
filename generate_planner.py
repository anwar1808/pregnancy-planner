"""
Pregnancy Planner PDF Generator
Output: /Users/annie/pregnancy_planner_2026.pdf
"""

from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor, white

# ── Page dimensions ───────────────────────────────────────────────────────────
PAGE_W = 595   # 210mm
PAGE_H = 794   # 280mm

# ── Colour palette ────────────────────────────────────────────────────────────
SAGE         = HexColor("#7a9e7e")
CLAY         = HexColor("#c4956a")
TEXT_DARK    = HexColor("#4a3f35")
TEXT_SEC     = HexColor("#a09080")
LINE_MED     = HexColor("#e8e0d4")
LINE_LIGHT   = HexColor("#f0ebe2")
FREE_LINE    = HexColor("#ddd5c5")
HABIT_BORDER = HexColor("#c8b89a")
DAY_COLOR    = HexColor("#b8a898")
TRIM_WHITE   = HexColor("#d8d8d8")   # muted white for trimester sublabel

# ── Layout constants ──────────────────────────────────────────────────────────
MARGIN_X  = 20 * mm          # left/right body margin
CONTENT_W = PAGE_W - 2 * MARGIN_X - 22   # reduced by 22pt for side tabs

BAND_H          = 30          # sage header band height (pt)
BAND_FONT       = 12          # "Week 18" font size
BAND_SUB_FONT   = 9           # trimester sublabel font size

SEC_FONT        = 8           # section label font size
SEC_GAP_AFTER   = 14          # space between section label and first item
SECTION_GAP     = 20          # space between sections

TASK_FONT       = 10          # task text font size
TASK_ROW_H      = 18          # height of each task row
CB_SIZE         = 9           # checkbox square side length

HABIT_NAME_W    = 85          # width of habit name underline
HABIT_CIRCLE_R  = 5           # habit circle radius
HABIT_ROW_H     = 24          # height of each habit row
DAY_FONT        = 7           # M T W T F S S font size
DAY_ROW_H       = 16          # height of day-letters row

NOTE_SPACING    = 16          # distance between note lines
BOTTOM_MARGIN   = 22          # pt from page bottom

BODY_START      = BAND_H + 22  # pt from page top where body begins

# ── Side nav tab definitions ──────────────────────────────────────────────────
TABS = [
    (0, "START",       "dest_start"),
    (1, "TRIM 1",      "dest_trim1"),
    (2, "TRIM 2",      "dest_trim2"),
    (3, "TRIM 3",      "dest_trim3"),
    (4, "APPTS",       "dest_appts"),
    (5, "CHECKLISTS",  "dest_checklists"),
    (6, "HEALTH",      "dest_health"),
    (7, "JOURNAL",     "dest_journal"),
    (8, "NOTES",       "dest_notes"),
]

TAB_W    = 18    # tab width (pt)
TAB_H    = 60    # tab height (pt)
TAB_GAP  = 2     # gap between tabs (pt)
TAB_X    = PAGE_W - TAB_W   # left edge of tab strip

# total height of all 9 tabs + gaps
_TAB_TOTAL_H = 9 * TAB_H + 8 * TAB_GAP
_TAB_START_Y = (PAGE_H - _TAB_TOTAL_H) / 2   # bottom-relative y of the lowest tab bottom


# ── Coordinate helper ─────────────────────────────────────────────────────────
def rl(top_y):
    """Convert top-relative y to ReportLab bottom-relative y."""
    return PAGE_H - top_y


# ─────────────────────────────────────────────────────────────────────────────
# SIDE NAV TABS
# ─────────────────────────────────────────────────────────────────────────────

def draw_side_tabs(c, active_idx):
    """Draw 9 side navigation tabs on the right edge of the page."""
    inactive_fill = HexColor("#ece6de")

    for i, (tab_idx, label, dest_name) in enumerate(TABS):
        # tabs are drawn top-to-bottom, so index 0 is at the top
        # bottom-relative y of this tab's bottom edge
        tab_bottom = _TAB_START_Y + (8 - i) * (TAB_H + TAB_GAP)
        tab_top    = tab_bottom + TAB_H

        if tab_idx == active_idx:
            fill_color = SAGE
            text_color = white
        else:
            fill_color = inactive_fill
            text_color = TEXT_SEC

        c.setFillColor(fill_color)
        c.setStrokeColor(fill_color)
        c.setLineWidth(0)
        c.rect(TAB_X, tab_bottom, TAB_W, TAB_H, fill=1, stroke=0)

        # Rotated text centred in the tab
        c.saveState()
        cx = TAB_X + TAB_W / 2
        cy = tab_bottom + TAB_H / 2
        c.translate(cx, cy)
        c.rotate(90)
        c.setFont("Helvetica", 6)
        c.setFillColor(text_color)
        c.drawCentredString(0, -2, label)
        c.restoreState()

        # Clickable link rectangle
        c.linkRect(
            '',
            dest_name,
            (TAB_X, tab_bottom, TAB_X + TAB_W, tab_top),
            relative=0,
            Border=[0, 0, 0],
        )


# ─────────────────────────────────────────────────────────────────────────────
# PRIMITIVES
# ─────────────────────────────────────────────────────────────────────────────

def draw_sage_band(c, label, sublabel=""):
    c.setFillColor(SAGE)
    c.rect(0, PAGE_H - BAND_H, PAGE_W, BAND_H, fill=1, stroke=0)

    # Week label
    c.setFillColor(white)
    c.setFont("Helvetica", BAND_FONT)
    c.drawString(MARGIN_X, PAGE_H - BAND_H + (BAND_H - BAND_FONT) / 2, label)

    if sublabel:
        label_w = c.stringWidth(label, "Helvetica", BAND_FONT)
        sep_x = MARGIN_X + label_w + 10

        # Separator line
        c.setStrokeColor(white)
        c.setLineWidth(0.5)
        mid = PAGE_H - BAND_H / 2
        c.line(sep_x, mid - 6, sep_x, mid + 6)

        # Sublabel
        c.setFillColor(TRIM_WHITE)
        c.setFont("Helvetica", BAND_SUB_FONT)
        c.drawString(sep_x + 8, PAGE_H - BAND_H + (BAND_H - BAND_SUB_FONT) / 2, sublabel.upper())


def draw_section_header(c, label, top_y, margin_x=None, content_w=None):
    """Draw 'LABEL ────' header. Returns top_y of first item below."""
    if margin_x is None: margin_x = MARGIN_X
    if content_w is None: content_w = CONTENT_W

    base = rl(top_y) + 2
    c.setFont("Helvetica", SEC_FONT)
    c.setFillColor(TEXT_SEC)
    c.drawString(margin_x, base, label)

    label_w = c.stringWidth(label, "Helvetica", SEC_FONT)
    rule_x = margin_x + label_w + 7
    c.setStrokeColor(LINE_MED)
    c.setLineWidth(0.5)
    c.line(rule_x, base + 3, margin_x + content_w, base + 3)

    return top_y + SEC_FONT + SEC_GAP_AFTER


def draw_checkbox(c, x, top_y, prefilled=True):
    """Draw a single checkbox at position."""
    color  = CLAY if prefilled else HexColor("#ccc0b0")
    weight = 1.2 if prefilled else 0.8
    c.setStrokeColor(color)
    c.setFillColor(white)
    c.setLineWidth(weight)
    c.roundRect(x, rl(top_y + CB_SIZE), CB_SIZE, CB_SIZE, 2, fill=1, stroke=1)


def draw_task_row(c, top_y, text=None, prefilled=True, margin_x=None, content_w=None):
    """Draw one task row. Returns top_y of next row."""
    if margin_x is None: margin_x = MARGIN_X
    if content_w is None: content_w = CONTENT_W

    draw_checkbox(c, margin_x, top_y, prefilled=prefilled)
    text_x = margin_x + CB_SIZE + 7

    if text and prefilled:
        c.setFont("Helvetica", TASK_FONT)
        c.setFillColor(TEXT_DARK)
        # Vertically centre text within CB_SIZE
        c.drawString(text_x, rl(top_y + CB_SIZE) + (CB_SIZE - TASK_FONT) / 2 + 1, text)
    else:
        # Free-form underline
        line_y = rl(top_y + CB_SIZE / 2)
        c.setStrokeColor(FREE_LINE)
        c.setLineWidth(0.5)
        c.line(text_x, line_y, margin_x + content_w, line_y)

    return top_y + TASK_ROW_H


def draw_note_lines(c, count, top_y, spacing=None, margin_x=None, content_w=None, color=None):
    """Draw `count` note lines. Returns top_y after last line."""
    if spacing   is None: spacing   = NOTE_SPACING
    if margin_x  is None: margin_x  = MARGIN_X
    if content_w is None: content_w = CONTENT_W
    if color     is None: color     = LINE_LIGHT

    c.setStrokeColor(color)
    c.setLineWidth(0.4)
    for i in range(count):
        ly = rl(top_y + spacing * (i + 1))
        c.line(margin_x, ly, margin_x + content_w, ly)
    return top_y + spacing * count + 4


def draw_habit_tracker(c, top_y, margin_x=None, content_w=None, rows=4):
    """Draw day-letter header + `rows` habit rows. Returns bottom top_y."""
    if margin_x  is None: margin_x  = MARGIN_X
    if content_w is None: content_w = CONTENT_W

    circles_start = margin_x + HABIT_NAME_W + 6
    circle_zone_w = margin_x + content_w - circles_start
    col_w = circle_zone_w / 7

    days = ["M", "T", "W", "T", "F", "S", "S"]

    # Day letters row
    c.setFont("Helvetica", DAY_FONT)
    c.setFillColor(DAY_COLOR)
    for i, d in enumerate(days):
        cx = circles_start + i * col_w + col_w / 2
        c.drawCentredString(cx, rl(top_y + DAY_FONT), d)

    top_y += DAY_ROW_H

    for _ in range(rows):
        row_base = rl(top_y + HABIT_CIRCLE_R + 2)

        # Name underline
        c.setStrokeColor(FREE_LINE)
        c.setLineWidth(0.5)
        c.line(margin_x, row_base, margin_x + HABIT_NAME_W, row_base)

        # 7 circles
        c.setStrokeColor(HABIT_BORDER)
        c.setFillColor(white)
        c.setLineWidth(0.8)
        for i in range(7):
            cx = circles_start + i * col_w + col_w / 2
            c.circle(cx, row_base, HABIT_CIRCLE_R, fill=1, stroke=1)

        top_y += HABIT_ROW_H

    return top_y


def draw_wrapped(c, text, x, top_y, max_w, font="Helvetica", size=10, leading=15, color=TEXT_DARK):
    """Word-wrap text block. Returns next top_y."""
    c.setFont(font, size)
    c.setFillColor(color)
    words = text.split()
    line, ty = "", top_y
    for word in words:
        test = (line + " " + word).strip()
        if c.stringWidth(test, font, size) <= max_w:
            line = test
        else:
            c.drawString(x, rl(ty), line)
            ty += leading
            line = word
    if line:
        c.drawString(x, rl(ty), line)
        ty += leading
    return ty


# ─────────────────────────────────────────────────────────────────────────────
# TRIMESTER HELPER
# ─────────────────────────────────────────────────────────────────────────────

def get_trimester(week):
    if week <= 12:  return "First Trimester"
    if week <= 26:  return "Second Trimester"
    return "Third Trimester"


# ─────────────────────────────────────────────────────────────────────────────
# COVER PAGE
# ─────────────────────────────────────────────────────────────────────────────

def draw_cover(c):
    # Full-page sage green background
    c.setFillColor(SAGE)
    c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)

    # Decorative thin horizontal line above title
    title_y_rl = PAGE_H / 2 + 20   # bottom-relative y of title baseline
    c.setStrokeColor(white)
    c.setLineWidth(0.6)
    c.line(80, title_y_rl + 50, PAGE_W - 80, title_y_rl + 50)

    # White centred title
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 30)
    c.drawCentredString(PAGE_W / 2, title_y_rl, "PREGNANCY PLANNER")

    # Subtitle
    c.setFillColor(TRIM_WHITE)
    c.setFont("Helvetica", 12)
    c.drawCentredString(PAGE_W / 2, title_y_rl - 24, "Your week-by-week guide to feeling prepared")

    # Decorative thin horizontal line below subtitle
    c.setStrokeColor(white)
    c.setLineWidth(0.6)
    c.line(80, title_y_rl - 44, PAGE_W - 80, title_y_rl - 44)

    # Bottom: "WEEKS 4 – 40" small text
    c.setFillColor(white)
    c.setFont("Helvetica", 9)
    c.drawCentredString(PAGE_W / 2, BOTTOM_MARGIN + 10, "WEEKS 4 – 40")

    # No side tabs on the cover (no active section yet)
    draw_side_tabs(c, 0)


# ─────────────────────────────────────────────────────────────────────────────
# CONTENTS PAGE
# ─────────────────────────────────────────────────────────────────────────────

def draw_contents_page(c):
    c.setFillColor(white)
    c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
    draw_sage_band(c, label="Contents")
    draw_side_tabs(c, 0)

    mx = MARGIN_X
    cw = CONTENT_W
    cur_y = BODY_START + 10

    def dot_leader_row(label, indent=0, size=10, bold=False):
        nonlocal cur_y
        font = "Helvetica-Bold" if bold else "Helvetica"
        c.setFont(font, size)
        c.setFillColor(TEXT_DARK if bold else TEXT_DARK)
        c.drawString(mx + indent, rl(cur_y), label)
        # dot leader
        label_w = c.stringWidth(label, font, size)
        dot_x = mx + indent + label_w + 4
        right_x = mx + cw - 2
        c.setFillColor(TEXT_SEC)
        c.setFont("Helvetica", 8)
        x = dot_x
        while x < right_x - 6:
            c.drawString(x, rl(cur_y) + 1, ".")
            x += 6
        cur_y += size + 8

    def sub_row(label, indent=16):
        nonlocal cur_y
        c.setFont("Helvetica", 9)
        c.setFillColor(TEXT_SEC)
        c.drawString(mx + indent, rl(cur_y), label)
        label_w = c.stringWidth(label, "Helvetica", 9)
        dot_x = mx + indent + label_w + 4
        right_x = mx + cw - 2
        x = dot_x
        while x < right_x - 6:
            c.drawString(x, rl(cur_y) + 1, ".")
            x += 6
        cur_y += 9 + 6

    sections = [
        ("Getting Started", False, []),
        ("What Your Planner Includes", False, []),
        ("Planning", False, ["Trimester Planning", "Week-by-Week Pages"]),
        ("Habit Tracking", False, []),
        ("Appointment Logs", False, []),
        ("Checklists", False, ["Baby Preparation", "Home Preparation", "Hospital Bag", "Postpartum Prep"]),
        ("Journal", False, []),
        ("Notes", False, []),
    ]

    for (label, bold, subs) in sections:
        dot_leader_row(label, bold=True)
        for sub in subs:
            sub_row(sub)
        cur_y += 4


# ─────────────────────────────────────────────────────────────────────────────
# ABOUT PAGE
# ─────────────────────────────────────────────────────────────────────────────

def draw_about_page(c):
    c.setFillColor(white)
    c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)

    draw_sage_band(c, label="About This Planner")
    draw_side_tabs(c, 0)

    mx = MARGIN_X
    cw = CONTENT_W
    cur_y = BODY_START

    # Main title
    c.setFont("Helvetica-Bold", 15)
    c.setFillColor(TEXT_DARK)
    c.drawString(mx, rl(cur_y), "A calm place for everything.")
    cur_y += 28

    paragraphs = [
        "This planner is designed to hold everything pregnancy brings — the appointments, the tasks, "
        "the thoughts, the questions. Not all at once. Just one week at a time.",

        "Each weekly page gives you a gentle structure: a handful of suggested tasks to get you started, "
        "space to add your own, a habit tracker for the small daily things, and room to write how you're feeling.",

        "There's no pressure to fill everything in. Use what helps. Leave what doesn't. This is your planner.",
    ]

    for para in paragraphs:
        cur_y = draw_wrapped(c, para, mx, cur_y, cw, font="Helvetica", size=10, leading=16)
        cur_y += 10

    # Rule
    c.setStrokeColor(LINE_MED)
    c.setLineWidth(0.5)
    c.line(mx, rl(cur_y), mx + cw, rl(cur_y))
    cur_y += 20

    cur_y = draw_section_header(c, "HOW TO USE IT", cur_y, mx, cw)

    bullets = [
        "Weekly pages run from Week 4 to Week 40.",
        "Suggested tasks are pre-printed — tick them off or ignore them.",
        "Blank checkboxes at the bottom of each section are yours to fill in.",
        "The habit tracker runs Mon–Sun. Write your habit on the line, fill circles as you go.",
        "Appointments, checklists, and notes pages are at the back.",
    ]

    for bullet in bullets:
        dot_y = rl(cur_y + 4)
        c.setFillColor(CLAY)
        c.circle(mx + 4, dot_y, 2.5, fill=1, stroke=0)
        cur_y = draw_wrapped(c, bullet, mx + 13, cur_y, cw - 13,
                             font="Helvetica", size=10, leading=15)
        cur_y += 4

    # Rule before navigation section
    cur_y += 8
    c.setStrokeColor(LINE_MED)
    c.setLineWidth(0.5)
    c.line(mx, rl(cur_y), mx + cw, rl(cur_y))
    cur_y += 20

    cur_y = draw_section_header(c, "NAVIGATING YOUR PLANNER", cur_y, mx, cw)

    nav_bullets = [
        "Use the tabs on the right edge of each page to jump between sections.",
        "Tap a tab while in Read Only mode (toggle off the pen tool) to follow the link.",
        "To add more pages, duplicate any page: press and hold the page thumbnail, then select Duplicate.",
    ]

    for bullet in nav_bullets:
        dot_y = rl(cur_y + 4)
        c.setFillColor(SAGE)
        c.circle(mx + 4, dot_y, 2.5, fill=1, stroke=0)
        cur_y = draw_wrapped(c, bullet, mx + 13, cur_y, cw - 13,
                             font="Helvetica", size=10, leading=15)
        cur_y += 4


# ─────────────────────────────────────────────────────────────────────────────
# TRIMESTER TITLE PAGE
# ─────────────────────────────────────────────────────────────────────────────

def draw_trimester_title_page(c, trimester_name, week_range, active_tab_idx):
    """Full sage green trimester title page."""
    c.setFillColor(SAGE)
    c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)

    # Trimester name (small, top)
    c.setFillColor(white)
    c.setFont("Helvetica", 11)
    c.drawCentredString(PAGE_W / 2, PAGE_H - 80, trimester_name.upper())

    # Decorative thin line above week range
    mid_y = PAGE_H / 2
    c.setStrokeColor(white)
    c.setLineWidth(0.6)
    c.line(80, mid_y + 55, PAGE_W - 80, mid_y + 55)

    # Week range (large, centred vertically)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 48)
    c.drawCentredString(PAGE_W / 2, mid_y, week_range)

    # Decorative thin line below
    c.setStrokeColor(white)
    c.setLineWidth(0.6)
    c.line(80, mid_y - 30, PAGE_W - 80, mid_y - 30)

    draw_side_tabs(c, active_tab_idx)


# ─────────────────────────────────────────────────────────────────────────────
# TRIMESTER CALENDAR PAGE
# ─────────────────────────────────────────────────────────────────────────────

def draw_trimester_calendar(c, trimester_name, start_week, end_week, active_tab_idx):
    """At-a-glance calendar grid for a trimester."""
    c.setFillColor(white)
    c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
    draw_sage_band(c, label=f"{trimester_name} \u2014 At a Glance")
    draw_side_tabs(c, active_tab_idx)

    mx = MARGIN_X
    cw = CONTENT_W
    cur_y = BODY_START + 6

    num_weeks = end_week - start_week + 1
    week_label_w = 30
    day_area_w = cw - week_label_w
    cell_w = day_area_w / 7

    # Available height for grid (leave room for notes section at bottom)
    notes_area_h = 60
    grid_h = PAGE_H - cur_y - BOTTOM_MARGIN - notes_area_h - 20
    cell_h = grid_h / (num_weeks + 1)   # +1 for header row

    grid_x = mx + week_label_w
    grid_top = cur_y

    days = ["M", "T", "W", "T", "F", "S", "S"]

    # Day headers row
    c.setFont("Helvetica-Bold", 7)
    c.setFillColor(TEXT_SEC)
    for i, d in enumerate(days):
        cx = grid_x + i * cell_w + cell_w / 2
        c.drawCentredString(cx, rl(grid_top + cell_h * 0.65), d)
    grid_top += cell_h

    # Week rows
    for row_idx, wk in enumerate(range(start_week, end_week + 1)):
        row_top = grid_top + row_idx * cell_h

        # Week label
        c.setFont("Helvetica", 7)
        c.setFillColor(TEXT_SEC)
        c.drawString(mx, rl(row_top + cell_h * 0.6), f"Wk {wk}")

        # 7 day cells
        for col in range(7):
            cell_x = grid_x + col * cell_w
            cell_y_rl = rl(row_top + cell_h) + 1
            c.setStrokeColor(HABIT_BORDER)
            c.setFillColor(white)
            c.setLineWidth(0.5)
            c.roundRect(cell_x + 1, cell_y_rl, cell_w - 2, cell_h - 2, 2, fill=1, stroke=1)

    # Small NOTES section at bottom
    notes_top = grid_top + num_weeks * cell_h + 14
    cur_y = draw_section_header(c, "NOTES", notes_top, mx, cw)
    draw_note_lines(c, 4, cur_y, spacing=13, margin_x=mx, content_w=cw)


# ─────────────────────────────────────────────────────────────────────────────
# TRIMESTER PREAMBLE
# ─────────────────────────────────────────────────────────────────────────────

TRIM_HABITS = {
    1: ["e.g. Take folic acid daily", "e.g. Rest when you need to"],
    2: ["e.g. Gentle exercise", "e.g. Track baby movements"],
    3: ["e.g. Practise breathing techniques", "e.g. Prepare freezer meals"],
}


def draw_trimester_preamble(c, trimester_name, week_range, opening, body_text, active_tab_idx, trim_num):
    c.setFillColor(white)
    c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
    draw_side_tabs(c, active_tab_idx)

    # Large sage band
    band_h = 120
    c.setFillColor(SAGE)
    c.rect(0, PAGE_H - band_h, PAGE_W, band_h, fill=1, stroke=0)

    # Trimester label (small, upper)
    c.setFillColor(TRIM_WHITE)
    c.setFont("Helvetica", 10)
    c.drawString(MARGIN_X, PAGE_H - 34, trimester_name.upper())

    # Week range (large)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 30)
    c.drawString(MARGIN_X, PAGE_H - 75, week_range)

    mx  = MARGIN_X
    cw  = CONTENT_W
    cur_y = band_h + 28

    # Opening line (italic)
    c.setFont("Helvetica-Oblique", 12)
    c.setFillColor(TEXT_DARK)
    c.drawString(mx, rl(cur_y), opening)
    cur_y += 28

    # Body paragraphs
    paras = [p.strip() for p in body_text.strip().split("\n\n") if p.strip()]
    for para in paras:
        cur_y = draw_wrapped(c, " ".join(para.split()), mx, cur_y, cw,
                             font="Helvetica", size=10.5, leading=17)
        cur_y += 12

    # ── HABITS TO BUILD THIS TRIMESTER ────────────────────────────────────────
    cur_y += 6
    cur_y = draw_section_header(c, "HABITS TO BUILD THIS TRIMESTER", cur_y, mx, cw)

    suggested = TRIM_HABITS.get(trim_num, [])
    for suggestion in suggested:
        dot_y = rl(cur_y + 4)
        c.setFillColor(SAGE)
        c.circle(mx + 4, dot_y, 2.5, fill=1, stroke=0)
        c.setFont("Helvetica", 10)
        c.setFillColor(TEXT_DARK)
        c.drawString(mx + 13, rl(cur_y), suggestion)
        cur_y += 16

    cur_y += 8
    # 4 free-write habit lines with name underline + circle tracker
    cur_y = draw_habit_tracker(c, cur_y, margin_x=mx, content_w=cw, rows=4)


# ─────────────────────────────────────────────────────────────────────────────
# WEEKLY PAGE — two-column layout
# ─────────────────────────────────────────────────────────────────────────────

def draw_weekly_page(c, week_num, tasks, active_tab_idx):
    c.setFillColor(white)
    c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)

    trimester = get_trimester(week_num)
    draw_sage_band(c, label=f"Week {week_num}", sublabel=trimester)
    draw_side_tabs(c, active_tab_idx)

    # Column layout
    left_col_w  = int(CONTENT_W * 0.45)   # ~207pt
    col_gap     = 12
    right_col_w = CONTENT_W - left_col_w - col_gap
    lx          = MARGIN_X
    rx          = MARGIN_X + left_col_w + col_gap

    body_top = BODY_START
    body_bottom = PAGE_H - BOTTOM_MARGIN
    available_body_h = body_bottom - body_top

    # ── LEFT COLUMN: Daily Planner ─────────────────────────────────────────
    lcur_y = body_top
    lcur_y = draw_section_header(c, "DAILY PLANNER", lcur_y, lx, left_col_w)

    days_labels = ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]
    day_section_h = (available_body_h - (lcur_y - body_top)) / 7

    for day_label in days_labels:
        # Day label
        c.setFont("Helvetica-Bold", 7)
        c.setFillColor(DAY_COLOR)
        c.drawString(lx, rl(lcur_y + 8), day_label)
        lcur_y += 12

        # 3 note lines per day
        lines_per_day = 3
        c.setStrokeColor(LINE_LIGHT)
        c.setLineWidth(0.4)
        for i in range(lines_per_day):
            ly = rl(lcur_y + 14 * (i + 1))
            c.line(lx, ly, lx + left_col_w, ly)
        lcur_y += 14 * lines_per_day + 4

    # ── RIGHT COLUMN ───────────────────────────────────────────────────────
    rcur_y = body_top

    # TO-DO LIST
    rcur_y = draw_section_header(c, "TO-DO LIST", rcur_y, rx, right_col_w)
    for task in tasks:
        rcur_y = draw_task_row(c, rcur_y, text=task, prefilled=True, margin_x=rx, content_w=right_col_w)
    # 7 free checkbox rows
    for _ in range(7):
        rcur_y = draw_task_row(c, rcur_y, prefilled=False, margin_x=rx, content_w=right_col_w)

    # HABITS
    rcur_y += SECTION_GAP - 8
    rcur_y = draw_section_header(c, "HABITS", rcur_y, rx, right_col_w)
    rcur_y = draw_habit_tracker(c, rcur_y, margin_x=rx, content_w=right_col_w, rows=4)

    # HOW ARE YOU FEELING?
    rcur_y += SECTION_GAP - 8
    rcur_y = draw_section_header(c, "HOW ARE YOU FEELING?", rcur_y, rx, right_col_w)
    rcur_y = draw_note_lines(c, 2, rcur_y, margin_x=rx, content_w=right_col_w)

    # NOTES: fill remaining space
    rcur_y += SECTION_GAP - 6
    rcur_y = draw_section_header(c, "NOTES", rcur_y, rx, right_col_w)
    available = PAGE_H - BOTTOM_MARGIN - rl(rcur_y)
    note_count = max(2, int(available / NOTE_SPACING))
    draw_note_lines(c, note_count, rcur_y, margin_x=rx, content_w=right_col_w)


# ─────────────────────────────────────────────────────────────────────────────
# APPOINTMENTS TITLE PAGE
# ─────────────────────────────────────────────────────────────────────────────

def draw_appointments_title_page(c):
    c.setFillColor(SAGE)
    c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)

    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 36)
    c.drawCentredString(PAGE_W / 2, PAGE_H / 2 + 20, "APPOINTMENTS")

    c.setFillColor(TRIM_WHITE)
    c.setFont("Helvetica", 12)
    c.drawCentredString(PAGE_W / 2, PAGE_H / 2 - 10, "Keep track of every appointment")

    # Decorative lines
    c.setStrokeColor(white)
    c.setLineWidth(0.6)
    c.line(80, PAGE_H / 2 + 50, PAGE_W - 80, PAGE_H / 2 + 50)
    c.line(80, PAGE_H / 2 - 30, PAGE_W - 80, PAGE_H / 2 - 30)

    draw_side_tabs(c, 4)
    c.bookmarkPage("dest_appts")


# ─────────────────────────────────────────────────────────────────────────────
# APPOINTMENT FULL PAGE (one appointment per page)
# ─────────────────────────────────────────────────────────────────────────────

def draw_appointment_full_page(c):
    c.setFillColor(white)
    c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
    draw_sage_band(c, label="Appointment")
    draw_side_tabs(c, 4)

    mx = MARGIN_X
    cw = CONTENT_W
    cur_y = BODY_START

    def field_label(label_text, x, y, w):
        c.setFont("Helvetica", SEC_FONT)
        c.setFillColor(TEXT_SEC)
        c.drawString(x, rl(y), label_text)
        # underline
        c.setStrokeColor(FREE_LINE)
        c.setLineWidth(0.5)
        c.line(x, rl(y + 16), x + w - 8, rl(y + 16))

    # DATE (half) | TIME (half)
    half = cw / 2
    field_label("DATE", mx, cur_y, half)
    field_label("TIME", mx + half, cur_y, half)
    cur_y += 26

    # WEEK (third) | TYPE (third) | LOCATION (third)
    third = cw / 3
    field_label("WEEK", mx, cur_y, third)
    field_label("TYPE", mx + third, cur_y, third)
    field_label("LOCATION", mx + 2 * third, cur_y, third)
    cur_y += 26

    # PROVIDER NAME (full width)
    field_label("PROVIDER NAME", mx, cur_y, cw)
    cur_y += 28

    # QUESTIONS TO ASK
    c.setFont("Helvetica", SEC_FONT)
    c.setFillColor(TEXT_SEC)
    c.drawString(mx, rl(cur_y), "QUESTIONS TO ASK")
    cur_y += 12

    for _ in range(4):
        # question line
        c.setStrokeColor(FREE_LINE)
        c.setLineWidth(0.5)
        c.line(mx, rl(cur_y), mx + cw, rl(cur_y))
        cur_y += 14
        # answer line (slightly indented)
        c.setStrokeColor(LINE_LIGHT)
        c.setLineWidth(0.4)
        c.line(mx + 16, rl(cur_y), mx + cw, rl(cur_y))
        cur_y += 16

    cur_y += 6

    # NOTES
    c.setFont("Helvetica", SEC_FONT)
    c.setFillColor(TEXT_SEC)
    c.drawString(mx, rl(cur_y), "NOTES")
    cur_y += 12
    for _ in range(5):
        c.setStrokeColor(LINE_LIGHT)
        c.setLineWidth(0.4)
        c.line(mx, rl(cur_y), mx + cw, rl(cur_y))
        cur_y += 16

    cur_y += 6

    # NEXT STEPS
    c.setFont("Helvetica", SEC_FONT)
    c.setFillColor(TEXT_SEC)
    c.drawString(mx, rl(cur_y), "NEXT STEPS")
    cur_y += 12
    for _ in range(3):
        c.setStrokeColor(FREE_LINE)
        c.setLineWidth(0.5)
        c.line(mx, rl(cur_y), mx + cw, rl(cur_y))
        cur_y += 16


# ─────────────────────────────────────────────────────────────────────────────
# CHECKLIST HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def draw_checklist_item(c, text, top_y, mx, col_w):
    draw_checkbox(c, mx, top_y, prefilled=True)
    tx = mx + CB_SIZE + 6
    words, line, ty = text.split(), "", top_y
    max_w = col_w - CB_SIZE - 6
    for word in words:
        test = (line + " " + word).strip()
        if c.stringWidth(test, "Helvetica", TASK_FONT) <= max_w:
            line = test
        else:
            c.setFont("Helvetica", TASK_FONT)
            c.setFillColor(TEXT_DARK)
            c.drawString(tx, rl(ty + CB_SIZE) + (CB_SIZE - TASK_FONT) / 2 + 1, line)
            ty += TASK_ROW_H
            line = word
    if line:
        c.setFont("Helvetica", TASK_FONT)
        c.setFillColor(TEXT_DARK)
        c.drawString(tx, rl(ty + CB_SIZE) + (CB_SIZE - TASK_FONT) / 2 + 1, line)
        ty += TASK_ROW_H
    return ty


def draw_free_row(c, top_y, mx, col_w):
    draw_checkbox(c, mx, top_y, prefilled=False)
    tx = mx + CB_SIZE + 6
    c.setStrokeColor(FREE_LINE)
    c.setLineWidth(0.5)
    c.line(tx, rl(top_y + CB_SIZE / 2), mx + col_w, rl(top_y + CB_SIZE / 2))
    return top_y + TASK_ROW_H


def draw_col_header(c, label, top_y, mx):
    c.setFont("Helvetica-Bold", SEC_FONT + 1)
    c.setFillColor(TEXT_SEC)
    c.drawString(mx, rl(top_y), label)
    return top_y + 14


# ─────────────────────────────────────────────────────────────────────────────
# CHECKLISTS TITLE PAGE
# ─────────────────────────────────────────────────────────────────────────────

def draw_checklists_title_page(c):
    c.setFillColor(SAGE)
    c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)

    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 36)
    c.drawCentredString(PAGE_W / 2, PAGE_H / 2 + 20, "CHECKLISTS")

    c.setFillColor(TRIM_WHITE)
    c.setFont("Helvetica", 12)
    c.drawCentredString(PAGE_W / 2, PAGE_H / 2 - 10, "Stay organised, one step at a time")

    c.setStrokeColor(white)
    c.setLineWidth(0.6)
    c.line(80, PAGE_H / 2 + 50, PAGE_W - 80, PAGE_H / 2 + 50)
    c.line(80, PAGE_H / 2 - 30, PAGE_W - 80, PAGE_H / 2 - 30)

    draw_side_tabs(c, 5)
    c.bookmarkPage("dest_checklists")


# ─────────────────────────────────────────────────────────────────────────────
# HOSPITAL BAG
# ─────────────────────────────────────────────────────────────────────────────

def draw_hospital_bag(c):
    c.setFillColor(white)
    c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
    draw_sage_band(c, label="Hospital Bag")
    draw_side_tabs(c, 5)

    gap   = 14
    col_w = (CONTENT_W - gap) / 2
    lx    = MARGIN_X
    rx    = MARGIN_X + col_w + gap

    ly = ry = BODY_START

    ly = draw_col_header(c, "FOR YOU", ly, lx)
    for item in [
        "Maternity notes", "Birth plan / preferences", "Nightgown or pyjamas",
        "Dressing gown", "Slippers", "Comfortable underwear (x5)",
        "Maternity pads (x2 packs)", "Nursing bras (x2)", "Breast pads",
        "Toiletries bag", "Lip balm", "Hair ties", "Phone charger",
        "Snacks", "Water bottle", "Pillow from home",
    ]:
        ly = draw_checklist_item(c, item, ly, lx, col_w)
    # 10 free rows
    for _ in range(10):
        ly = draw_free_row(c, ly, lx, col_w)

    ry = draw_col_header(c, "FOR BABY", ry, rx)
    for item in [
        "Sleepsuits (x3)", "Vests (x3)", "Hat (x2)", "Scratch mitts",
        "Socks", "Cardigan", "Going-home outfit", "Nappies (newborn pack)",
        "Cotton wool / wipes", "Muslin cloths (x4)", "Car seat (in car)",
    ]:
        ry = draw_checklist_item(c, item, ry, rx, col_w)
    # 10 free rows
    for _ in range(10):
        ry = draw_free_row(c, ry, rx, col_w)


# ─────────────────────────────────────────────────────────────────────────────
# BABY ESSENTIALS
# ─────────────────────────────────────────────────────────────────────────────

def draw_baby_essentials(c):
    c.setFillColor(white)
    c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
    draw_sage_band(c, label="Baby Essentials")
    draw_side_tabs(c, 5)

    gap   = 14
    col_w = (CONTENT_W - gap) / 2
    lx    = MARGIN_X
    rx    = MARGIN_X + col_w + gap

    ly = ry = BODY_START

    for header, items in [
        ("SLEEPING", ["Cot or Moses basket", "Mattress (firm, flat)", "Fitted sheets (x3)",
                      "Sleeping bags (x2)", "Baby monitor", "Blackout blind"]),
        ("FEEDING",  ["Nursing pillow", "Breast pump (if using)", "Bottles and steriliser",
                      "Bibs (x6)", "Muslin cloths"]),
    ]:
        ly = draw_col_header(c, header, ly, lx)
        for item in items:
            ly = draw_checklist_item(c, item, ly, lx, col_w)
        ly += 6
    for _ in range(3):
        ly = draw_free_row(c, ly, lx, col_w)

    for header, items in [
        ("BATHING",       ["Baby bath or bath seat", "Hooded towels (x2)", "Gentle baby wash",
                           "Nappy cream", "Cotton wool"]),
        ("OUT AND ABOUT", ["Pram / pushchair", "Car seat (essential)", "Changing bag",
                           "Changing mat", "Sling or carrier (optional)"]),
    ]:
        ry = draw_col_header(c, header, ry, rx)
        for item in items:
            ry = draw_checklist_item(c, item, ry, rx, col_w)
        ry += 6
    for _ in range(3):
        ry = draw_free_row(c, ry, rx, col_w)


# ─────────────────────────────────────────────────────────────────────────────
# ADMIN & WORK
# ─────────────────────────────────────────────────────────────────────────────

def draw_admin_work(c):
    c.setFillColor(white)
    c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
    draw_sage_band(c, label="Admin & Work")
    draw_side_tabs(c, 5)

    mx    = MARGIN_X
    cw    = CONTENT_W
    cur_y = BODY_START

    for header, items in [
        ("BEFORE BABY", [
            "Notify employer of pregnancy (by week 25)",
            "Submit MATB1 form to employer",
            "Confirm maternity leave start date",
            "Apply for Maternity Allowance (if self-employed)",
            "Check NHS entitlements — free prescriptions and dental",
            "Register with a GP for baby",
            "Research Child Benefit (apply after birth)",
        ]),
        ("AFTER BIRTH", [
            "Register the birth (within 42 days)",
            "Apply for Child Benefit",
            "Notify HMRC of new child",
            "Update will or insurance if needed",
            "Inform your employer of return date",
            "Apply for childcare vouchers / free hours (15\u201330hrs)",
        ]),
    ]:
        cur_y = draw_col_header(c, header, cur_y, mx)
        for item in items:
            cur_y = draw_checklist_item(c, item, cur_y, mx, cw)
        cur_y += 8

    for _ in range(4):
        cur_y = draw_free_row(c, cur_y, mx, cw)


# ─────────────────────────────────────────────────────────────────────────────
# HEALTH TITLE PAGE + LINED PAGES
# ─────────────────────────────────────────────────────────────────────────────

def draw_health_title_page(c):
    c.setFillColor(SAGE)
    c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)

    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 36)
    c.drawCentredString(PAGE_W / 2, PAGE_H / 2 + 20, "HEALTH & WELLBEING")

    c.setStrokeColor(white)
    c.setLineWidth(0.6)
    c.line(80, PAGE_H / 2 + 55, PAGE_W - 80, PAGE_H / 2 + 55)
    c.line(80, PAGE_H / 2 - 10, PAGE_W - 80, PAGE_H / 2 - 10)

    draw_side_tabs(c, 6)
    c.bookmarkPage("dest_health")


def draw_blank_lined_page(c, band_label, active_tab_idx):
    c.setFillColor(white)
    c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
    draw_sage_band(c, label=band_label)
    draw_side_tabs(c, active_tab_idx)

    top     = BAND_H + 20 * mm
    bottom  = BOTTOM_MARGIN + 20
    spacing = NOTE_SPACING
    count   = int((PAGE_H - top - bottom) / spacing)

    c.setStrokeColor(LINE_LIGHT)
    c.setLineWidth(0.4)
    for i in range(count):
        ly = PAGE_H - top - spacing * (i + 1)
        c.line(MARGIN_X, ly, MARGIN_X + CONTENT_W, ly)


# ─────────────────────────────────────────────────────────────────────────────
# JOURNAL TITLE PAGE
# ─────────────────────────────────────────────────────────────────────────────

def draw_journal_title_page(c):
    c.setFillColor(SAGE)
    c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)

    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 48)
    c.drawCentredString(PAGE_W / 2, PAGE_H / 2 + 20, "JOURNAL")

    c.setStrokeColor(white)
    c.setLineWidth(0.6)
    c.line(80, PAGE_H / 2 + 60, PAGE_W - 80, PAGE_H / 2 + 60)
    c.line(80, PAGE_H / 2 - 10, PAGE_W - 80, PAGE_H / 2 - 10)

    draw_side_tabs(c, 7)
    c.bookmarkPage("dest_journal")


# ─────────────────────────────────────────────────────────────────────────────
# NOTES TITLE PAGE + NOTES PAGES
# ─────────────────────────────────────────────────────────────────────────────

def draw_notes_title_page(c):
    c.setFillColor(SAGE)
    c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)

    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 48)
    c.drawCentredString(PAGE_W / 2, PAGE_H / 2 + 20, "NOTES")

    c.setStrokeColor(white)
    c.setLineWidth(0.6)
    c.line(80, PAGE_H / 2 + 60, PAGE_W - 80, PAGE_H / 2 + 60)
    c.line(80, PAGE_H / 2 - 10, PAGE_W - 80, PAGE_H / 2 - 10)

    draw_side_tabs(c, 8)
    c.bookmarkPage("dest_notes")


def draw_notes_page(c, page_num):
    c.setFillColor(white)
    c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
    draw_sage_band(c, label="Notes")
    draw_side_tabs(c, 8)

    top      = BAND_H + 20 * mm
    bottom   = BOTTOM_MARGIN + 20
    spacing  = NOTE_SPACING
    count    = int((PAGE_H - top - bottom) / spacing)

    c.setStrokeColor(LINE_LIGHT)
    c.setLineWidth(0.4)
    for i in range(count):
        ly = PAGE_H - top - spacing * (i + 1)
        c.line(MARGIN_X, ly, MARGIN_X + CONTENT_W, ly)

    c.setFont("Helvetica", 8)
    c.setFillColor(TEXT_SEC)
    c.drawRightString(MARGIN_X + CONTENT_W, BOTTOM_MARGIN, str(page_num))


# ─────────────────────────────────────────────────────────────────────────────
# WEEKLY TASK DATA
# ─────────────────────────────────────────────────────────────────────────────

WEEKLY_TASKS = {
    4:  ["Take a pregnancy test", "Book a GP appointment", "Start folic acid (400mcg daily)"],
    5:  ["Register with your GP or midwife", "Note your last period date", "Rest — your body is already working hard"],
    6:  ["Book your midwife booking appointment", "Look into pregnancy vitamins", "Tell your partner if you haven't yet"],
    7:  ["Prepare questions for your booking appointment", "Avoid alcohol, raw fish, soft cheeses", "Be gentle with yourself — fatigue is normal"],
    8:  ["Attend booking appointment (if booked)", "Blood tests and health checks this week", "Think about who you want to tell, and when"],
    9:  ["Rest as much as you can", "Research maternity pay and leave entitlements", "Look into antenatal classes for later"],
    10: ["12-week scan coming — book it if not yet done", "Think about who you want at your scan", "Prepare any questions for the sonographer"],
    11: ["Prepare for your 12-week scan", "Note down any symptoms to mention", "It's okay to feel nervous — that's completely normal"],
    12: ["12-week dating scan this week", "Consider telling close family and friends", "Review your scan results with your midwife"],
    13: ["You've made it to the second trimester", "Consider sharing your news more widely", "Book your 20-week anomaly scan"],
    14: ["Research maternity leave options", "Start thinking about pram styles", "Note any questions for your next midwife appointment"],
    15: ["Think about nursery ideas (no pressure)", "Explore antenatal class options", "Start a baby names list if you'd like"],
    16: ["Midwife appointment this week", "You may start feeling movement soon", "Think about your birth preferences — no rush"],
    17: ["Book antenatal classes if not yet done", "Research hospitals or birth centres nearby", "Start a list of baby items you'll need"],
    18: ["Book your anomaly scan (if not yet done)", "Research prams and car seats", "Start thinking about your birth preferences"],
    19: ["Prepare questions for your anomaly scan", "Think about hospital bag basics", "Rest when you can — your body is busy"],
    20: ["20-week anomaly scan this week", "Note scan results and any follow-up needed", "Celebrate — you're halfway there"],
    21: ["Discuss scan results with your midwife", "Start your hospital bag list", "Research baby monitors and essentials"],
    22: ["Think about childcare options", "Research prams — test a few if possible", "Look into your employer's maternity policy"],
    23: ["Antenatal classes may start now", "Think about who will be your birth partner", "Start a postpartum plan — meals, support, rest"],
    24: ["Midwife appointment this week", "Review your budget for baby items", "Think about what you need for the nursery"],
    25: ["Finalise your birth preferences draft", "Check in with your birth partner", "Start researching postpartum support options"],
    26: ["Submit maternity leave paperwork to HR", "Confirm your last working day", "Start thinking about a handover plan at work"],
    27: ["Start gathering items for your hospital bag", "Book a hospital or birth centre tour", "Think about cord blood banking if interested"],
    28: ["Midwife appointment — blood tests this week", "Review your birth preferences document", "Rest — sleep may get harder, prioritise it"],
    29: ["Finalise nursery essentials", "Install or plan for baby's car seat", "Check your hospital bag list"],
    30: ["Start packing your hospital bag", "Confirm your birth partner's availability", "Think about postpartum meals and freezer prep"],
    31: ["Attend antenatal class if ongoing", "Talk through birth preferences with your midwife", "Rest — it's okay to slow down"],
    32: ["Hospital bag: add key items this week", "Pre-register at your hospital or birth centre", "Look into newborn care basics"],
    33: ["Finalise your birth preferences", "Discuss any concerns with your midwife", "Prepare your home for baby's arrival"],
    34: ["Midwife appointment this week", "Hospital bag should be nearly ready", "Prepare a list of people to notify after birth"],
    35: ["Hospital bag: check it's complete", "Know the signs of labour", "Rest and reduce commitments where possible"],
    36: ["Weekly midwife appointments begin", "Install car seat — check it's fitted correctly", "Stock up on postpartum essentials for yourself"],
    37: ["Full term — baby could arrive any time", "Final check on hospital bag", "Inform your birth partner to stay on call"],
    38: ["Weekly midwife appointment", "Rest as much as possible", "Tie up any loose ends at home"],
    39: ["Stay calm — your body knows what to do", "Walk gently if it helps you feel settled", "Know when to call your midwife or hospital"],
    40: ["Due date week — rest, breathe, trust yourself", "Stay in contact with your midwife", "You've done everything you need to do"],
}

FIRST_TRIMESTER_BODY = """
This is the quietest trimester from the outside — and often the most overwhelming on the inside. You may feel exhausted in a way that's hard to explain, or nauseous, or both. That's not weakness. That's your body doing something extraordinary.

This trimester is mostly about rest, and letting things settle. There isn't much you need to do yet, and that's okay. A few gentle things will come your way — a booking appointment, a first scan — and this planner will walk you through them, one at a time.

For now, be kind to yourself. The planning can wait. You can't do this wrong.
"""

SECOND_TRIMESTER_BODY = """
The fog of the first trimester tends to lift, and with it comes a little more space to think, to plan, to even enjoy this. Your bump will start to show. At some point, you'll feel movement — and that moment tends to make everything feel more real.

This is a good time to start thinking ahead, gently. Not all at once — just a little each week. Appointments to book, things to look into, lists to begin. Nothing is urgent. Everything has time.

Use this trimester to get curious, not busy. There's a difference.
"""

THIRD_TRIMESTER_BODY = """
Things might feel heavier now — physically and emotionally. That's real, and it's okay. Your body is preparing for something remarkable, and it's allowed to take up space doing so.

This trimester is about getting ready, not perfect. A bag packed. A few preferences written down. A little more rest wherever you can find it. The to-do list in this planner will feel manageable because it is — it's been designed so nothing sneaks up on you.

You don't need to have everything figured out. You just need to show up. And you already are.
"""


# ─────────────────────────────────────────────────────────────────────────────
# BUILD PDF
# ─────────────────────────────────────────────────────────────────────────────

def build_pdf():
    path = "/Users/annie/pregnancy_planner_2026.pdf"
    c = canvas.Canvas(path, pagesize=(PAGE_W, PAGE_H))

    # ── Cover ──────────────────────────────────────────────────────────────
    c.bookmarkPage("dest_start")
    draw_cover(c)
    c.showPage()

    # ── Contents ───────────────────────────────────────────────────────────
    draw_contents_page(c)
    c.showPage()

    # ── About ──────────────────────────────────────────────────────────────
    draw_about_page(c)
    c.showPage()

    # ── FIRST TRIMESTER ────────────────────────────────────────────────────
    c.bookmarkPage("dest_trim1")
    draw_trimester_title_page(c, "First Trimester", "Weeks 1 \u2013 12", active_tab_idx=1)
    c.showPage()

    draw_trimester_calendar(c, "First Trimester", 1, 12, active_tab_idx=1)
    c.showPage()

    draw_trimester_preamble(
        c, "First Trimester", "Weeks 1 \u2013 12",
        "You might not look different yet, but everything is already changing.",
        FIRST_TRIMESTER_BODY, active_tab_idx=1, trim_num=1
    )
    c.showPage()

    for w in range(4, 13):
        draw_weekly_page(c, w, WEEKLY_TASKS[w], active_tab_idx=1)
        c.showPage()

    # ── SECOND TRIMESTER ───────────────────────────────────────────────────
    c.bookmarkPage("dest_trim2")
    draw_trimester_title_page(c, "Second Trimester", "Weeks 13 \u2013 26", active_tab_idx=2)
    c.showPage()

    draw_trimester_calendar(c, "Second Trimester", 13, 26, active_tab_idx=2)
    c.showPage()

    draw_trimester_preamble(
        c, "Second Trimester", "Weeks 13 \u2013 26",
        "This is where most women find their breath again.",
        SECOND_TRIMESTER_BODY, active_tab_idx=2, trim_num=2
    )
    c.showPage()

    for w in range(13, 27):
        draw_weekly_page(c, w, WEEKLY_TASKS[w], active_tab_idx=2)
        c.showPage()

    # ── THIRD TRIMESTER ────────────────────────────────────────────────────
    c.bookmarkPage("dest_trim3")
    draw_trimester_title_page(c, "Third Trimester", "Weeks 27 \u2013 40", active_tab_idx=3)
    c.showPage()

    draw_trimester_calendar(c, "Third Trimester", 27, 40, active_tab_idx=3)
    c.showPage()

    draw_trimester_preamble(
        c, "Third Trimester", "Weeks 27 \u2013 40",
        "You're in the home stretch — and you're more ready than you feel.",
        THIRD_TRIMESTER_BODY, active_tab_idx=3, trim_num=3
    )
    c.showPage()

    for w in range(27, 41):
        draw_weekly_page(c, w, WEEKLY_TASKS[w], active_tab_idx=3)
        c.showPage()

    # ── APPOINTMENTS ───────────────────────────────────────────────────────
    draw_appointments_title_page(c)
    c.showPage()

    for _ in range(10):
        draw_appointment_full_page(c)
        c.showPage()

    # ── CHECKLISTS ─────────────────────────────────────────────────────────
    draw_checklists_title_page(c)
    c.showPage()

    draw_hospital_bag(c)
    c.showPage()

    draw_baby_essentials(c)
    c.showPage()

    draw_admin_work(c)
    c.showPage()

    # ── HEALTH & WELLBEING ─────────────────────────────────────────────────
    draw_health_title_page(c)
    c.showPage()

    for _ in range(3):
        draw_blank_lined_page(c, "Health & Wellbeing", active_tab_idx=6)
        c.showPage()

    # ── JOURNAL ────────────────────────────────────────────────────────────
    draw_journal_title_page(c)
    c.showPage()

    for _ in range(3):
        draw_blank_lined_page(c, "Journal", active_tab_idx=7)
        c.showPage()

    # ── NOTES ──────────────────────────────────────────────────────────────
    draw_notes_title_page(c)
    c.showPage()

    for i in range(1, 5):
        draw_notes_page(c, i)
        c.showPage()

    c.save()
    print(f"Saved: {path}")


if __name__ == "__main__":
    build_pdf()
