"""
Pregnancy Planner — v3
======================
Major restructure (per Annie, 27 May 2026):

  * 9 full-height side tabs with full names (Start, 1st Trimester, 2nd
    Trimester, 3rd Trimester, Appointments, Checklists, Birth Plan,
    Journal, Notes). No Health tab.
  * Per-trimester colour theming (sage / clay / terracotta).
  * Top icon nav strip on every content page with clickable shortcuts.
  * Cover: 'The Pregnancy Planner' / 'A place to plan and prepare,
    week-by-week.' / background graphic.
  * Trimester title pages: big name, smaller week-range, graphic.
  * Monthly overview: bigger title, grid layout, no week column.
  * Trimester preamble: name + week-range subtitle + Priorities (3) +
    habits to build.
  * Weekly pages: daily planner full-height left col, weekly bump
    photo, action-only to-dos from Excel, hyperlinked scan/list
    mentions.
  * Appointments: booking, dating scan (11–14w), anatomy scan (18–21w),
    additional scan template, midwife appts at 25/28/31/34/36/38/40/41/
    42 plus template, next steps as bullet list.
  * Checklists: hospital bag, baby essentials, work & admin,
    postpartum care, signs of labour, questions for midwife, questions
    for scan.
  * Birth Plan: full vaginal and C-section variants.
  * Closing summary page.
  * Inline hyperlinks for scans, hospital bag, postpartum, birth plan,
    signs of labour.

Output: pregnancy_planner_2026_v3.pdf
"""

import os

from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor, white
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph
from reportlab.lib.enums import TA_LEFT


# ─────────────────────────────────────────────────────────────────────
# PAGE + PALETTE
# ─────────────────────────────────────────────────────────────────────
PAGE_W = 595   # 210 mm
PAGE_H = 794   # 280 mm — iPad-friendly 3:4

# Earthy palette
SAGE         = HexColor("#7a9e7e")   # T1
CLAY         = HexColor("#c4956a")   # T2
TERRACOTTA   = HexColor("#b56e57")   # T3
OAT          = HexColor("#8c7a66")   # neutral sections
SAGE_DEEP    = HexColor("#5f7d63")
CLAY_DEEP    = HexColor("#9e7449")
TERRA_DEEP   = HexColor("#925240")
OAT_DEEP     = HexColor("#6d5f4f")
CREAM        = HexColor("#faf6ef")
TEXT_DARK    = HexColor("#4a3f35")
TEXT_SEC     = HexColor("#a09080")
LINE_MED     = HexColor("#e8e0d4")
LINE_LIGHT   = HexColor("#f0ebe2")
FREE_LINE    = HexColor("#ddd5c5")
HABIT_BORDER = HexColor("#c8b89a")
DAY_COLOR    = HexColor("#b8a898")
TRIM_WHITE   = HexColor("#d8d8d8")
PHOTO_BG     = HexColor("#f7f2e8")
PHOTO_BORDER = HexColor("#d4c8b3")

# ─────────────────────────────────────────────────────────────────────
# LAYOUT
# ─────────────────────────────────────────────────────────────────────
TAB_W            = 24
TAB_GAP          = 3
TAB_X            = PAGE_W - TAB_W

NAV_BAR_H        = 18          # height of icon nav bar under header
BAND_H           = 30          # header band height
BAND_FONT        = 12
BAND_SUB_FONT    = 9

MARGIN_X         = 20 * mm
CONTENT_W        = PAGE_W - 2 * MARGIN_X - TAB_W   # account for wider tabs

SEC_FONT         = 8
SEC_GAP_AFTER    = 14
SECTION_GAP      = 20

TASK_FONT        = 10
TASK_ROW_H       = 18
CB_SIZE          = 9

HABIT_NAME_W     = 85
HABIT_CIRCLE_R   = 5
HABIT_ROW_H      = 24
DAY_FONT         = 7
DAY_ROW_H        = 16

NOTE_SPACING     = 16
BOTTOM_MARGIN    = 22

BODY_START       = BAND_H + NAV_BAR_H + 14   # body starts under band + nav strip


# ─────────────────────────────────────────────────────────────────────
# TAB STRUCTURE — full-height nav
# ─────────────────────────────────────────────────────────────────────
TABS = [
    # (idx, label,           dest_name,        colour)
    (0, "START",            "dest_start",     OAT),
    (1, "1ST TRIMESTER",    "dest_trim1",     SAGE),
    (2, "2ND TRIMESTER",    "dest_trim2",     CLAY),
    (3, "3RD TRIMESTER",    "dest_trim3",     TERRACOTTA),
    (4, "APPOINTMENTS",     "dest_appts",     OAT),
    (5, "CHECKLISTS",       "dest_checklists",OAT),
    (6, "BIRTH PLAN",       "dest_birthplan", OAT),
    (7, "JOURNAL",          "dest_journal",   OAT),
    (8, "NOTES",            "dest_notes",     OAT),
]
N_TABS = len(TABS)

# Each tab fills the full page height proportionally
TAB_TOTAL_H   = PAGE_H - 2 * 6                     # 6pt cap top + bottom
_TAB_H_RAW    = (TAB_TOTAL_H - (N_TABS - 1) * TAB_GAP) / N_TABS
TAB_H         = _TAB_H_RAW
TAB_TOP_START = PAGE_H - 6                          # top edge of first tab


# Icon nav strip — same 9 sections, drawn as small clickable boxes
NAV_ICONS = [
    # (label, dest_name, icon_kind, base_colour)
    ("Start",   "dest_start",     "home",     OAT),
    ("T1",      "dest_trim1",     "leaf",     SAGE),
    ("T2",      "dest_trim2",     "circle",   CLAY),
    ("T3",      "dest_trim3",     "heart",    TERRACOTTA),
    ("Appts",   "dest_appts",     "calendar", OAT),
    ("Lists",   "dest_checklists","check",    OAT),
    ("Birth",   "dest_birthplan", "spark",    OAT),
    ("Journal", "dest_journal",   "pencil",   OAT),
    ("Notes",   "dest_notes",     "lines",    OAT),
]


# ─────────────────────────────────────────────────────────────────────
# COORDINATE HELPER
# ─────────────────────────────────────────────────────────────────────
def rl(top_y):
    """Convert top-relative y → ReportLab bottom-relative y."""
    return PAGE_H - top_y


# ─────────────────────────────────────────────────────────────────────
# SIDE TABS
# ─────────────────────────────────────────────────────────────────────
def draw_side_tabs(c, active_idx):
    """Draw 9 full-height side tabs on the right edge."""
    inactive_fill = HexColor("#ece6de")

    for i, (idx, label, dest, base_color) in enumerate(TABS):
        # Tabs run top → bottom; idx 0 is the topmost
        tab_top    = TAB_TOP_START - i * (TAB_H + TAB_GAP)
        tab_bottom = tab_top - TAB_H

        if idx == active_idx:
            fill_color, text_color = base_color, white
        else:
            fill_color, text_color = inactive_fill, OAT_DEEP

        c.setFillColor(fill_color)
        c.setStrokeColor(fill_color)
        c.setLineWidth(0)
        c.rect(TAB_X, tab_bottom, TAB_W, TAB_H, fill=1, stroke=0)

        # Rotated text — drawn from centre, rotated 90°
        c.saveState()
        cx = TAB_X + TAB_W / 2
        cy = tab_bottom + TAB_H / 2
        c.translate(cx, cy)
        c.rotate(90)
        c.setFont("Helvetica-Bold" if idx == active_idx else "Helvetica", 7)
        c.setFillColor(text_color)
        c.drawCentredString(0, -2.5, label)
        c.restoreState()

        # Clickable link rectangle
        c.linkRect('', dest,
                   (TAB_X, tab_bottom, TAB_X + TAB_W, tab_top),
                   relative=0, Border=[0, 0, 0])


# ─────────────────────────────────────────────────────────────────────
# ICON NAV BAR — under header band on every content page
# ─────────────────────────────────────────────────────────────────────
def _draw_icon(c, kind, cx, cy, color, size=6):
    """Draw a tiny simple icon centred on (cx, cy)."""
    c.setStrokeColor(color)
    c.setFillColor(color)
    c.setLineWidth(0.9)

    if kind == "home":
        # roof + box
        c.line(cx - size, cy, cx, cy + size)
        c.line(cx + size, cy, cx, cy + size)
        c.rect(cx - size + 1, cy - size + 1, 2 * size - 2, size, fill=0, stroke=1)
    elif kind == "leaf":
        # simple leaf — ellipse
        c.ellipse(cx - size + 1, cy - size / 2, cx + size - 1, cy + size / 2, fill=1, stroke=0)
        c.setStrokeColor(white)
        c.setLineWidth(0.5)
        c.line(cx - size + 1, cy, cx + size - 1, cy)
    elif kind == "circle":
        c.circle(cx, cy, size - 1, fill=1, stroke=0)
    elif kind == "heart":
        # two small circles + triangle bottom — approximate heart
        r = size / 2.4
        c.circle(cx - r, cy + r / 2, r, fill=1, stroke=0)
        c.circle(cx + r, cy + r / 2, r, fill=1, stroke=0)
        p = c.beginPath()
        p.moveTo(cx - size + 1, cy + r / 2)
        p.lineTo(cx, cy - size + 1)
        p.lineTo(cx + size - 1, cy + r / 2)
        p.close()
        c.drawPath(p, fill=1, stroke=0)
    elif kind == "calendar":
        c.rect(cx - size, cy - size + 1, 2 * size, 2 * size - 2, fill=0, stroke=1)
        c.line(cx - size, cy + size / 2 - 1, cx + size, cy + size / 2 - 1)
        c.line(cx - size / 2, cy + size, cx - size / 2, cy + size - 2)
        c.line(cx + size / 2, cy + size, cx + size / 2, cy + size - 2)
    elif kind == "check":
        c.rect(cx - size, cy - size + 1, 2 * size, 2 * size - 2, fill=0, stroke=1)
        # tick
        c.setLineWidth(1.2)
        c.line(cx - size / 2, cy, cx - 1, cy - size / 2 + 1)
        c.line(cx - 1, cy - size / 2 + 1, cx + size - 1, cy + size / 2)
    elif kind == "spark":
        # four-point star
        c.line(cx - size, cy, cx + size, cy)
        c.line(cx, cy - size, cx, cy + size)
        c.line(cx - size * 0.6, cy - size * 0.6, cx + size * 0.6, cy + size * 0.6)
        c.line(cx - size * 0.6, cy + size * 0.6, cx + size * 0.6, cy - size * 0.6)
    elif kind == "pencil":
        # diagonal line w/ tip
        c.line(cx - size, cy + size, cx + size - 1, cy - size + 1)
        c.line(cx + size - 1, cy - size + 1, cx + size, cy - size + 3)
    elif kind == "lines":
        c.setLineWidth(0.8)
        c.line(cx - size, cy + size / 2 + 1, cx + size, cy + size / 2 + 1)
        c.line(cx - size, cy,                  cx + size, cy)
        c.line(cx - size, cy - size / 2 - 1,   cx + size, cy - size / 2 - 1)


def draw_icon_nav(c, active_idx, base_color):
    """Horizontal icon nav strip under the header band."""
    strip_top    = PAGE_H - BAND_H
    strip_bottom = strip_top - NAV_BAR_H

    # Strip background — very pale
    c.setFillColor(CREAM)
    c.setStrokeColor(CREAM)
    c.rect(0, strip_bottom, PAGE_W - TAB_W, NAV_BAR_H, fill=1, stroke=0)

    # Slot widths across full strip
    n = len(NAV_ICONS)
    slot_w = (PAGE_W - TAB_W) / n
    cy     = strip_bottom + NAV_BAR_H / 2

    for i, (label, dest, kind, _col) in enumerate(NAV_ICONS):
        slot_left = i * slot_w
        cx = slot_left + slot_w / 2

        if i == active_idx:
            # Highlight active icon — small pill behind
            c.setFillColor(base_color)
            c.setStrokeColor(base_color)
            c.roundRect(cx - 11, cy - 7.5, 22, 15, 4, fill=1, stroke=0)
            icon_col = white
        else:
            icon_col = TEXT_SEC

        _draw_icon(c, kind, cx, cy, icon_col, size=5)

        # Clickable area
        c.linkRect('', dest,
                   (slot_left, strip_bottom, slot_left + slot_w, strip_top),
                   relative=0, Border=[0, 0, 0])

    # Subtle separator line at bottom of strip
    c.setStrokeColor(LINE_MED)
    c.setLineWidth(0.4)
    c.line(0, strip_bottom, PAGE_W - TAB_W, strip_bottom)


# ─────────────────────────────────────────────────────────────────────
# HEADER BAND
# ─────────────────────────────────────────────────────────────────────
def draw_band(c, label, sublabel="", band_color=OAT):
    c.setFillColor(band_color)
    c.rect(0, PAGE_H - BAND_H, PAGE_W, BAND_H, fill=1, stroke=0)

    c.setFillColor(white)
    c.setFont("Helvetica-Bold", BAND_FONT)
    c.drawString(MARGIN_X, PAGE_H - BAND_H + (BAND_H - BAND_FONT) / 2, label)

    if sublabel:
        label_w = c.stringWidth(label, "Helvetica-Bold", BAND_FONT)
        sep_x = MARGIN_X + label_w + 10
        c.setStrokeColor(white)
        c.setLineWidth(0.5)
        mid = PAGE_H - BAND_H / 2
        c.line(sep_x, mid - 6, sep_x, mid + 6)
        c.setFillColor(TRIM_WHITE)
        c.setFont("Helvetica", BAND_SUB_FONT)
        c.drawString(sep_x + 8,
                     PAGE_H - BAND_H + (BAND_H - BAND_SUB_FONT) / 2,
                     sublabel.upper())


