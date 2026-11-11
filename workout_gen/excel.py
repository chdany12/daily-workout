"""Writes a Workout to a phone-friendly .xlsx: one tab, big text, tap-to-check column."""

from urllib.parse import quote_plus

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.worksheet.datavalidation import DataValidation

from .engine import Row, Workout

COLS = {"A": 6, "B": 30, "C": 22, "D": 44, "E": 11}
WRAP_TOP = Alignment(wrap_text=True, vertical="top")
CENTER = Alignment(horizontal="center", vertical="center")
THIN = Side(style="thin", color="BBBBBB")
BOX = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)

SECTION_FILL = {
    "WARM-UP": "FFE08A",
    "MAIN EVENT": "FF8A80",
    "COOL-DOWN": "A5D6A7",
}
GROUP_FILL = "EEEEEE"
DEMO_URL = "https://www.youtube.com/results?search_query="
NEW_FILL = "E1F5FE"


def _height(*texts, width_chars=40, line=21, minimum=26):
    lines = max(1, max((len(t or "") // width_chars + 1) for t in texts))
    return max(minimum, lines * line)


def write(w: Workout, path):
    wb = Workbook()
    ws = wb.active
    ws.title = "Workout"
    for col, width in COLS.items():
        ws.column_dimensions[col].width = width

    check = DataValidation(type="list", formula1='"✅"', allow_blank=True,
                           showDropDown=False)  # False = show the arrow (Excel's naming is backwards)
    ws.add_data_validation(check)

    r = 1

    def merged(text, font, fill=None, height=None):
        nonlocal r
        ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=5)
        c = ws.cell(r, 1, text)
        c.font, c.alignment = font, WRAP_TOP
        if fill:
            c.fill = PatternFill("solid", fgColor=fill)
        ws.row_dimensions[r].height = height or _height(text, width_chars=95)
        r += 1

    merged(w.name, Font(size=24, bold=True), height=40)
    focus_label = {"upper": "Upper body", "lower": "Lower body", "core": "Core", "full": "Full body"}[w.focus]
    merged(f"{focus_label}  ·  {w.minutes} min  ·  {w.format_name}  ·  Level {w.level}",
           Font(size=14, color="555555"), height=24)
    merged("HOW IT WORKS:  " + w.format_rules, Font(size=13))
    merged("🎲 TWIST:  " + w.twist, Font(size=13, bold=True, color="6A1B9A"), fill="F3E5F5")
    r += 1

    for c, h in zip("ABCDE", ["✓", "Move", "Do", "How", "Demo"]):
        cell = ws[f"{c}{r}"]
        cell.value = h
        cell.font = Font(size=13, bold=True, color="FFFFFF")
        cell.fill = PatternFill("solid", fgColor="37474F")
        cell.alignment = CENTER
    ws.freeze_panes = f"A{r + 1}"
    r += 1

    def section(title, rows: list[Row]):
        nonlocal r
        merged(title, Font(size=16, bold=True), fill=SECTION_FILL[title], height=28)
        for row in rows:
            if row.group:
                merged(row.move, Font(size=13, bold=True, italic=True), fill=GROUP_FILL, height=24)
                continue
            move = ("🆕 " if row.new else "") + row.move
            values = ["", move, row.do, row.cue]
            for c, v in zip("ABCD", values):
                cell = ws[f"{c}{r}"]
                cell.value = v
                cell.border = BOX
                cell.alignment = CENTER if c == "A" else WRAP_TOP
                cell.font = Font(size=14, bold=(c == "B"))
                if row.new and c == "B":
                    cell.fill = PatternFill("solid", fgColor=NEW_FILL)
            if row.cue:  # real exercise rows (not deck draws / score lines) get a video link
                name = row.move.split(" = ")[-1]
                link = ws[f"E{r}"]
                link.value = "▶ Watch"
                link.hyperlink = DEMO_URL + quote_plus(f"{name} exercise how to")
                link.font = Font(size=13, bold=True, color="1565C0", underline="single")
                link.alignment = CENTER
                link.border = BOX
            check.add(f"A{r}")
            ws.row_dimensions[r].height = _height(row.cue, move, width_chars=38)
            r += 1
        r += 1

    section("WARM-UP", w.warmup)
    section("MAIN EVENT", w.main)
    section("COOL-DOWN", w.cooldown)

    merged("AFTER — tell me how it went (this decides what v2 looks like)", Font(size=14, bold=True),
           fill="CFD8DC", height=26)
    for q in ["Finished? (yes / partly / no)", "Fun? (1–5)", "Too hard / too easy / just right?",
              "Most boring part?", "Best part?"]:
        ws[f"B{r}"] = q
        ws[f"B{r}"].font = Font(size=13)
        ws.merge_cells(start_row=r, start_column=3, end_row=r, end_column=5)
        ws[f"C{r}"].border = BOX
        ws.row_dimensions[r].height = 26
        r += 1
    ws[f"B{r + 1}"] = "🆕 = a move you've never done before"
    ws[f"B{r + 1}"].font = Font(size=11, italic=True, color="777777")

    ws.page_setup.orientation = "portrait"
    ws.page_setup.fitToWidth = 1
    ws.page_setup.fitToHeight = 0
    ws.sheet_properties.pageSetUpPr.fitToPage = True
    wb.save(path)