def page_frame(c, label, sublabel="", active_idx=0, band_color=OAT):
    """Common content-page frame: white bg, band, nav, side tabs."""
    c.setFillColor(white)
    c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
    draw_band(c, label, sublabel, band_color)
    draw_icon_nav(c, active_idx, band_color)
    draw_side_tabs(c, active_idx)


# ─────────────────────────────────────────────────────────────────────
# PRIMITIVES
# ─────────────────────────────────────────────────────────────────────
def draw_section_header(c, label, top_y, margin_x=None, content_w=None):
    if margin_x is None: margin_x = MARGIN_X
    if content_w is None: content_w = CONTENT_W

    base = rl(top_y) + 2
    c.setFont("Helvetica-Bold", SEC_FONT)
    c.setFillColor(TEXT_SEC)
    c.drawString(margin_x, base, label)

    label_w = c.stringWidth(label, "Helvetica-Bold", SEC_FONT)
    rule_x = margin_x + label_w + 7
    c.setStrokeColor(LINE_MED)
    c.setLineWidth(0.5)
    c.line(rule_x, base + 3, margin_x + content_w, base + 3)

    return top_y + SEC_FONT + SEC_GAP_AFTER


def draw_checkbox(c, x, top_y, accent_color=None):
    color = accent_color or CLAY
    c.setStrokeColor(color)
    c.setFillColor(white)
    c.setLineWidth(1.0)
    c.roundRect(x, rl(top_y + CB_SIZE), CB_SIZE, CB_SIZE, 2, fill=1, stroke=1)


def draw_free_checkbox(c, x, top_y):
    c.setStrokeColor(HexColor("#ccc0b0"))
    c.setFillColor(white)
    c.setLineWidth(0.8)
    c.roundRect(x, rl(top_y + CB_SIZE), CB_SIZE, CB_SIZE, 2, fill=1, stroke=1)


def draw_note_lines(c, count, top_y, spacing=None, margin_x=None,
                    content_w=None, color=None):
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


def draw_wrapped(c, text, x, top_y, max_w, font="Helvetica", size=10,
                 leading=15, color=TEXT_DARK):
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


def draw_habit_tracker(c, top_y, margin_x=None, content_w=None,
                       rows=4, accent=SAGE):
    if margin_x  is None: margin_x  = MARGIN_X
    if content_w is None: content_w = CONTENT_W

    circles_start = margin_x + HABIT_NAME_W + 6
    circle_zone_w = margin_x + content_w - circles_start
    col_w = circle_zone_w / 7

    days = ["M", "T", "W", "T", "F", "S", "S"]
    c.setFont("Helvetica-Bold", DAY_FONT)
    c.setFillColor(DAY_COLOR)
    for i, d in enumerate(days):
        cx = circles_start + i * col_w + col_w / 2
        c.drawCentredString(cx, rl(top_y + DAY_FONT), d)

    top_y += DAY_ROW_H

    for _ in range(rows):
        row_base = rl(top_y + HABIT_CIRCLE_R + 2)
        c.setStrokeColor(FREE_LINE)
        c.setLineWidth(0.5)
        c.line(margin_x, row_base, margin_x + HABIT_NAME_W, row_base)

        c.setStrokeColor(HABIT_BORDER)
        c.setFillColor(white)
        c.setLineWidth(0.8)
        for i in range(7):
            cx = circles_start + i * col_w + col_w / 2
            c.circle(cx, row_base, HABIT_CIRCLE_R, fill=1, stroke=1)

        top_y += HABIT_ROW_H

    return top_y


# ─────────────────────────────────────────────────────────────────────
# HYPERLINK-AWARE TASK ROW
# ─────────────────────────────────────────────────────────────────────
# Keyword → dest map for inline task links
LINK_RULES = [
    # (substring case-insensitive, dest_name, display-style replacement-or-none)
    ("12-week dating scan",       "dest_dating_scan"),
    ("12-week scan",              "dest_dating_scan"),
    ("dating scan",               "dest_dating_scan"),
    ("anomaly scan",              "dest_anatomy_scan"),   # legacy phrase
    ("anatomy scan",              "dest_anatomy_scan"),
    ("20-week scan",              "dest_anatomy_scan"),
    ("birth preferences",         "dest_birth_plan"),
    ("birth plan",                "dest_birth_plan"),
    ("hospital bag",              "dest_hospital_bag"),
    ("postpartum essentials",     "dest_postpartum"),
    ("postpartum",                "dest_postpartum"),
    ("signs of labour",           "dest_signs_of_labour"),
    ("baby items",                "dest_baby_essentials"),
    ("baby's car seat",           "dest_baby_essentials"),
    ("car seat",                  "dest_baby_essentials"),
    ("nursery essentials",        "dest_baby_essentials"),
    ("midwife appointment",       "dest_appts"),
    ("booking appointment",       "dest_booking"),
]


def _apply_links(text):
    """Replace ANOMALY→ANATOMY language; wrap link substrings in inline
    <link> markup for Paragraph rendering."""
    # Language fix: substitute '20-week anomaly' phrasing if any slipped through
    text = text.replace("20-week anomaly", "anatomy")
    text = text.replace("anomaly scan", "anatomy scan")

    # Find earliest matching substring and wrap. Repeat for one match per
    # rule to avoid double-wrapping when one phrase is a substring of
    # another already wrapped.
    used_spans = []   # list of (start, end)

    def _overlaps(a, b):
        for (s, e) in used_spans:
            if not (b <= s or a >= e):
                return True
        return False

    # Sort rules by descending phrase length so longer matches win
    sorted_rules = sorted(LINK_RULES, key=lambda r: -len(r[0]))

    # Build a list of (start, end, dest) markers
    markers = []
    lower = text.lower()
    for phrase, dest in sorted_rules:
        idx = lower.find(phrase)
        while idx != -1:
            end = idx + len(phrase)
            if not _overlaps(idx, end):
                markers.append((idx, end, dest))
                used_spans.append((idx, end))
            idx = lower.find(phrase, end)

    if not markers:
        return text

    markers.sort()
    out = []
    cursor = 0
    for (s, e, dest) in markers:
        out.append(text[cursor:s])
        # Paragraph inline link
        out.append(f'<link href="#{dest}" color="#9e7449"><u>{text[s:e]}</u></link>')
        cursor = e
    out.append(text[cursor:])
    return "".join(out)


_PARA_STYLE = ParagraphStyle(
    "task",
    fontName="Helvetica",
    fontSize=TASK_FONT,
    leading=12.5,
    textColor=TEXT_DARK,
    alignment=TA_LEFT,
    leftIndent=0,
    spaceBefore=0,
    spaceAfter=0,
)


def draw_task_row(c, top_y, text, margin_x=None, content_w=None,
                  accent=CLAY, link=True):
    """Action task row with checkbox + (optionally) linked text."""
    if margin_x is None: margin_x = MARGIN_X
    if content_w is None: content_w = CONTENT_W

    draw_checkbox(c, margin_x, top_y, accent_color=accent)
    text_x = margin_x + CB_SIZE + 7
    text_w = content_w - CB_SIZE - 7

    body = _apply_links(text) if link else text
    para = Paragraph(body, _PARA_STYLE)
    w, h = para.wrap(text_w, 200)
    para.drawOn(c, text_x, rl(top_y + CB_SIZE) + (CB_SIZE - TASK_FONT) / 2 + 1 - (h - TASK_FONT))

    return top_y + max(TASK_ROW_H, h + 4)


def draw_free_row(c, top_y, margin_x=None, content_w=None):
    if margin_x is None: margin_x = MARGIN_X
    if content_w is None: content_w = CONTENT_W

    draw_free_checkbox(c, margin_x, top_y)
    text_x = margin_x + CB_SIZE + 7
    line_y = rl(top_y + CB_SIZE / 2)
    c.setStrokeColor(FREE_LINE)
    c.setLineWidth(0.5)
    c.line(text_x, line_y, margin_x + content_w, line_y)
    return top_y + TASK_ROW_H


# ─────────────────────────────────────────────────────────────────────
# DECORATIVE GRAPHICS
# ─────────────────────────────────────────────────────────────────────
def draw_botanical_motif(c, cx, cy, color=white, scale=1.0):
    """Simple stem-with-leaves decorative motif."""
    s = scale
    c.setStrokeColor(color)
    c.setLineWidth(1.0)
    # Central stem
    c.line(cx, cy - 50 * s, cx, cy + 50 * s)
    # Pairs of leaves
    for offset in (-30, -10, 10, 30):
        y = cy + offset * s
        # leaf left
        c.ellipse(cx - 22 * s, y - 4 * s, cx - 4 * s, y + 4 * s, fill=0, stroke=1)
        # leaf right
        c.ellipse(cx + 4 * s, y - 4 * s, cx + 22 * s, y + 4 * s, fill=0, stroke=1)


def draw_circle_motif(c, cx, cy, color=white, scale=1.0):
    """Concentric circles motif — sun/moon/bump suggestion."""
    s = scale
    c.setStrokeColor(color)
    c.setLineWidth(0.8)
    c.setFillColor(white if False else color)
    c.setFillColor(color)
    # Outer ring
    c.setFillColor(color)
    c.circle(cx, cy, 38 * s, fill=0, stroke=1)
    c.circle(cx, cy, 26 * s, fill=0, stroke=1)
    c.circle(cx, cy, 14 * s, fill=0, stroke=1)


def draw_arc_motif(c, cx, cy, color=white, scale=1.0):
    """Set of nested arcs — gentle, third-trimester."""
    s = scale
    c.setStrokeColor(color)
    c.setLineWidth(1.0)
    for r in (50, 36, 22):
        c.arc(cx - r * s, cy - r * s, cx + r * s, cy + r * s, startAng=20, extent=140)


def draw_cover_motif(c, cx, cy, color=white):
    """Cover background — a vertical column of small botanical sprigs."""
    c.setStrokeColor(color)
    c.setLineWidth(0.8)
    # Central vertical hairline
    c.line(cx, cy - 180, cx, cy + 180)
    # Sprigs at intervals
    for offset, leaf in [(-160, 0.8), (-100, 1.0), (-40, 1.1), (40, 1.1),
                         (100, 1.0), (160, 0.8)]:
        y = cy + offset
        # Stems out to either side
        c.line(cx - 25 * leaf, y, cx, y)
        c.line(cx + 25 * leaf, y, cx, y)
        # Leaf circles
        c.circle(cx - 25 * leaf, y, 3 * leaf, fill=0, stroke=1)
        c.circle(cx + 25 * leaf, y, 3 * leaf, fill=0, stroke=1)


# ─────────────────────────────────────────────────────────────────────
# COVER (Page 1)
# ─────────────────────────────────────────────────────────────────────
def draw_cover(c):
    # Full sage background
    c.setFillColor(SAGE)
    c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)

    # Background graphic — column of sprigs centred
    draw_cover_motif(c, PAGE_W / 2, PAGE_H / 2 + 30, color=HexColor("#9bb89e"))

    # Decorative line above title
    title_y_rl = PAGE_H / 2 - 100
    c.setStrokeColor(white)
    c.setLineWidth(0.6)
    c.line(80, title_y_rl + 56, PAGE_W - 80, title_y_rl + 56)

    # Main title
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 32)
    c.drawCentredString(PAGE_W / 2, title_y_rl, "The Pregnancy Planner")

    # Subtitle
    c.setFillColor(TRIM_WHITE)
    c.setFont("Helvetica-Oblique", 13)
    c.drawCentredString(PAGE_W / 2, title_y_rl - 26,
                        "A place to plan and prepare, week-by-week.")

    # Lower decorative line
    c.setStrokeColor(white)
    c.setLineWidth(0.6)
    c.line(80, title_y_rl - 46, PAGE_W - 80, title_y_rl - 46)

    # Bottom small text
    c.setFillColor(white)
    c.setFont("Helvetica", 9)
    c.drawCentredString(PAGE_W / 2, BOTTOM_MARGIN + 10, "WEEKS 4 — 40")

    draw_side_tabs(c, 0)


# ─────────────────────────────────────────────────────────────────────
# CONTENTS PAGE (Page 2)
# ─────────────────────────────────────────────────────────────────────
def draw_contents_page(c):
    page_frame(c, label="Contents", active_idx=0, band_color=OAT)

    mx = MARGIN_X
    cw = CONTENT_W
    cur_y = BODY_START + 6

    def dot_leader_row(label, dest=None, indent=0, size=10, bold=False):
        nonlocal cur_y
        font = "Helvetica-Bold" if bold else "Helvetica"
        c.setFont(font, size)
        c.setFillColor(TEXT_DARK)
        c.drawString(mx + indent, rl(cur_y), label)
        label_w = c.stringWidth(label, font, size)
        dot_x = mx + indent + label_w + 4
        right_x = mx + cw - 2
        c.setFillColor(TEXT_SEC)
        c.setFont("Helvetica", 8)
        x = dot_x
        while x < right_x - 6:
            c.drawString(x, rl(cur_y) + 1, ".")
            x += 6
        # Clickable
        if dest:
            c.linkRect('', dest,
                       (mx + indent, rl(cur_y) - 2, right_x, rl(cur_y) + size + 2),
                       relative=0, Border=[0, 0, 0])
        cur_y += size + 8

    def sub_row(label, dest=None, indent=18, size=9):
        nonlocal cur_y
        c.setFont("Helvetica", size)
        c.setFillColor(TEXT_SEC)
        c.drawString(mx + indent, rl(cur_y), label)
        label_w = c.stringWidth(label, "Helvetica", size)
        dot_x = mx + indent + label_w + 4
        right_x = mx + cw - 2
        x = dot_x
        while x < right_x - 6:
            c.drawString(x, rl(cur_y) + 1, ".")
            x += 6
        if dest:
            c.linkRect('', dest,
                       (mx + indent, rl(cur_y) - 2, right_x, rl(cur_y) + size + 2),
                       relative=0, Border=[0, 0, 0])
        cur_y += size + 6

    dot_leader_row("Getting Started",     "dest_start",      bold=True)
    sub_row("About this planner",         "dest_about")
    sub_row("How to use it",              "dest_about")

    dot_leader_row("1st Trimester",       "dest_trim1",      bold=True)
    sub_row("Monthly overview",           "dest_trim1_cal")
    sub_row("Priorities & habits",        "dest_trim1_pre")
    sub_row("Weeks 4 – 12",               "dest_trim1_pre")

    dot_leader_row("2nd Trimester",       "dest_trim2",      bold=True)
    sub_row("Monthly overview",           "dest_trim2_cal")
    sub_row("Priorities & habits",        "dest_trim2_pre")
    sub_row("Weeks 13 – 26",              "dest_trim2_pre")

    dot_leader_row("3rd Trimester",       "dest_trim3",      bold=True)
    sub_row("Monthly overview",           "dest_trim3_cal")
    sub_row("Priorities & habits",        "dest_trim3_pre")
    sub_row("Weeks 27 – 40",              "dest_trim3_pre")

    dot_leader_row("Appointments",        "dest_appts",      bold=True)
    sub_row("Booking appointment (8 – 12 wks)", "dest_booking")
    sub_row("Dating scan (11 – 14 wks)",  "dest_dating_scan")
    sub_row("Anatomy scan (18 – 21 wks)", "dest_anatomy_scan")
    sub_row("Additional scans (template)","dest_additional_scan")
    sub_row("Midwife appointments",       "dest_midwife_25")

    dot_leader_row("Checklists",          "dest_checklists", bold=True)
    sub_row("Hospital bag",               "dest_hospital_bag")
    sub_row("Baby essentials",            "dest_baby_essentials")
    sub_row("Admin & work",               "dest_admin_work")
    sub_row("Postpartum care",            "dest_postpartum")
    sub_row("Signs of labour",            "dest_signs_of_labour")
    sub_row("Questions for your midwife", "dest_questions_midwife")
    sub_row("Questions at scan appts",    "dest_questions_scan")

    dot_leader_row("Birth Plan",          "dest_birthplan",  bold=True)
    sub_row("Vaginal birth plan",         "dest_birth_plan_vaginal")
    sub_row("C-section birth plan",       "dest_birth_plan_csection")

    dot_leader_row("Journal",             "dest_journal",    bold=True)
    dot_leader_row("Notes",                "dest_notes",     bold=True)
    dot_leader_row("A note to close",     "dest_closing",    bold=True)


# ─────────────────────────────────────────────────────────────────────
# ABOUT / HOW TO USE (Page 3)
# ─────────────────────────────────────────────────────────────────────
def draw_about_page(c):
    page_frame(c, label="About This Planner", active_idx=0, band_color=OAT)
    c.bookmarkPage("dest_about")

    mx = MARGIN_X
    cw = CONTENT_W
    cur_y = BODY_START + 6

    c.setFont("Helvetica-Bold", 15)
    c.setFillColor(TEXT_DARK)
    c.drawString(mx, rl(cur_y), "A calm place for everything.")
    cur_y += 28

    paragraphs = [
        "This planner is designed to hold everything pregnancy brings — the appointments, the tasks, "
        "the thoughts, and the questions. Not all at once. Just one week at a time.",

        "Each weekly page gives you a gentle structure: a handful of suggested tasks to get you started, "
        "space to add your own, a habit tracker for the small daily things, and room to write how you're feeling.",

        "There's no pressure to fill everything in. Use what helps. Leave what doesn't. This is your planner.",
    ]
    for para in paragraphs:
        cur_y = draw_wrapped(c, para, mx, cur_y, cw,
                             font="Helvetica", size=10.5, leading=16)
        cur_y += 10

    c.setStrokeColor(LINE_MED)
    c.setLineWidth(0.5)
    c.line(mx, rl(cur_y), mx + cw, rl(cur_y))
    cur_y += 20

    cur_y = draw_section_header(c, "HOW TO USE IT", cur_y, mx, cw)
    bullets = [
        "Weekly pages run from Week 4 to Week 40, each colour-coded by trimester.",
        "Suggested tasks are pre-printed — tick them off, or ignore them.",
        "Blank checkboxes at the bottom of each section are yours to fill in.",
        "Each trimester title page has space to plan the habits you want to establish in that period. "
        "Those habits can then be tracked on each weekly page.",
        "The habit tracker runs Mon–Sun. Write your habit on the line, fill circles as you go.",
        "Appointments, checklists, your birth plan, and notes pages are at the back.",
    ]
    for bullet in bullets:
        dot_y = rl(cur_y + 4)
        c.setFillColor(CLAY)
        c.circle(mx + 4, dot_y, 2.5, fill=1, stroke=0)
        cur_y = draw_wrapped(c, bullet, mx + 13, cur_y, cw - 13,
                             font="Helvetica", size=10, leading=15)
        cur_y += 4

    cur_y += 10
    c.setStrokeColor(LINE_MED)
    c.setLineWidth(0.5)
    c.line(mx, rl(cur_y), mx + cw, rl(cur_y))
    cur_y += 20

    cur_y = draw_section_header(c, "NAVIGATING YOUR PLANNER", cur_y, mx, cw)
    nav_bullets = [
        "Tap any tab on the right edge to jump between sections.",
        "Tap any icon in the small nav bar at the top to jump between sections.",
        "Tap any underlined phrase inside a weekly to-do (e.g. 'dating scan') to jump straight to that page.",
        "In GoodNotes, links only work when the pen tool is off (Read-Only mode).",
        "To add more pages, duplicate any page: press and hold the page thumbnail, then select Duplicate.",
    ]
    for bullet in nav_bullets:
        dot_y = rl(cur_y + 4)
        c.setFillColor(SAGE)
        c.circle(mx + 4, dot_y, 2.5, fill=1, stroke=0)
        cur_y = draw_wrapped(c, bullet, mx + 13, cur_y, cw - 13,
                             font="Helvetica", size=10, leading=15)
        cur_y += 4


# ─────────────────────────────────────────────────────────────────────
# TRIMESTER TITLE PAGE
# ─────────────────────────────────────────────────────────────────────
def draw_trimester_title_page(c, trimester_name, week_range, color, motif,
                              active_idx, dest_name):
    c.setFillColor(color)
    c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
    c.bookmarkPage(dest_name)

    # Background motif behind big text
    if motif == "leaf":
        draw_botanical_motif(c, PAGE_W / 2, PAGE_H / 2 + 30, color=HexColor("#9bb89e"), scale=1.6)
    elif motif == "circle":
        draw_circle_motif(c, PAGE_W / 2, PAGE_H / 2 + 30, color=HexColor("#deb491"), scale=1.6)
    elif motif == "arc":
        draw_arc_motif(c, PAGE_W / 2, PAGE_H / 2 + 30, color=HexColor("#cf957f"), scale=1.6)

    # Big trimester name — centred
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 40)
    c.drawCentredString(PAGE_W / 2, PAGE_H / 2 - 30, trimester_name)

    # Decorative line below
    c.setStrokeColor(white)
    c.setLineWidth(0.6)
    c.line(120, PAGE_H / 2 - 56, PAGE_W - 120, PAGE_H / 2 - 56)

    # Smaller week range subtitle
    c.setFillColor(TRIM_WHITE)
    c.setFont("Helvetica", 14)
    c.drawCentredString(PAGE_W / 2, PAGE_H / 2 - 80, week_range)

    draw_side_tabs(c, active_idx)


# ─────────────────────────────────────────────────────────────────────
# TRIMESTER MONTHLY OVERVIEW (grid)
# ─────────────────────────────────────────────────────────────────────
def draw_trimester_calendar(c, trimester_name, start_week, end_week,
                            color, active_idx, dest_name):
    """Grid monthly overview — no week label column."""
    page_frame(c, label=f"{trimester_name} — Monthly Overview",
               active_idx=active_idx, band_color=color)
    c.bookmarkPage(dest_name)

    mx = MARGIN_X
    cw = CONTENT_W
    cur_y = BODY_START + 14

    # Big title in body too
    c.setFont("Helvetica-Bold", 18)
    c.setFillColor(TEXT_DARK)
    c.drawString(mx, rl(cur_y), f"{trimester_name} — Monthly overview")
    cur_y += 26

    c.setFont("Helvetica-Oblique", 10)
    c.setFillColor(TEXT_SEC)
    c.drawString(mx, rl(cur_y), f"Weeks {start_week} – {end_week}")
    cur_y += 22

    # Grid: 7 day columns, one row per week, no left labels
    num_weeks = end_week - start_week + 1
    day_area_w = cw
    cell_w = day_area_w / 7
    notes_area_h = 80
    grid_h = PAGE_H - cur_y - BOTTOM_MARGIN - notes_area_h - 28
    cell_h = grid_h / (num_weeks + 1)

    grid_x = mx
    grid_top = cur_y

    days = ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]
    c.setFont("Helvetica-Bold", 8)
    c.setFillColor(TEXT_SEC)
    for i, d in enumerate(days):
        cx = grid_x + i * cell_w + cell_w / 2
        c.drawCentredString(cx, rl(grid_top + cell_h * 0.65), d)

    grid_top += cell_h

    # Continuous grid — drawn as one outer rect + interior lines (no separate boxes per cell)
    c.setStrokeColor(HABIT_BORDER)
    c.setLineWidth(0.5)
    # Outer
    c.rect(grid_x, rl(grid_top + num_weeks * cell_h),
           cell_w * 7, num_weeks * cell_h, fill=0, stroke=1)
    # Vertical column lines
    for col in range(1, 7):
        x = grid_x + col * cell_w
        c.line(x, rl(grid_top), x, rl(grid_top + num_weeks * cell_h))
    # Horizontal row lines
    for row in range(1, num_weeks):
        y = rl(grid_top + row * cell_h)
        c.line(grid_x, y, grid_x + 7 * cell_w, y)

    # Small NOTES section at bottom
    notes_top = grid_top + num_weeks * cell_h + 18
    cur_y = draw_section_header(c, "NOTES", notes_top, mx, cw)
    draw_note_lines(c, 4, cur_y, spacing=14, margin_x=mx, content_w=cw)


# ─────────────────────────────────────────────────────────────────────
# TRIMESTER PREAMBLE
# ─────────────────────────────────────────────────────────────────────
def draw_trimester_preamble(c, trimester_name, week_range, color,
                            opening, body_text, priorities, habits,
                            active_idx, dest_name):
    page_frame(c, label=trimester_name, sublabel=week_range,
               active_idx=active_idx, band_color=color)
    c.bookmarkPage(dest_name)

    mx = MARGIN_X
    cw = CONTENT_W
    cur_y = BODY_START + 6

    # Big body title
    c.setFont("Helvetica-Bold", 22)
    c.setFillColor(TEXT_DARK)
    c.drawString(mx, rl(cur_y), trimester_name)
    cur_y += 22

    c.setFont("Helvetica-Oblique", 11)
    c.setFillColor(TEXT_SEC)
    c.drawString(mx, rl(cur_y), week_range)
    cur_y += 22

    # Italic opening
    c.setFont("Helvetica-Oblique", 11)
    c.setFillColor(TEXT_DARK)
    cur_y = draw_wrapped(c, opening, mx, cur_y, cw,
                         font="Helvetica-Oblique", size=11, leading=17)
    cur_y += 8

    # Body paragraphs
    paras = [p.strip() for p in body_text.strip().split("\n\n") if p.strip()]
    for para in paras:
        cur_y = draw_wrapped(c, " ".join(para.split()), mx, cur_y, cw,
                             font="Helvetica", size=10.5, leading=16)
        cur_y += 10

    # PRIORITIES section
    cur_y = draw_section_header(c, "PRIORITIES", cur_y, mx, cw)
    for i, pri in enumerate(priorities, 1):
        # Numbered circle
        dot_y = rl(cur_y + 5)
        c.setFillColor(color)
        c.circle(mx + 5, dot_y, 6, fill=1, stroke=0)
        c.setFillColor(white)
        c.setFont("Helvetica-Bold", 7)
        c.drawCentredString(mx + 5, dot_y - 2.5, str(i))
        c.setFillColor(TEXT_DARK)
        cur_y = draw_wrapped(c, pri, mx + 16, cur_y, cw - 16,
                             font="Helvetica", size=10.5, leading=15)
        cur_y += 6

    # HABITS section
    cur_y += 8
    cur_y = draw_section_header(c, "HABITS TO BUILD THIS TRIMESTER", cur_y, mx, cw)
    for habit in habits:
        dot_y = rl(cur_y + 4)
        c.setFillColor(color)
        c.circle(mx + 4, dot_y, 2.5, fill=1, stroke=0)
        c.setFont("Helvetica", 10)
        c.setFillColor(TEXT_DARK)
        c.drawString(mx + 13, rl(cur_y), habit)
        cur_y += 16
    cur_y += 6
    cur_y = draw_habit_tracker(c, cur_y, margin_x=mx, content_w=cw,
                               rows=4, accent=color)


# ─────────────────────────────────────────────────────────────────────
# WEEKLY PAGE
# ─────────────────────────────────────────────────────────────────────
def get_trimester(week):
    if week <= 12: return "First Trimester"
    if week <= 26: return "Second Trimester"
    return "Third Trimester"


def get_trimester_color(week):
    if week <= 12: return SAGE, 1
    if week <= 26: return CLAY, 2
    return TERRACOTTA, 3


def draw_weekly_page(c, week_num, action_tasks):
    color, _ = get_trimester_color(week_num)
    if week_num <= 12:   active_idx = 1
    elif week_num <= 26: active_idx = 2
    else:                active_idx = 3

    page_frame(c, label=f"Week {week_num}", sublabel=get_trimester(week_num),
               active_idx=active_idx, band_color=color)

    # Column layout
    left_col_w  = int(CONTENT_W * 0.42)
    col_gap     = 14
    right_col_w = CONTENT_W - left_col_w - col_gap
    lx          = MARGIN_X
    rx          = MARGIN_X + left_col_w + col_gap

    body_top    = BODY_START
    body_bottom = PAGE_H - BOTTOM_MARGIN
    available_body_h = body_bottom - body_top

    # ── LEFT COLUMN: Daily Planner — full page height ──────────────
    lcur_y = body_top
    lcur_y = draw_section_header(c, "DAILY PLANNER", lcur_y, lx, left_col_w)

    days_labels = ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]
    available_for_days = (body_bottom - rl(lcur_y) + 0)  # remaining
    # Compute remaining height — using top-relative arithmetic
    day_section_h = (PAGE_H - BOTTOM_MARGIN - rl(lcur_y)) / 7

    for day_label in days_labels:
        # Day label
        c.setFont("Helvetica-Bold", 8)
        c.setFillColor(color)
        c.drawString(lx, rl(lcur_y + 9), day_label)
        # Subtle hairline under day label
        label_w = c.stringWidth(day_label, "Helvetica-Bold", 8)
        c.setStrokeColor(LINE_MED)
        c.setLineWidth(0.5)
        c.line(lx + label_w + 6, rl(lcur_y + 5),
               lx + left_col_w, rl(lcur_y + 5))
        lcur_y += 14

        # Note lines filling the day section
        remaining = day_section_h - 14
        line_spacing = 13
        n_lines = max(2, int(remaining / line_spacing))
        c.setStrokeColor(LINE_LIGHT)
        c.setLineWidth(0.4)
        for i in range(n_lines):
            ly = rl(lcur_y + line_spacing * (i + 1))
            c.line(lx, ly, lx + left_col_w, ly)
        lcur_y += line_spacing * n_lines + 2

    # ── RIGHT COLUMN ───────────────────────────────────────────────
    rcur_y = body_top

    # TO-DO LIST (action only)
    rcur_y = draw_section_header(c, "TO-DO LIST", rcur_y, rx, right_col_w)
    for task in action_tasks:
        rcur_y = draw_task_row(c, rcur_y, task, margin_x=rx,
                               content_w=right_col_w, accent=color)
    for _ in range(5):
        rcur_y = draw_free_row(c, rcur_y, margin_x=rx, content_w=right_col_w)

    # BUMP PHOTO
    rcur_y += SECTION_GAP - 10
    rcur_y = draw_section_header(c, "WEEKLY BUMP", rcur_y, rx, right_col_w)
    photo_h = 90
    c.setFillColor(PHOTO_BG)
    c.setStrokeColor(PHOTO_BORDER)
    c.setLineWidth(0.6)
    c.roundRect(rx, rl(rcur_y + photo_h), right_col_w, photo_h, 4,
                fill=1, stroke=1)
    # Tiny corner marks for "photo here"
    c.setFillColor(TEXT_SEC)
    c.setFont("Helvetica-Oblique", 8)
    c.drawCentredString(rx + right_col_w / 2,
                        rl(rcur_y + photo_h / 2) - 3,
                        "Add your weekly bump photo")
    rcur_y += photo_h + 8

    # HABITS
    rcur_y += SECTION_GAP - 14
    rcur_y = draw_section_header(c, "HABITS", rcur_y, rx, right_col_w)
    rcur_y = draw_habit_tracker(c, rcur_y, margin_x=rx,
                                content_w=right_col_w, rows=3, accent=color)

    # NOTES (fills remaining)
    rcur_y += SECTION_GAP - 12
    rcur_y = draw_section_header(c, "NOTES", rcur_y, rx, right_col_w)
    available = PAGE_H - BOTTOM_MARGIN - rl(rcur_y)
    note_count = max(2, int(available / NOTE_SPACING))
    draw_note_lines(c, note_count, rcur_y, margin_x=rx,
                    content_w=right_col_w)


# ─────────────────────────────────────────────────────────────────────
# APPOINTMENTS — section title page
# ─────────────────────────────────────────────────────────────────────
def draw_appts_title_page(c):
    c.setFillColor(OAT)
    c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
    c.bookmarkPage("dest_appts")

    draw_botanical_motif(c, PAGE_W / 2, PAGE_H / 2 + 30,
                         color=HexColor("#a08c75"), scale=1.6)

    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 40)
    c.drawCentredString(PAGE_W / 2, PAGE_H / 2 - 30, "Appointments")

    c.setStrokeColor(white)
    c.setLineWidth(0.6)
    c.line(120, PAGE_H / 2 - 56, PAGE_W - 120, PAGE_H / 2 - 56)

    c.setFillColor(TRIM_WHITE)
    c.setFont("Helvetica", 13)
    c.drawCentredString(PAGE_W / 2, PAGE_H / 2 - 80,
                        "Booking, scans, midwife appointments")

    draw_side_tabs(c, 4)


# ─────────────────────────────────────────────────────────────────────
# APPOINTMENT TEMPLATES
# ─────────────────────────────────────────────────────────────────────
def _appt_field(c, label, x, y, w):
    c.setFont("Helvetica-Bold", SEC_FONT)
    c.setFillColor(TEXT_SEC)
    c.drawString(x, rl(y), label)
    c.setStrokeColor(FREE_LINE)
    c.setLineWidth(0.5)
    c.line(x, rl(y + 16), x + w - 8, rl(y + 16))


def _appt_next_steps_bullets(c, top_y, mx, cw, count=4):
    c.setFont("Helvetica-Bold", SEC_FONT)
    c.setFillColor(TEXT_SEC)
    c.drawString(mx, rl(top_y), "NEXT STEPS")
    top_y += 14
    for _ in range(count):
        # bullet dot
        c.setFillColor(CLAY)
        c.circle(mx + 4, rl(top_y + 4), 2.2, fill=1, stroke=0)
        # underline
        c.setStrokeColor(FREE_LINE)
        c.setLineWidth(0.5)
        c.line(mx + 13, rl(top_y + 4), mx + cw, rl(top_y + 4))
        top_y += 18
    return top_y


def draw_booking_appt(c):
    page_frame(c, label="Booking Appointment",
               sublabel="8 – 12 weeks", active_idx=4, band_color=OAT)
    c.bookmarkPage("dest_booking")

    mx = MARGIN_X
    cw = CONTENT_W
    cur_y = BODY_START + 4

    # Intro
    c.setFont("Helvetica-Oblique", 10)
    c.setFillColor(TEXT_SEC)
    cur_y = draw_wrapped(c,
        "Your first official appointment — usually with your community midwife. "
        "Lasts around an hour. You'll talk through your medical history, options "
        "for screening, and what NHS care will look like from here.",
        mx, cur_y, cw, font="Helvetica-Oblique", size=10, leading=15,
        color=TEXT_SEC)
    cur_y += 12

    half = cw / 2
    _appt_field(c, "DATE", mx, cur_y, half)
    _appt_field(c, "TIME", mx + half, cur_y, half)
    cur_y += 28

    third = cw / 3
    _appt_field(c, "WEEK", mx, cur_y, third)
    _appt_field(c, "PROVIDER", mx + third, cur_y, third)
    _appt_field(c, "LOCATION", mx + 2 * third, cur_y, third)
    cur_y += 32

    # Questions
    c.setFont("Helvetica-Bold", SEC_FONT)
    c.setFillColor(TEXT_SEC)
    c.drawString(mx, rl(cur_y), "QUESTIONS TO ASK")
    cur_y += 14
    for _ in range(5):
        c.setStrokeColor(FREE_LINE)
        c.setLineWidth(0.5)
        c.line(mx, rl(cur_y), mx + cw, rl(cur_y))
        cur_y += 18

    cur_y += 4
    # Notes
    c.setFont("Helvetica-Bold", SEC_FONT)
    c.setFillColor(TEXT_SEC)
    c.drawString(mx, rl(cur_y), "NOTES")
    cur_y += 14
    for _ in range(5):
        c.setStrokeColor(LINE_LIGHT)
        c.setLineWidth(0.4)
        c.line(mx, rl(cur_y), mx + cw, rl(cur_y))
        cur_y += 16

    cur_y += 4
    _appt_next_steps_bullets(c, cur_y, mx, cw, count=4)


def _draw_scan_page(c, title, sublabel, dest_name, intro,
                    include_due_date=False):
    page_frame(c, label=title, sublabel=sublabel, active_idx=4, band_color=OAT)
    c.bookmarkPage(dest_name)

    mx = MARGIN_X
    cw = CONTENT_W
    cur_y = BODY_START + 4

    c.setFont("Helvetica-Oblique", 10)
    cur_y = draw_wrapped(c, intro, mx, cur_y, cw,
                         font="Helvetica-Oblique", size=10, leading=15,
                         color=TEXT_SEC)
    cur_y += 10

    half = cw / 2
    _appt_field(c, "DATE", mx, cur_y, half)
    _appt_field(c, "TIME", mx + half, cur_y, half)
    cur_y += 26

    third = cw / 3
    _appt_field(c, "WEEK", mx, cur_y, third)
    _appt_field(c, "SONOGRAPHER", mx + third, cur_y, third)
    _appt_field(c, "LOCATION", mx + 2 * third, cur_y, third)
    cur_y += 28

    if include_due_date:
        _appt_field(c, "ESTIMATED DUE DATE", mx, cur_y, cw)
        cur_y += 26

    # Photo box
    c.setFont("Helvetica-Bold", SEC_FONT)
    c.setFillColor(TEXT_SEC)
    c.drawString(mx, rl(cur_y), "SCAN PHOTO")
    cur_y += 14
    photo_h = 150
    c.setFillColor(PHOTO_BG)
    c.setStrokeColor(PHOTO_BORDER)
    c.setLineWidth(0.6)
    c.roundRect(mx, rl(cur_y + photo_h), cw, photo_h, 4, fill=1, stroke=1)
    c.setFillColor(TEXT_SEC)
    c.setFont("Helvetica-Oblique", 9)
    c.drawCentredString(mx + cw / 2, rl(cur_y + photo_h / 2) - 3,
                        "Add your scan photo here")
    cur_y += photo_h + 14

    # Notes
    c.setFont("Helvetica-Bold", SEC_FONT)
    c.setFillColor(TEXT_SEC)
    c.drawString(mx, rl(cur_y), "NOTES")
    cur_y += 14
    for _ in range(3):
        c.setStrokeColor(LINE_LIGHT)
        c.setLineWidth(0.4)
        c.line(mx, rl(cur_y), mx + cw, rl(cur_y))
        cur_y += 16

    cur_y += 4
    _appt_next_steps_bullets(c, cur_y, mx, cw, count=3)


def draw_dating_scan(c):
    _draw_scan_page(c,
        title="Dating Scan", sublabel="11 – 14 weeks",
        dest_name="dest_dating_scan",
        intro="Confirms how many weeks pregnant you are and your estimated due date. "
              "Usually combined with screening blood tests on the same day.",
        include_due_date=True)


def draw_anatomy_scan(c):
    _draw_scan_page(c,
        title="Anatomy Scan", sublabel="18 – 21 weeks",
        dest_name="dest_anatomy_scan",
        intro="A detailed scan checking baby's growth and development — heart, "
              "brain, spine, kidneys, limbs, and the position of the placenta. "
              "You may also choose to find out the baby's sex.")


def draw_additional_scan_template(c):
    page_frame(c, label="Additional Scan", sublabel="Template",
               active_idx=4, band_color=OAT)
    c.bookmarkPage("dest_additional_scan")

    mx = MARGIN_X
    cw = CONTENT_W
    cur_y = BODY_START + 4

    c.setFont("Helvetica-Oblique", 10)
    cur_y = draw_wrapped(c,
        "Use this template for any extra scan that doesn't fall within the "
        "standard dating or anatomy scan timings — for example, a growth scan, "
        "reassurance scan, or follow-up. To add more pages: press and hold the "
        "page thumbnail in GoodNotes and select Duplicate.",
        mx, cur_y, cw, font="Helvetica-Oblique", size=10, leading=15,
        color=TEXT_SEC)
    cur_y += 12

    half = cw / 2
    _appt_field(c, "DATE", mx, cur_y, half)
    _appt_field(c, "TIME", mx + half, cur_y, half)
    cur_y += 26

    _appt_field(c, "SCAN TYPE", mx, cur_y, cw)
    cur_y += 26

    third = cw / 3
    _appt_field(c, "WEEK", mx, cur_y, third)
    _appt_field(c, "SONOGRAPHER", mx + third, cur_y, third)
    _appt_field(c, "LOCATION", mx + 2 * third, cur_y, third)
    cur_y += 28

    # Photo box
    c.setFont("Helvetica-Bold", SEC_FONT)
    c.setFillColor(TEXT_SEC)
    c.drawString(mx, rl(cur_y), "SCAN PHOTO")
    cur_y += 14
    photo_h = 130
    c.setFillColor(PHOTO_BG)
    c.setStrokeColor(PHOTO_BORDER)
    c.setLineWidth(0.6)
    c.roundRect(mx, rl(cur_y + photo_h), cw, photo_h, 4, fill=1, stroke=1)
    c.setFillColor(TEXT_SEC)
    c.setFont("Helvetica-Oblique", 9)
    c.drawCentredString(mx + cw / 2, rl(cur_y + photo_h / 2) - 3,
                        "Add your scan photo here")
    cur_y += photo_h + 12

    c.setFont("Helvetica-Bold", SEC_FONT)
    c.setFillColor(TEXT_SEC)
    c.drawString(mx, rl(cur_y), "NOTES")
    cur_y += 14
    for _ in range(3):
        c.setStrokeColor(LINE_LIGHT)
        c.setLineWidth(0.4)
        c.line(mx, rl(cur_y), mx + cw, rl(cur_y))
        cur_y += 16

    cur_y += 4
    _appt_next_steps_bullets(c, cur_y, mx, cw, count=3)


# ─────────────────────────────────────────────────────────────────────
# MIDWIFE APPOINTMENT PAGES
# ─────────────────────────────────────────────────────────────────────
MIDWIFE_APPTS = [
    # (week, dest, first_time_only_note)
    (25, "dest_midwife_25", True),
    (28, "dest_midwife_28", False),
    (31, "dest_midwife_31", True),
    (34, "dest_midwife_34", False),
    (36, "dest_midwife_36", False),
    (38, "dest_midwife_38", False),
    (40, "dest_midwife_40", True),
    (41, "dest_midwife_41", False),
    (42, "dest_midwife_42", False),
]


def draw_midwife_appt(c, week, dest, first_time_only):
    title = f"Midwife Appointment"
    sublabel = f"{week} weeks"
    page_frame(c, label=title, sublabel=sublabel,
               active_idx=4, band_color=OAT)
    c.bookmarkPage(dest)

    mx = MARGIN_X
    cw = CONTENT_W
    cur_y = BODY_START + 4

    if first_time_only:
        # Pale terracotta tinted callout box
        callout_h = 32
        c.setFillColor(HexColor("#f7ebe1"))
        c.setStrokeColor(HexColor("#e4c6b4"))
        c.setLineWidth(0.5)
        c.roundRect(mx, rl(cur_y + callout_h), cw, callout_h, 4, fill=1, stroke=1)
        c.setFillColor(TERRA_DEEP)
        c.setFont("Helvetica-Bold", 8)
        c.drawString(mx + 12, rl(cur_y + 12), "FIRST-TIME MUMS ONLY")
        c.setFillColor(TEXT_DARK)
        c.setFont("Helvetica", 9)
        c.drawString(mx + 12, rl(cur_y + 24),
                     f"This {week}-week appointment is only routinely offered to first-time mums in the UK.")
        cur_y += callout_h + 14

    half = cw / 2
    _appt_field(c, "DATE", mx, cur_y, half)
    _appt_field(c, "TIME", mx + half, cur_y, half)
    cur_y += 28

    third = cw / 3
    _appt_field(c, "WEEK", mx, cur_y, third)
    _appt_field(c, "MIDWIFE", mx + third, cur_y, third)
    _appt_field(c, "LOCATION", mx + 2 * third, cur_y, third)
    cur_y += 30

    c.setFont("Helvetica-Bold", SEC_FONT)
    c.setFillColor(TEXT_SEC)
    c.drawString(mx, rl(cur_y), "QUESTIONS TO ASK")
    cur_y += 14
    for _ in range(4):
        c.setStrokeColor(FREE_LINE)
        c.setLineWidth(0.5)
        c.line(mx, rl(cur_y), mx + cw, rl(cur_y))
        cur_y += 18

    cur_y += 4
    c.setFont("Helvetica-Bold", SEC_FONT)
    c.setFillColor(TEXT_SEC)
    c.drawString(mx, rl(cur_y), "NOTES")
    cur_y += 14
    for _ in range(5):
        c.setStrokeColor(LINE_LIGHT)
        c.setLineWidth(0.4)
        c.line(mx, rl(cur_y), mx + cw, rl(cur_y))
        cur_y += 16

    cur_y += 4
    _appt_next_steps_bullets(c, cur_y, mx, cw, count=3)


def draw_midwife_template(c):
    page_frame(c, label="Midwife Appointment", sublabel="Template",
               active_idx=4, band_color=OAT)
    c.bookmarkPage("dest_midwife_extra")

    mx = MARGIN_X
    cw = CONTENT_W
    cur_y = BODY_START + 4

    c.setFont("Helvetica-Oblique", 10)
    cur_y = draw_wrapped(c,
        "Use this template for any midwife appointment that doesn't fall within "
        "the standard NHS schedule above. To add more pages: press and hold the "
        "page thumbnail in GoodNotes and select Duplicate.",
        mx, cur_y, cw, font="Helvetica-Oblique", size=10, leading=15,
        color=TEXT_SEC)
    cur_y += 12

    half = cw / 2
    _appt_field(c, "DATE", mx, cur_y, half)
    _appt_field(c, "TIME", mx + half, cur_y, half)
    cur_y += 28

    third = cw / 3
    _appt_field(c, "WEEK", mx, cur_y, third)
    _appt_field(c, "MIDWIFE", mx + third, cur_y, third)
    _appt_field(c, "LOCATION", mx + 2 * third, cur_y, third)
    cur_y += 30

    c.setFont("Helvetica-Bold", SEC_FONT)
    c.setFillColor(TEXT_SEC)
    c.drawString(mx, rl(cur_y), "QUESTIONS TO ASK")
    cur_y += 14
    for _ in range(4):
        c.setStrokeColor(FREE_LINE)
        c.setLineWidth(0.5)
        c.line(mx, rl(cur_y), mx + cw, rl(cur_y))
        cur_y += 18

    cur_y += 4
    c.setFont("Helvetica-Bold", SEC_FONT)
    c.setFillColor(TEXT_SEC)
    c.drawString(mx, rl(cur_y), "NOTES")
    cur_y += 14
    for _ in range(5):
        c.setStrokeColor(LINE_LIGHT)
        c.setLineWidth(0.4)
        c.line(mx, rl(cur_y), mx + cw, rl(cur_y))
        cur_y += 16

    cur_y += 4
    _appt_next_steps_bullets(c, cur_y, mx, cw, count=3)


# ─────────────────────────────────────────────────────────────────────
# CHECKLISTS — title page
# ─────────────────────────────────────────────────────────────────────
def draw_checklists_title_page(c):
    c.setFillColor(OAT)
    c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
    c.bookmarkPage("dest_checklists")

    draw_botanical_motif(c, PAGE_W / 2, PAGE_H / 2 + 30,
                         color=HexColor("#a08c75"), scale=1.6)

    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 40)
    c.drawCentredString(PAGE_W / 2, PAGE_H / 2 - 30, "Checklists")

    c.setStrokeColor(white)
    c.setLineWidth(0.6)
    c.line(120, PAGE_H / 2 - 56, PAGE_W - 120, PAGE_H / 2 - 56)

    c.setFillColor(TRIM_WHITE)
    c.setFont("Helvetica", 13)
    c.drawCentredString(PAGE_W / 2, PAGE_H / 2 - 80,
                        "Stay organised, one step at a time")

    draw_side_tabs(c, 5)


# ─────────────────────────────────────────────────────────────────────
# CHECKLIST HELPER
# ─────────────────────────────────────────────────────────────────────
def draw_checklist_item(c, text, top_y, mx, col_w, link=False):
    """Single checklist item with checkbox + wrapping text."""
    draw_checkbox(c, mx, top_y)
    tx = mx + CB_SIZE + 6

    body = _apply_links(text) if link else text
    para = Paragraph(body, _PARA_STYLE)
    w, h = para.wrap(col_w - CB_SIZE - 6, 200)
    # Vertically centre w/ checkbox baseline
    para.drawOn(c, tx, rl(top_y + CB_SIZE) + (CB_SIZE - TASK_FONT) / 2 + 1 - (h - TASK_FONT))
    return top_y + max(TASK_ROW_H, h + 4)


def draw_col_header(c, label, top_y, mx, col_w=None, accent=OAT):
    """Coloured small-caps column header with hairline underline.
    col_w is accepted but unused (kept for call-site symmetry)."""
    c.setFont("Helvetica-Bold", SEC_FONT + 1)
    c.setFillColor(accent)
    c.drawString(mx, rl(top_y), label)
    label_w = c.stringWidth(label, "Helvetica-Bold", SEC_FONT + 1)
    c.setStrokeColor(accent)
    c.setLineWidth(0.6)
    c.line(mx, rl(top_y + 3), mx + label_w, rl(top_y + 3))
    return top_y + 16


# ─────────────────────────────────────────────────────────────────────
# CHECKLIST PAGES (use Excel data subset)
# ─────────────────────────────────────────────────────────────────────
def draw_hospital_bag(c):
    page_frame(c, label="Hospital Bag", active_idx=5, band_color=OAT)
    c.bookmarkPage("dest_hospital_bag")

    gap = 14
    col_w = (CONTENT_W - gap) / 2
    lx = MARGIN_X
    rx = MARGIN_X + col_w + gap
    ly = ry = BODY_START + 4

    ly = draw_col_header(c, "FOR YOU — LABOUR", ly, lx, accent=CLAY)
    for item in [
        "Maternity notes", "Birth plan (printed copy)", "ID and hospital paperwork",
        "Phone and long charger cable", "Pillow from home", "Lip balm",
        "Hair ties / hairband", "Snacks (high-energy)",
        "Water bottle with straw", "Flip-flops for the shower",
        "TENS machine (if using)", "Mints / lozenges",
    ]:
        ly = draw_checklist_item(c, item, ly, lx, col_w)

    ly += 8
    ly = draw_col_header(c, "FOR YOU — AFTER BIRTH", ly, lx, accent=CLAY)
    for item in [
        "Nightgown / front-opening pyjamas",
        "Dressing gown", "Slippers",
        "Comfortable underwear (x5+)", "Nursing bras (x2)",
        "Maternity pads (2 packs)", "Breast pads",
        "Toiletries: toothbrush, dry shampoo, face wipes",
        "Going-home outfit (loose)",
    ]:
        ly = draw_checklist_item(c, item, ly, lx, col_w)

    ry = draw_col_header(c, "FOR BABY", ry, rx, accent=CLAY)
    for item in [
        "Sleepsuits / babygros (x3)", "Vests (x3)",
        "Hat (x2)", "Scratch mitts", "Socks", "Cardigan",
        "Going-home outfit", "Nappies (newborn pack)",
        "Cotton wool / wipes", "Muslin cloths (x4)",
        "Car seat (fitted in car)", "Blanket",
        "Snowsuit / weather layer (if winter)",
    ]:
        ry = draw_checklist_item(c, item, ry, rx, col_w)

    ry += 8
    ry = draw_col_header(c, "FOR YOUR PARTNER", ry, rx, accent=CLAY)
    for item in [
        "Change of clothes", "Toiletries", "Snacks and drinks",
        "Phone and charger", "Camera", "Pillow",
        "Cash / card for parking",
    ]:
        ry = draw_checklist_item(c, item, ry, rx, col_w)


def draw_baby_essentials(c):
    page_frame(c, label="Baby Essentials", active_idx=5, band_color=OAT)
    c.bookmarkPage("dest_baby_essentials")

    gap = 14
    col_w = (CONTENT_W - gap) / 2
    lx = MARGIN_X
    rx = MARGIN_X + col_w + gap
    ly = ry = BODY_START + 4

    for header, items in [
        ("SLEEPING", [
            "Cot or Moses basket",
            "Mattress (firm, flat, new if possible)",
            "Fitted sheets (x3)",
            "Sleeping bags (x2, age-appropriate tog)",
            "Cellular blankets",
            "Baby monitor",
            "Blackout blind or cover",
        ]),
        ("FEEDING", [
            "Nursing pillow",
            "Bottles and steriliser (if using formula or pumping)",
            "Breast pump (if planning to express)",
            "Bibs (x6)",
            "Muslin cloths (x10)",
            "Bottle brush",
        ]),
        ("CLOTHING (NEWBORN)", [
            "Sleepsuits / babygros (x7)",
            "Vests (x7)",
            "Cardigan (x2)",
            "Hats (x2)",
            "Socks (x3 pairs)",
            "Scratch mitts",
        ]),
    ]:
        ly = draw_col_header(c, header, ly, lx, col_w)
        for item in items:
            ly = draw_checklist_item(c, item, ly, lx, col_w)
        ly += 8

    for header, items in [
        ("BATHING", [
            "Baby bath or bath support",
            "Hooded towels (x2)",
            "Gentle baby wash",
            "Cotton wool",
        ]),
        ("CHANGING", [
            "Changing mat",
            "Changing bag",
            "Nappies (newborn pack)",
            "Nappy cream",
            "Wipes (sensitive)",
            "Nappy disposal bin or sacks",
        ]),
        ("OUT AND ABOUT", [
            "Pram / pushchair",
            "Car seat (essential)",
            "Sling or carrier (optional)",
            "Pram blanket / footmuff",
            "Rain cover",
        ]),
    ]:
        ry = draw_col_header(c, header, ry, rx, col_w)
        for item in items:
            ry = draw_checklist_item(c, item, ry, rx, col_w)
        ry += 8


def draw_admin_work(c):
    page_frame(c, label="Admin & Work", active_idx=5, band_color=OAT)
    c.bookmarkPage("dest_admin_work")

    mx = MARGIN_X
    cw = CONTENT_W
    cur_y = BODY_START + 4

    for header, items in [
        ("DURING PREGNANCY — WORK & HR", [
            "Notify employer of pregnancy in writing (by week 25)",
            "Request a workplace risk assessment",
            "Submit MATB1 form once received from midwife",
            "Confirm maternity leave start date with HR",
            "Discuss enhanced maternity pay (if applicable)",
            "Plan a handover for your role",
        ]),
        ("DURING PREGNANCY — FINANCES & ADMIN", [
            "Check NHS entitlements — free prescriptions and dental",
            "Apply for Maternity Allowance (if self-employed)",
            "Research Child Benefit (apply after birth)",
            "Update wills, insurance, or pension if needed",
            "Open a savings account for baby (optional)",
        ]),
        ("AFTER BIRTH", [
            "Register the birth (within 42 days in England & Wales)",
            "Apply for Child Benefit",
            "Notify HMRC of new child",
            "Add baby to your health insurance",
            "Register baby with a GP",
            "Apply for childcare hours (15 / 30 free hours)",
            "Inform employer of return-to-work date",
        ]),
    ]:
        cur_y = draw_col_header(c, header, cur_y, mx, accent=CLAY)
        for item in items:
            cur_y = draw_checklist_item(c, item, cur_y, mx, cw)
        cur_y += 10


def draw_postpartum_care(c):
    page_frame(c, label="Postpartum Care", active_idx=5, band_color=OAT)
    c.bookmarkPage("dest_postpartum")

    mx = MARGIN_X
    cw = CONTENT_W
    cur_y = BODY_START + 4

    c.setFont("Helvetica-Oblique", 10)
    cur_y = draw_wrapped(c,
        "The fourth trimester is yours too. Stock up on these before baby arrives "
        "so you can rest and recover at home without worrying about errands.",
        mx, cur_y, cw, font="Helvetica-Oblique", size=10, leading=15,
        color=TEXT_SEC)
    cur_y += 12

    gap = 14
    col_w = (cw - gap) / 2
    lx = mx
    rx = mx + col_w + gap
    ly = ry = cur_y

    for header, items in [
        ("BLEEDING & RECOVERY", [
            "Maternity pads (3+ packs — heavy flow)",
            "Disposable underwear or old pants",
            "Peri bottle (for rinsing perineum)",
            "Witch hazel pads / sitz spray",
            "Cooling pads / ice packs",
            "Donut cushion (if perineum sore)",
        ]),
        ("BREASTFEEDING", [
            "Nipple cream (lanolin or coconut)",
            "Breast pads (disposable or washable)",
            "Nursing bras (x3, soft cotton)",
            "Nursing tops or button-front pyjamas",
            "Haakaa or silicone pump",
            "Heat / cold packs for breasts",
        ]),
    ]:
        ly = draw_col_header(c, header, ly, lx, col_w, accent=CLAY)
        for item in items:
            ly = draw_checklist_item(c, item, ly, lx, col_w)
        ly += 8

    for header, items in [
        ("REST & COMFORT", [
            "Loose, comfortable clothing",
            "Robe with pockets",
            "Slippers",
            "Phone charger by the bed",
            "Easy-access snacks and water",
            "Pillow for nursing position",
        ]),
        ("RECOVERY FROM C-SECTION", [
            "High-waisted underwear (above the scar)",
            "Loose drawstring trousers",
            "Scar care: silicone strips or gel",
            "Stool softener (ask GP/midwife)",
            "Help with stairs and lifting",
        ]),
        ("EMOTIONAL & PRACTICAL", [
            "List of who to call if you feel low",
            "Meal train or batch-cooked freezer meals",
            "Pre-arranged help with older children / pets",
            "Plan for visitors: how, when, who",
        ]),
    ]:
        ry = draw_col_header(c, header, ry, rx, col_w, accent=CLAY)
        for item in items:
            ry = draw_checklist_item(c, item, ry, rx, col_w)
        ry += 8


def draw_signs_of_labour(c):
    page_frame(c, label="Signs of Labour", active_idx=5, band_color=OAT)
    c.bookmarkPage("dest_signs_of_labour")

    mx = MARGIN_X
    cw = CONTENT_W
    cur_y = BODY_START + 4

    c.setFont("Helvetica-Oblique", 10)
    cur_y = draw_wrapped(c,
        "Knowing what to look out for — and what's reassuring — helps you feel "
        "calmer in the days and weeks before birth. Always trust your instincts "
        "and call your midwife or hospital if anything worries you.",
        mx, cur_y, cw, font="Helvetica-Oblique", size=10, leading=15,
        color=TEXT_SEC)
    cur_y += 14

    cur_y = draw_col_header(c, "EARLY SIGNS", cur_y, mx, accent=CLAY)
    for item in [
        "A 'show' — pink or blood-tinged mucus plug",
        "Mild cramping or backache that comes and goes",
        "Nesting urge — sudden energy and tidying",
        "Loose stools or upset stomach",
        "Baby moving lower into the pelvis ('lightening')",
        "Braxton Hicks contractions becoming more frequent",
    ]:
        cur_y = draw_checklist_item(c, item, cur_y, mx, cw)

    cur_y += 8
    cur_y = draw_col_header(c, "ACTIVE LABOUR", cur_y, mx, accent=CLAY)
    for item in [
        "Regular contractions getting longer, stronger, closer together",
        "Contractions you can't talk through",
        "Waters breaking — clear / pale fluid (note time and colour)",
        "Strong urge to bear down (in established labour)",
    ]:
        cur_y = draw_checklist_item(c, item, cur_y, mx, cw)

    cur_y += 8
    cur_y = draw_col_header(c, "CALL YOUR MIDWIFE / HOSPITAL IF…", cur_y, mx, accent=TERRACOTTA)
    for item in [
        "Contractions are 5 minutes apart, lasting 60 seconds, for 1 hour (5-1-1)",
        "Your waters break — even if not in labour yet",
        "Waters are green, brown, or blood-stained",
        "You notice reduced or changed baby movements",
        "You have bright red bleeding (more than a smear)",
        "Severe or persistent headache, visual changes, or swelling",
        "You feel something isn't right — trust that feeling",
    ]:
        cur_y = draw_checklist_item(c, item, cur_y, mx, cw)


def draw_questions_midwife(c):
    page_frame(c, label="Questions for Your Midwife", active_idx=5, band_color=OAT)
    c.bookmarkPage("dest_questions_midwife")

    mx = MARGIN_X
    cw = CONTENT_W
    cur_y = BODY_START + 4

    c.setFont("Helvetica-Oblique", 10)
    cur_y = draw_wrapped(c,
        "Prompts to think through before each appointment. Pick the ones that "
        "matter most to you — don't feel you need to ask every single one.",
        mx, cur_y, cw, font="Helvetica-Oblique", size=10, leading=15,
        color=TEXT_SEC)
    cur_y += 12

    gap = 14
    col_w = (cw - gap) / 2
    lx = mx
    rx = mx + col_w + gap
    ly = ry = cur_y

    for header, items in [
        ("FIRST TRIMESTER", [
            "What screening tests are offered and when?",
            "Which vitamins do I need to take?",
            "Are my current medications safe to continue?",
            "What symptoms should I report?",
            "How do I contact you between appointments?",
        ]),
        ("SECOND TRIMESTER", [
            "Is my baby growing as expected?",
            "What does this scan / blood test result mean?",
            "When will I feel movements? What should they feel like?",
            "How do I start a birth plan?",
            "Which antenatal classes do you recommend?",
        ]),
    ]:
        ly = draw_col_header(c, header, ly, lx, col_w, accent=CLAY)
        for item in items:
            ly = draw_checklist_item(c, item, ly, lx, col_w)
        ly += 8

    for header, items in [
        ("THIRD TRIMESTER", [
            "How is baby positioned?",
            "What are my pain relief options?",
            "When should I come into hospital?",
            "What if I go past my due date?",
            "What happens if I need an induction or C-section?",
            "How do I monitor baby's movements at home?",
        ]),
        ("APPROACHING / AFTER 40 WEEKS", [
            "What does my induction pathway look like?",
            "What is a membrane sweep and what does it involve?",
            "What if I want to wait — and what are the risks?",
            "What postnatal support is available locally?",
            "When will my postnatal check be?",
        ]),
    ]:
        ry = draw_col_header(c, header, ry, rx, col_w, accent=CLAY)
        for item in items:
            ry = draw_checklist_item(c, item, ry, rx, col_w)
        ry += 8


def draw_questions_scan(c):
    page_frame(c, label="Questions at Scan Appointments",
               active_idx=5, band_color=OAT)
    c.bookmarkPage("dest_questions_scan")

    mx = MARGIN_X
    cw = CONTENT_W
    cur_y = BODY_START + 4

    c.setFont("Helvetica-Oblique", 10)
    cur_y = draw_wrapped(c,
        "Use these prompts for both your dating scan and anatomy scan. "
        "Sonographers welcome questions — but they may not be able to discuss "
        "everything in detail. Your midwife will follow up on results.",
        mx, cur_y, cw, font="Helvetica-Oblique", size=10, leading=15,
        color=TEXT_SEC)
    cur_y += 12

    cur_y = draw_col_header(c, "AT THE DATING SCAN (11 – 14 weeks)", cur_y, mx, accent=SAGE)
    for item in [
        "Is everything developing as expected?",
        "Is there one baby — or more?",
        "What's my updated due date?",
        "What does the nuchal translucency measurement show?",
        "What happens with the combined screening results?",
        "When and how will I get my results?",
    ]:
        cur_y = draw_checklist_item(c, item, cur_y, mx, cw)

    cur_y += 8
    cur_y = draw_col_header(c, "AT THE ANATOMY SCAN (18 – 21 weeks)", cur_y, mx, accent=CLAY)
    for item in [
        "Is baby's growth on track?",
        "Are all the major organs developing as expected?",
        "Where is the placenta positioned?",
        "Is the amniotic fluid level normal?",
        "Can you tell me the sex of the baby (if I want to know)?",
        "Do I need a follow-up scan, and if so, when?",
        "When and how will I get the full report?",
    ]:
        cur_y = draw_checklist_item(c, item, cur_y, mx, cw)

    cur_y += 8
    cur_y = draw_col_header(c, "ANY SCAN — GENERAL", cur_y, mx, accent=TERRACOTTA)
    for item in [
        "What did you see today that you'd like the midwife to follow up?",
        "Is there anything I should monitor at home?",
        "Are there any signs I should call about urgently?",
    ]:
        cur_y = draw_checklist_item(c, item, cur_y, mx, cw)


# ─────────────────────────────────────────────────────────────────────
# BIRTH PLAN
# ─────────────────────────────────────────────────────────────────────
def draw_birthplan_title_page(c):
    c.setFillColor(OAT)
    c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
    c.bookmarkPage("dest_birthplan")
    c.bookmarkPage("dest_birth_plan")   # alias for inline links

    draw_botanical_motif(c, PAGE_W / 2, PAGE_H / 2 + 30,
                         color=HexColor("#a08c75"), scale=1.6)

    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 40)
    c.drawCentredString(PAGE_W / 2, PAGE_H / 2 - 30, "Birth Plan")

    c.setStrokeColor(white)
    c.setLineWidth(0.6)
    c.line(120, PAGE_H / 2 - 56, PAGE_W - 120, PAGE_H / 2 - 56)

    c.setFillColor(TRIM_WHITE)
    c.setFont("Helvetica", 12)
    c.drawCentredString(PAGE_W / 2, PAGE_H / 2 - 80,
                        "Vaginal birth · C-section")

    draw_side_tabs(c, 6)


def _bp_section_label(c, label, top_y, mx, cw, accent=CLAY):
    c.setFont("Helvetica-Bold", 9)
    c.setFillColor(accent)
    c.drawString(mx, rl(top_y), label)
    label_w = c.stringWidth(label, "Helvetica-Bold", 9)
    c.setStrokeColor(accent)
    c.setLineWidth(0.5)
    c.line(mx + label_w + 6, rl(top_y + 3), mx + cw, rl(top_y + 3))
    return top_y + 14


def _bp_field(c, label, top_y, mx, w):
    c.setFont("Helvetica", 8)
    c.setFillColor(TEXT_SEC)
    c.drawString(mx, rl(top_y), label.upper())
    c.setStrokeColor(FREE_LINE)
    c.setLineWidth(0.5)
    c.line(mx, rl(top_y + 14), mx + w - 8, rl(top_y + 14))
    return top_y + 22


def _bp_check_options(c, options, top_y, mx, col_w):
    """Render a vertical list of small checkboxes for preset options."""
    for opt in options:
        draw_free_checkbox(c, mx, top_y)
        c.setFont("Helvetica", 9.5)
        c.setFillColor(TEXT_DARK)
        c.drawString(mx + CB_SIZE + 6, rl(top_y + CB_SIZE) - 1, opt)
        top_y += 16
    return top_y


def _bp_free_lines(c, count, top_y, mx, cw):
    for _ in range(count):
        c.setStrokeColor(FREE_LINE)
        c.setLineWidth(0.5)
        c.line(mx, rl(top_y + 4), mx + cw, rl(top_y + 4))
        top_y += 16
    return top_y


def draw_birth_plan_vaginal_p1(c):
    page_frame(c, label="Birth Plan", sublabel="Vaginal birth",
               active_idx=6, band_color=OAT)
    c.bookmarkPage("dest_birth_plan_vaginal")

    mx = MARGIN_X
    cw = CONTENT_W
    cur_y = BODY_START + 4

    # OVERVIEW
    cur_y = _bp_section_label(c, "OVERVIEW", cur_y, mx, cw, accent=CLAY)
    half = cw / 2
    cur_y_save = cur_y
    cur_y = _bp_field(c, "Due date", cur_y, mx, half)
    cur_y_a = cur_y
    cur_y = _bp_field(c, "Preferred location", cur_y, mx, half)

    cur_y_right = cur_y_save
    cur_y_right = _bp_field(c, "Birth partner — name", cur_y_right, mx + half, half)
    cur_y_right = _bp_field(c, "Birth partner — contact", cur_y_right, mx + half, half)

    cur_y = max(cur_y, cur_y_right) + 4
    cur_y = _bp_field(c, "Dietary requirements / allergies", cur_y, mx, cw)
    cur_y += 6

    # DURING LABOUR — SET UP
    cur_y = _bp_section_label(c, "DURING LABOUR — SET UP", cur_y, mx, cw, accent=CLAY)
    col_w = (cw - 14) / 2
    save_y = cur_y

    c.setFont("Helvetica", 8); c.setFillColor(TEXT_SEC)
    c.drawString(mx, rl(cur_y), "WHO I WANT IN THE ROOM")
    cur_y += 12
    cur_y = _bp_check_options(c, [
        "Birth partner only",
        "No trainees / observers, please",
        "Limited interruptions where possible",
        "Same midwife where possible",
    ], cur_y, mx, col_w)
    cur_y = _bp_free_lines(c, 2, cur_y, mx, col_w)

    right_y = save_y
    c.setFont("Helvetica", 8); c.setFillColor(TEXT_SEC)
    c.drawString(mx + col_w + 14, rl(right_y), "ENVIRONMENT PREFERENCES")
    right_y += 12
    right_y = _bp_check_options(c, [
        "Dim lights / fairy lights",
        "Music from my playlist",
        "Aromatherapy / oils",
        "Quiet talking / minimal interruption",
    ], right_y, mx + col_w + 14, col_w)
    right_y = _bp_free_lines(c, 2, right_y, mx + col_w + 14, col_w)

    cur_y = max(cur_y, right_y) + 6

    # HYDRATION
    cur_y = _bp_section_label(c, "HYDRATION", cur_y, mx, cw, accent=CLAY)
    cur_y = _bp_check_options(c, [
        "Drinking water / oral fluids as I want",
        "IV fluids only if medically necessary",
        "Ice chips if requested",
    ], cur_y, mx, cw)
    cur_y += 4

    # BIRTHING POSITIONS
    cur_y = _bp_section_label(c, "BIRTHING POSITIONS — WHAT I'D LIKE TO TRY", cur_y, mx, cw, accent=CLAY)
    cur_y = _bp_check_options(c, [
        "Upright / standing",
        "On all fours",
        "Side-lying",
        "Water birth (if available)",
        "Birthing ball",
        "Squatting",
        "Whatever feels right in the moment",
    ], cur_y, mx, cw)


def draw_birth_plan_vaginal_p2(c):
    page_frame(c, label="Birth Plan", sublabel="Vaginal birth — cont.",
               active_idx=6, band_color=OAT)

    mx = MARGIN_X
    cw = CONTENT_W
    cur_y = BODY_START + 4

    # PAIN RELIEF
    cur_y = _bp_section_label(c, "PAIN RELIEF — IN ORDER OF PREFERENCE", cur_y, mx, cw, accent=CLAY)
    cur_y = _bp_check_options(c, [
        "No pain relief unless I ask",
        "Hypnobirthing techniques / breathing",
        "TENS machine",
        "Water (bath / pool)",
        "Gas and air (Entonox)",
        "Pethidine / Diamorphine",
        "Epidural",
        "Whatever I decide on the day",
    ], cur_y, mx, cw)
    cur_y += 4

    # MONITORING & INTERVENTIONS
    cur_y = _bp_section_label(c, "BABY MONITORING & INTERVENTIONS", cur_y, mx, cw, accent=CLAY)
    cur_y = _bp_check_options(c, [
        "Intermittent monitoring (preferred)",
        "Continuous monitoring only if medically needed",
        "Avoid routine vaginal examinations where possible",
        "Discuss any intervention with me before it happens",
    ], cur_y, mx, cw)
    cur_y += 4

    # ASSISTED DELIVERY OPTIONS
    cur_y = _bp_section_label(c, "IF ASSISTED DELIVERY BECOMES NEEDED", cur_y, mx, cw, accent=CLAY)
    cur_y = _bp_check_options(c, [
        "Forceps — discuss with me first",
        "Ventouse (vacuum) — discuss with me first",
        "Episiotomy — only if necessary, please discuss",
        "Unplanned C-section — see my C-section plan",
    ], cur_y, mx, cw)
    cur_y += 4

    # SECOND STAGE
    cur_y = _bp_section_label(c, "SECOND STAGE — PUSHING", cur_y, mx, cw, accent=CLAY)
    cur_y = _bp_check_options(c, [
        "Spontaneous pushing — follow my body",
        "Coached pushing only if needed",
        "Mirror to see baby being born",
        "Partner to help guide baby out (if possible)",
    ], cur_y, mx, cw)
    cur_y += 4

    # NOTES
    cur_y = _bp_section_label(c, "ANYTHING ELSE", cur_y, mx, cw, accent=CLAY)
    cur_y = _bp_free_lines(c, 4, cur_y, mx, cw)


def draw_birth_plan_postdelivery(c):
    page_frame(c, label="Birth Plan", sublabel="Post-delivery",
               active_idx=6, band_color=OAT)

    mx = MARGIN_X
    cw = CONTENT_W
    cur_y = BODY_START + 4

    cur_y = _bp_section_label(c, "DELAYED CORD CLAMPING", cur_y, mx, cw, accent=CLAY)
    cur_y = _bp_check_options(c, [
        "Yes — please wait at least 1–3 minutes",
        "Yes — until the cord stops pulsating",
        "Cord blood banking arranged (private)",
        "Partner to cut the cord (if possible)",
    ], cur_y, mx, cw)
    cur_y += 4

    cur_y = _bp_section_label(c, "IMMEDIATE SKIN-TO-SKIN", cur_y, mx, cw, accent=CLAY)
    cur_y = _bp_check_options(c, [
        "Yes — on my chest immediately if safe",
        "Partner to do skin-to-skin if I can't",
        "Delay weighing / measuring until after first feed",
    ], cur_y, mx, cw)
    cur_y += 4

    cur_y = _bp_section_label(c, "PLACENTA", cur_y, mx, cw, accent=CLAY)
    cur_y = _bp_check_options(c, [
        "Active management — injection to deliver placenta",
        "Physiological — wait and deliver naturally",
        "I'd like to see the placenta",
        "We'd like to take the placenta home",
    ], cur_y, mx, cw)
    cur_y += 4

    cur_y = _bp_section_label(c, "FEEDING", cur_y, mx, cw, accent=CLAY)
    cur_y = _bp_check_options(c, [
        "Breastfeeding — please support first latch",
        "Formula feeding from the start",
        "Combination feeding",
        "Undecided — please support whichever I choose",
    ], cur_y, mx, cw)
    cur_y += 4

    cur_y = _bp_section_label(c, "BABY'S FIRST CHECKS", cur_y, mx, cw, accent=CLAY)
    cur_y = _bp_check_options(c, [
        "Vitamin K — injection (preferred)",
        "Vitamin K — oral doses",
        "Decline vitamin K",
        "Newborn checks done with me / partner present",
    ], cur_y, mx, cw)
    cur_y += 4

    cur_y = _bp_section_label(c, "IF NICU OR SCBU IS NEEDED", cur_y, mx, cw, accent=TERRACOTTA)
    cur_y = _bp_check_options(c, [
        "Partner to stay with baby at all times",
        "Skin-to-skin as soon as it's possible",
        "Pump milk for baby as soon as I can",
        "Updates every step of the way, please",
    ], cur_y, mx, cw)
    cur_y += 4

    cur_y = _bp_section_label(c, "MY POSTPARTUM CHECKS", cur_y, mx, cw, accent=CLAY)
    cur_y = _bp_check_options(c, [
        "Privacy for any examinations",
        "Same midwife where possible",
        "Pain relief offered if needed",
    ], cur_y, mx, cw)


def draw_birth_plan_csection(c):
    page_frame(c, label="Birth Plan", sublabel="C-section",
               active_idx=6, band_color=OAT)
    c.bookmarkPage("dest_birth_plan_csection")

    mx = MARGIN_X
    cw = CONTENT_W
    cur_y = BODY_START + 4

    c.setFont("Helvetica-Oblique", 9.5)
    cur_y = draw_wrapped(c,
        "Whether planned or unplanned, a C-section is still your birth. "
        "These preferences help keep the experience close to what you want, "
        "where it's safely possible.",
        mx, cur_y, cw, font="Helvetica-Oblique", size=10, leading=14,
        color=TEXT_SEC)
    cur_y += 10

    cur_y = _bp_section_label(c, "OVERVIEW", cur_y, mx, cw, accent=TERRACOTTA)
    half = cw / 2
    save = cur_y
    cur_y = _bp_field(c, "Due date / planned date", cur_y, mx, half)
    right_y = save
    right_y = _bp_field(c, "Birth partner — name", right_y, mx + half, half)
    cur_y = max(cur_y, right_y)
    cur_y = _bp_field(c, "Hospital", cur_y, mx, half)
    cur_y = _bp_field(c, "Dietary requirements / allergies", cur_y, mx, cw)
    cur_y += 4

    cur_y = _bp_section_label(c, "IN THEATRE", cur_y, mx, cw, accent=TERRACOTTA)
    cur_y = _bp_check_options(c, [
        "Birth partner present throughout",
        "Music from my playlist played",
        "Drape lowered at the moment of birth (if safe)",
        "Quiet talking / commentary as baby is born",
        "Explanations from the team as it happens",
    ], cur_y, mx, cw)
    cur_y += 4

    cur_y = _bp_section_label(c, "AS BABY IS BORN", cur_y, mx, cw, accent=TERRACOTTA)
    cur_y = _bp_check_options(c, [
        "Delayed cord clamping where possible",
        "Immediate skin-to-skin with me (if safe)",
        "Skin-to-skin with partner if I can't",
        "Cord blood banking arranged (private)",
        "Photos / video allowed",
    ], cur_y, mx, cw)
    cur_y += 4

    cur_y = _bp_section_label(c, "FEEDING & FIRST CHECKS", cur_y, mx, cw, accent=TERRACOTTA)
    cur_y = _bp_check_options(c, [
        "Support for first breastfeed in recovery",
        "Formula feeding from the start",
        "Vitamin K — injection",
        "Vitamin K — oral",
        "Baby's newborn checks done with me present",
    ], cur_y, mx, cw)
    cur_y += 4

    cur_y = _bp_section_label(c, "MY RECOVERY", cur_y, mx, cw, accent=TERRACOTTA)
    cur_y = _bp_check_options(c, [
        "Help with first feed when I'm ready",
        "Pain relief explained and offered",
        "Help mobilising slowly when safe",
        "Privacy for examinations",
    ], cur_y, mx, cw)
    cur_y += 4

    cur_y = _bp_section_label(c, "ANYTHING ELSE", cur_y, mx, cw, accent=TERRACOTTA)
    cur_y = _bp_free_lines(c, 4, cur_y, mx, cw)


# ─────────────────────────────────────────────────────────────────────
# JOURNAL + NOTES — title pages and lined pages
# ─────────────────────────────────────────────────────────────────────
def draw_journal_title_page(c):
    c.setFillColor(OAT)
    c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
    c.bookmarkPage("dest_journal")

    draw_botanical_motif(c, PAGE_W / 2, PAGE_H / 2 + 30,
                         color=HexColor("#a08c75"), scale=1.6)

    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 44)
    c.drawCentredString(PAGE_W / 2, PAGE_H / 2 - 30, "Journal")

    c.setStrokeColor(white)
    c.setLineWidth(0.6)
    c.line(120, PAGE_H / 2 - 56, PAGE_W - 120, PAGE_H / 2 - 56)

    c.setFillColor(TRIM_WHITE)
    c.setFont("Helvetica-Oblique", 12)
    c.drawCentredString(PAGE_W / 2, PAGE_H / 2 - 80,
                        "Words for the days you want to remember")

    draw_side_tabs(c, 7)


def draw_notes_title_page(c):
    c.setFillColor(OAT)
    c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
    c.bookmarkPage("dest_notes")

    draw_botanical_motif(c, PAGE_W / 2, PAGE_H / 2 + 30,
                         color=HexColor("#a08c75"), scale=1.6)

    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 44)
    c.drawCentredString(PAGE_W / 2, PAGE_H / 2 - 30, "Notes")

    c.setStrokeColor(white)
    c.setLineWidth(0.6)
    c.line(120, PAGE_H / 2 - 56, PAGE_W - 120, PAGE_H / 2 - 56)

    draw_side_tabs(c, 8)


def draw_blank_lined_page(c, band_label, active_idx):
    page_frame(c, label=band_label, active_idx=active_idx, band_color=OAT)

    top    = BAND_H + NAV_BAR_H + 20 * mm
    bottom = BOTTOM_MARGIN + 20
    spacing = NOTE_SPACING
    count = int((PAGE_H - top - bottom) / spacing)

    c.setStrokeColor(LINE_LIGHT)
    c.setLineWidth(0.4)
    for i in range(count):
        ly = PAGE_H - top - spacing * (i + 1)
        c.line(MARGIN_X, ly, MARGIN_X + CONTENT_W, ly)


# ─────────────────────────────────────────────────────────────────────
# CLOSING PAGE
# ─────────────────────────────────────────────────────────────────────
def draw_closing_page(c):
    c.setFillColor(SAGE)
    c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
    c.bookmarkPage("dest_closing")

    draw_cover_motif(c, PAGE_W / 2, PAGE_H / 2, color=HexColor("#9bb89e"))

    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 28)
    c.drawCentredString(PAGE_W / 2, PAGE_H / 2 + 60, "And here you are.")

    # Body — multi-line, centred
    lines = [
        "However you arrived here — through long nights of nausea,",
        "the weight of a third trimester body, the rush of a quick labour",
        "or the slow patience of a long one — you have done something",
        "extraordinary.",
        "",
        "Your body has grown, stretched, ached, and remade itself.",
        "Your mind has held excitement, fear, joy, and the quiet kind",
        "of love that only this moment makes.",
        "",
        "There will be more days ahead with their own kind of hard.",
        "There will be more days ahead with their own kind of joy.",
        "Both are yours, and you are ready for both.",
        "",
        "Wishing you slow mornings, soft landings,",
        "and a deep, settled love with your new baby.",
    ]

    cy = PAGE_H / 2 + 20
    c.setFont("Helvetica", 11.5)
    c.setFillColor(white)
    for line in lines:
        if line == "":
            cy -= 10
        else:
            c.drawCentredString(PAGE_W / 2, cy, line)
            cy -= 17

    c.setStrokeColor(white)
    c.setLineWidth(0.6)
    c.line(140, BOTTOM_MARGIN + 70, PAGE_W - 140, BOTTOM_MARGIN + 70)

    c.setFillColor(TRIM_WHITE)
    c.setFont("Helvetica-Oblique", 10)
    c.drawCentredString(PAGE_W / 2, BOTTOM_MARGIN + 50,
                        "Welcome to the rest of it.")

    draw_side_tabs(c, 8)


# ─────────────────────────────────────────────────────────────────────
# CONTENT DATA
# ─────────────────────────────────────────────────────────────────────
# Action-only weekly to-dos derived from the Excel
# 'Weekly Tasks' sheet (rows where TYPE=Action). Tasks from weeks 1-3
# are not used (planner starts at week 4).
WEEKLY_ACTIONS = {
    4:  ["Book a GP appointment",
         "Start folic acid (400mcg daily)"],
    5:  ["Register with your GP or midwife",
         "Note your last menstrual period date"],
    6:  ["Book your midwife booking appointment (ideally by week 8 – 10)",
         "Look into pregnancy multivitamins"],
    7:  ["Prepare questions for your booking appointment",
         "Avoid alcohol, raw fish, soft cheeses, and raw meat"],
    8:  ["Attend booking appointment (if booked)",
         "Complete blood tests requested at booking"],
    9:  ["Rest when you need to — fatigue is normal",
         "Research maternity pay and leave entitlements"],
    10: ["Book your dating scan if not yet done",
         "Think about who you want at your scan"],
    11: ["Prepare questions for your sonographer",
         "Note any symptoms to mention to your midwife"],
    12: ["Attend your dating scan",
         "Review combined screening results with midwife"],
    13: ["Book your anatomy scan",
         "Consider sharing pregnancy news more widely"],
    14: ["Research maternity leave options in detail",
         "Speak to HR about your company's maternity policy"],
    15: ["Start a baby names list if you'd like",
         "Explore antenatal class options — popular ones book up early"],
    16: ["Attend midwife appointment",
         "Think about your birth preferences — no rush"],
    17: ["Book antenatal classes if not yet done",
         "Research hospitals or birth centres nearby"],
    18: ["Book your anatomy scan if not yet done",
         "Start thinking about birth preferences formally"],
    19: ["Prepare questions for your anatomy scan",
         "Think about hospital bag basics"],
    20: ["Attend your anatomy scan",
         "Note scan results and any follow-up needed"],
    21: ["Discuss scan results with your midwife",
         "Start your hospital bag list formally"],
    22: ["Research childcare options and register interest on waiting lists",
         "Look into your employer's enhanced maternity policy"],
    23: ["Book antenatal classes if not yet started",
         "Start a postpartum plan — meals, support, rest"],
    24: ["Attend midwife appointment",
         "Review your baby budget and priorities"],
    25: ["Notify employer of pregnancy (legal deadline)",
         "Submit MATB1 form once received from midwife"],
    26: ["Submit maternity leave paperwork to HR",
         "Confirm your last working day in writing"],
    27: ["Book a hospital or birth centre tour",
         "Start gathering items for your hospital bag"],
    28: ["Attend midwife appointment (blood tests this week)",
         "Review your birth preferences document"],
    29: ["Finalise nursery essentials purchases",
         "Install or plan for baby's car seat"],
    30: ["Start packing your hospital bag",
         "Confirm your birth partner's availability around your due date"],
    31: ["Attend antenatal class if still in session",
         "Talk through your birth preferences with your midwife"],
    32: ["Add key items to hospital bag",
         "Pre-register at your hospital or birth centre"],
    33: ["Finalise your birth preferences document",
         "Prepare your home for baby's arrival"],
    34: ["Attend midwife appointment",
         "Prepare list of people to notify after birth"],
    35: ["Check hospital bag is complete",
         "Know the signs of labour",
         "Consider private Group B Strep test"],
    36: ["Weekly midwife appointments begin from now",
         "Install car seat and check fitting",
         "Stock up on postpartum essentials for yourself"],
    37: ["Final check on hospital bag",
         "Inform your birth partner to stay on call"],
    38: ["Attend weekly midwife appointment",
         "Tie up any loose ends at home"],
    39: ["Stay in contact with your midwife",
         "Know when to call your midwife or hospital"],
    40: ["Stay in contact with your midwife",
         "Rest, breathe, trust yourself"],
}


# Trimester content
FIRST_TRIMESTER_BODY = """
This is the quietest trimester from the outside — and often the most overwhelming on the inside. You may feel exhausted in a way that's hard to explain, or nauseous, or both. That's not weakness. That's your body doing something extraordinary.

This trimester is mostly about rest and letting things settle. There isn't much you need to do yet, and that's okay. A few gentle things will come your way — a booking appointment, a first scan — and this planner will walk you through them, one at a time.

For now, be kind to yourself. The planning can wait. You can't do this wrong.
"""

SECOND_TRIMESTER_BODY = """
The fog of the first trimester tends to lift, and with it comes a little more space to think, to plan, and to even enjoy this. Your bump will start to show. At some point, you'll feel movement — and that moment tends to make everything feel more real.

This is a good time to start thinking ahead, gently. Not all at once — just a little each week. Appointments to book, things to look into, lists to begin. Nothing is urgent. Everything has time.

Use this trimester to get curious, not busy. There's a difference.
"""

THIRD_TRIMESTER_BODY = """
Things might feel heavier now — physically and emotionally. That's real, and it's okay. Your body is preparing for something remarkable, and it's allowed to take up space doing so.

This trimester is about getting ready, not perfect. A bag packed. A few preferences written down. A little more rest wherever you can find it. The to-do list in this planner will feel manageable because it is — it's been designed so nothing sneaks up on you.

You don't need to have everything figured out. You just need to show up. And you already are.
"""

T1_PRIORITIES = [
    "Confirm your pregnancy, start folic acid, and book your first GP / midwife appointment.",
    "Get your booking appointment and dating scan in the diary — these are the two anchor moments of this trimester.",
    "Rest. Be gentle with yourself. Tell only who you want to, when you're ready.",
]
T1_HABITS = ["e.g. Take folic acid daily",
             "e.g. Rest when you need to"]

T2_PRIORITIES = [
    "Attend your anatomy scan and midwife appointments — note results and questions in this planner.",
    "Begin lists you'll keep coming back to — hospital bag, baby essentials, birth preferences.",
    "Tell your employer (legal deadline week 25) and start a maternity leave plan.",
]
T2_HABITS = ["e.g. Gentle exercise (walk / swim / yoga)",
             "e.g. Track baby movements once you feel them"]

T3_PRIORITIES = [
    "Finalise your hospital bag, car seat, birth preferences, and postpartum essentials.",
    "Attend more frequent midwife appointments and know the signs of labour.",
    "Slow down. Stock the freezer. Set up your support network for after birth.",
]
T3_HABITS = ["e.g. Practise breathing techniques",
             "e.g. Prepare freezer meals"]


# ─────────────────────────────────────────────────────────────────────
# BUILD
# ─────────────────────────────────────────────────────────────────────
def build_pdf(out_path=None):
    if out_path is None:
        out_path = os.path.join(os.path.dirname(__file__),
                                "pregnancy_planner_2026_v3.pdf")

    c = canvas.Canvas(out_path, pagesize=(PAGE_W, PAGE_H))

    # ── Cover ─────────────────────────────────────────────────────
    c.bookmarkPage("dest_start")
    draw_cover(c)
    c.showPage()

    # ── Contents ──────────────────────────────────────────────────
    draw_contents_page(c)
    c.showPage()

    # ── About ─────────────────────────────────────────────────────
    draw_about_page(c)
    c.showPage()

    # ── 1ST TRIMESTER ─────────────────────────────────────────────
    draw_trimester_title_page(c, "1st Trimester", "Weeks 1 – 12",
                              SAGE, "leaf", 1, "dest_trim1")
    c.showPage()

    draw_trimester_calendar(c, "1st Trimester", 1, 12,
                            SAGE, 1, "dest_trim1_cal")
    c.showPage()

    draw_trimester_preamble(c, "1st Trimester", "Weeks 1 – 12", SAGE,
        "You might not look different yet, but everything is already changing.",
        FIRST_TRIMESTER_BODY, T1_PRIORITIES, T1_HABITS, 1, "dest_trim1_pre")
    c.showPage()

    for w in range(4, 13):
        draw_weekly_page(c, w, WEEKLY_ACTIONS[w])
        c.showPage()

    # ── 2ND TRIMESTER ─────────────────────────────────────────────
    draw_trimester_title_page(c, "2nd Trimester", "Weeks 13 – 26",
                              CLAY, "circle", 2, "dest_trim2")
    c.showPage()

    draw_trimester_calendar(c, "2nd Trimester", 13, 26,
                            CLAY, 2, "dest_trim2_cal")
    c.showPage()

    draw_trimester_preamble(c, "2nd Trimester", "Weeks 13 – 26", CLAY,
        "This is where most women find their breath again.",
        SECOND_TRIMESTER_BODY, T2_PRIORITIES, T2_HABITS, 2, "dest_trim2_pre")
    c.showPage()

    for w in range(13, 27):
        draw_weekly_page(c, w, WEEKLY_ACTIONS[w])
        c.showPage()

    # ── 3RD TRIMESTER ─────────────────────────────────────────────
    draw_trimester_title_page(c, "3rd Trimester", "Weeks 27 – 40",
                              TERRACOTTA, "arc", 3, "dest_trim3")
    c.showPage()

    draw_trimester_calendar(c, "3rd Trimester", 27, 40,
                            TERRACOTTA, 3, "dest_trim3_cal")
    c.showPage()

    draw_trimester_preamble(c, "3rd Trimester", "Weeks 27 – 40", TERRACOTTA,
        "You're in the home stretch — and you're more ready than you feel.",
        THIRD_TRIMESTER_BODY, T3_PRIORITIES, T3_HABITS, 3, "dest_trim3_pre")
    c.showPage()

    for w in range(27, 41):
        draw_weekly_page(c, w, WEEKLY_ACTIONS[w])
        c.showPage()

    # ── APPOINTMENTS ──────────────────────────────────────────────
    draw_appts_title_page(c)
    c.showPage()

    draw_booking_appt(c)
    c.showPage()

    draw_dating_scan(c)
    c.showPage()

    draw_anatomy_scan(c)
    c.showPage()

    draw_additional_scan_template(c)
    c.showPage()

    for (week, dest, ftm) in MIDWIFE_APPTS:
        draw_midwife_appt(c, week, dest, ftm)
        c.showPage()

    draw_midwife_template(c)
    c.showPage()

    # ── CHECKLISTS ────────────────────────────────────────────────
    draw_checklists_title_page(c)
    c.showPage()

    draw_hospital_bag(c)
    c.showPage()

    draw_baby_essentials(c)
    c.showPage()

    draw_admin_work(c)
    c.showPage()

    draw_postpartum_care(c)
    c.showPage()

    draw_signs_of_labour(c)
    c.showPage()

    draw_questions_midwife(c)
    c.showPage()

    draw_questions_scan(c)
    c.showPage()

    # ── BIRTH PLAN ────────────────────────────────────────────────
    draw_birthplan_title_page(c)
    c.showPage()

    draw_birth_plan_vaginal_p1(c)
    c.showPage()

    draw_birth_plan_vaginal_p2(c)
    c.showPage()

    draw_birth_plan_postdelivery(c)
    c.showPage()

    draw_birth_plan_csection(c)
    c.showPage()

    # ── JOURNAL ───────────────────────────────────────────────────
    draw_journal_title_page(c)
    c.showPage()
    for _ in range(4):
        draw_blank_lined_page(c, "Journal", active_idx=7)
        c.showPage()

    # ── NOTES ─────────────────────────────────────────────────────
    draw_notes_title_page(c)
    c.showPage()
    for _ in range(4):
        draw_blank_lined_page(c, "Notes", active_idx=8)
        c.showPage()

    # ── CLOSING ───────────────────────────────────────────────────
    draw_closing_page(c)
    c.showPage()

    c.save()
    print(f"Saved: {out_path}")


if __name__ == "__main__":
    build_pdf()
