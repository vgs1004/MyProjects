"""Build a presentable Excel action tracker from the extracted minutes.

Sheets:
  Overview        KPI tiles, summary, open actions by owner, actions by priority, two charts
  Action tracker  one row per action, with a Status dropdown (Open / In progress / Done)
  Decisions
  Open questions

The Overview uses formulas, so when someone changes a Status to Done the
tiles and charts update by themselves.
"""

import io

from openpyxl import Workbook
from openpyxl.chart import BarChart, DoughnutChart, Reference
from openpyxl.chart.label import DataLabelList
from openpyxl.chart.series import DataPoint
from openpyxl.formatting.rule import CellIsRule, FormulaRule
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.worksheet.table import Table, TableStyleInfo

# Same palette as the portfolio
PLUM, PINK, BLUE, ORANGE, PERI = "3A1E4A", "E0527F", "5371D1", "E88F30", "7A96EA"
LIGHT = {"High": "FBE3EA", "Medium": "FCEBD9", "Low": "E3F2E6"}
DARK = {"High": "A3264F", "Medium": "9A5410", "Low": "2E7D45"}
GREY, AMBER = "8A8A8A", "FFF1C9"

FONT = "Calibri"
WHITE = Font(name=FONT, color="FFFFFF", bold=True)
THIN = Side(style="thin", color="E2DCE6")
BOX = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
WRAP = Alignment(wrap_text=True, vertical="top")
STATUSES = ["Open", "In progress", "Done"]


def _fill(hex_):
    return PatternFill("solid", start_color=hex_, end_color=hex_)


def _banner(ws, text, sub, last_col):
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=last_col)
    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=last_col)
    c = ws.cell(1, 1, text)
    c.font, c.fill, c.alignment = Font(name=FONT, size=18, bold=True, color="FFFFFF"), _fill(PLUM), Alignment(vertical="center", indent=1)
    s = ws.cell(2, 1, sub)
    s.font, s.fill, s.alignment = Font(name=FONT, size=10, italic=True, color="FFFFFF"), _fill(PLUM), Alignment(vertical="center", indent=1)
    for col in range(1, last_col + 1):
        ws.cell(1, col).fill = ws.cell(2, col).fill = _fill(PLUM)
    ws.row_dimensions[1].height, ws.row_dimensions[2].height = 34, 20


def _table(ws, name, headers, rows, widths, first_row=4):
    """Write a styled Excel Table (with filter buttons) and return its data range rows."""
    for j, (h, w) in enumerate(zip(headers, widths), start=1):
        c = ws.cell(first_row, j, h)
        c.font, c.fill, c.alignment, c.border = WHITE, _fill(PLUM), Alignment(vertical="center", wrap_text=True), BOX
        ws.column_dimensions[get_column_letter(j)].width = w
    rows = rows or [["(none)"] + [""] * (len(headers) - 1)]
    for i, row in enumerate(rows, start=first_row + 1):
        for j, v in enumerate(row, start=1):
            c = ws.cell(i, j, v)
            c.font, c.alignment, c.border = Font(name=FONT, size=11), WRAP, BOX
    last = first_row + len(rows)
    ref = f"A{first_row}:{get_column_letter(len(headers))}{last}"
    t = Table(displayName=name, ref=ref)
    t.tableStyleInfo = TableStyleInfo(name="TableStyleLight1", showRowStripes=True)
    ws.add_table(t)
    ws.freeze_panes = ws.cell(first_row + 1, 1)
    ws.sheet_view.zoomScale = 110
    ws.page_setup.orientation = "landscape"
    ws.page_setup.fitToWidth, ws.page_setup.fitToHeight = 1, 0
    ws.sheet_properties.pageSetUpPr.fitToPage = True
    ws.print_title_rows = f"{first_row}:{first_row}"
    return first_row + 1, last


def build_workbook(result: dict, title: str = "Meeting", meeting_date: str = "") -> bytes:
    wb = Workbook()
    ov = wb.active
    ov.title = "Overview"
    when = f"Meeting date: {meeting_date}  ·  " if meeting_date else ""

    # ---------------- Action tracker ----------------
    at = wb.create_sheet("Action tracker")
    _banner(at, f"{title}: action tracker",
            "Change Status to In progress or Done as work moves on. The Overview updates by itself.", 8)
    actions = result["action_items"]
    rows = [[i, a.get("task", ""), a.get("owner", ""), a.get("due", ""), a.get("priority", "Medium"),
             "Open", a.get("check", ""), a.get("source_quote", "")] for i, a in enumerate(actions, 1)]
    first, last = _table(at, "Actions",
                         ["#", "Task", "Owner", "Due", "Priority", "Status", "Needs a check", "Evidence from transcript"],
                         rows, [5, 48, 18, 16, 11, 14, 26, 46])
    for r in range(first, last + 1):
        at.cell(r, 1).alignment = Alignment(horizontal="center", vertical="top")
        at.cell(r, 8).font = Font(name=FONT, size=10, italic=True, color=GREY)
        for col in (5, 6):
            at.cell(r, col).alignment = Alignment(horizontal="center", vertical="top")
    dv = DataValidation(type="list", formula1=f'"{",".join(STATUSES)}"', allow_blank=False)
    at.add_data_validation(dv)
    dv.add(f"F{first}:F{last}")
    for p in ("High", "Medium", "Low"):
        at.conditional_formatting.add(f"E{first}:E{last}", CellIsRule(
            operator="equal", formula=[f'"{p}"'], fill=_fill(LIGHT[p]), font=Font(bold=True, color=DARK[p])))
    at.conditional_formatting.add(f"G{first}:G{last}", FormulaRule(
        formula=[f'LEN($G{first})>0'], fill=_fill(AMBER), font=Font(color="7A5A00")))
    at.conditional_formatting.add(f"A{first}:H{last}", FormulaRule(
        formula=[f'$F{first}="Done"'], font=Font(color="A0A0A0", strike=True)))
    at.conditional_formatting.add(f"F{first}:F{last}", CellIsRule(
        operator="equal", formula=['"In progress"'], fill=_fill("E3E9FA"), font=Font(color=BLUE, bold=True)))

    rng = lambda col: f"'Action tracker'!${col}${first}:${col}${last}"  # noqa: E731
    owner_r, prio_r, status_r, check_r = rng("C"), rng("E"), rng("F"), rng("G")

    # ---------------- Decisions / Open questions ----------------
    de = wb.create_sheet("Decisions")
    _banner(de, f"{title}: decisions", "What the group agreed in the meeting.", 5)
    _table(de, "Decisions", ["#", "Decision", "Decided by", "Needs a check", "Evidence from transcript"],
           [[i, d.get("decision", ""), d.get("decided_by", ""), d.get("check", ""), d.get("source_quote", "")]
            for i, d in enumerate(result["decisions"], 1)], [5, 55, 28, 22, 46])
    oq = wb.create_sheet("Open questions")
    _banner(oq, f"{title}: open questions", "Raised in the meeting but not answered yet.", 3)
    _table(oq, "OpenQuestions", ["#", "Question", "Raised by"],
           [[i, q.get("question", ""), q.get("raised_by", "")] for i, q in enumerate(result["open_questions"], 1)],
           [5, 70, 22])

    # ---------------- Overview ----------------
    ov.sheet_view.showGridLines = False
    for col in range(1, 13):
        ov.column_dimensions[get_column_letter(col)].width = 13
    ov.column_dimensions["A"].width = 2
    _banner(ov, f"{title}: minutes and actions",
            f"{when}Made on this computer from the transcript with a local AI model. Check rows marked 'Needs a check'.", 12)

    n_dec, n_q = len(result["decisions"]), len(result["open_questions"])
    tiles = [
        ("Action items", f"=COUNTA({rng('B')})" if actions else 0, PINK),
        ("Still open", f'=COUNTIF({status_r},"<>Done")' if actions else 0, BLUE),
        ("High priority open", f'=COUNTIFS({prio_r},"High",{status_r},"<>Done")' if actions else 0, ORANGE),
        ("Need a check", f'=COUNTIF({check_r},"?*")' if actions else 0, PERI),
        ("Decisions · Questions", f"{n_dec} · {n_q}", PLUM),
    ]
    for k, (label, value, colour) in enumerate(tiles):
        c0 = 2 + k * 2
        ov.merge_cells(start_row=4, start_column=c0, end_row=4, end_column=c0 + 1)
        ov.merge_cells(start_row=5, start_column=c0, end_row=6, end_column=c0 + 1)
        lab, val = ov.cell(4, c0, label), ov.cell(5, c0, value)
        lab.font = Font(name=FONT, size=10, bold=True, color="FFFFFF")
        val.font = Font(name=FONT, size=26, bold=True, color="FFFFFF")
        lab.alignment = Alignment(horizontal="center", vertical="center")
        val.alignment = Alignment(horizontal="center", vertical="center")
        for r in (4, 5, 6):
            for c in (c0, c0 + 1):
                ov.cell(r, c).fill = _fill(colour)
    ov.row_dimensions[4].height, ov.row_dimensions[5].height, ov.row_dimensions[6].height = 22, 26, 26

    def heading(row, text):
        h = ov.cell(row, 2, text)
        h.font = Font(name=FONT, size=13, bold=True, color=PLUM)
        for c in range(2, 12):
            ov.cell(row, c).border = Border(bottom=Side(style="medium", color=PINK))

    heading(8, "Summary")
    ov.merge_cells("B9:K11")
    s = ov.cell(9, 2, result.get("summary", ""))
    s.font, s.alignment = Font(name=FONT, size=11), Alignment(wrap_text=True, vertical="top")
    for r in (9, 10, 11):
        ov.row_dimensions[r].height = 22

    # Open actions by owner (left) and by priority (below it); charts on the right
    heading(13, "Actions by owner and priority")
    owners = list(dict.fromkeys(a.get("owner", "") or "Not stated" for a in actions)) or ["(none)"]
    hdr = 14
    for j, h in enumerate(["Owner", "Open", "Done"], start=2):
        c = ov.cell(hdr, j, h)
        c.font, c.fill, c.border = WHITE, _fill(PLUM), BOX
    for i, o in enumerate(owners, start=hdr + 1):
        ov.cell(i, 2, o)
        ov.cell(i, 3, f'=COUNTIFS({owner_r},B{i},{status_r},"<>Done")' if actions else 0)
        ov.cell(i, 4, f'=COUNTIFS({owner_r},B{i},{status_r},"Done")' if actions else 0)
        for c in (2, 3, 4):
            ov.cell(i, c).border, ov.cell(i, c).font = BOX, Font(name=FONT, size=11)
    o_last = hdr + len(owners)

    p_hdr = o_last + 2
    for j, h in enumerate(["Priority", "Actions"], start=2):
        c = ov.cell(p_hdr, j, h)
        c.font, c.fill, c.border = WHITE, _fill(PLUM), BOX
    for i, p in enumerate(["High", "Medium", "Low"], start=p_hdr + 1):
        ov.cell(i, 2, p).font = Font(name=FONT, bold=True, color=DARK[p])
        ov.cell(i, 2).fill = _fill(LIGHT[p])
        ov.cell(i, 3, f'=COUNTIF({prio_r},B{i})' if actions else 0)
        ov.cell(i, 2).border = ov.cell(i, 3).border = BOX

    bar = BarChart()
    bar.type, bar.grouping, bar.overlap = "bar", "stacked", 100
    bar.title, bar.style = "Actions per owner", 10
    bar.add_data(Reference(ov, min_col=3, max_col=4, min_row=hdr, max_row=o_last), titles_from_data=True)
    bar.set_categories(Reference(ov, min_col=2, min_row=hdr + 1, max_row=o_last))
    bar.series[0].graphicalProperties.solidFill = BLUE
    bar.series[1].graphicalProperties.solidFill = "C9C3CF"
    bar.y_axis.majorGridlines = None
    bar.y_axis.majorUnit = 1  # whole actions only
    bar.x_axis.scaling.orientation = "maxMin"  # first owner at the top
    bar.y_axis.delete = False
    bar.x_axis.delete = False
    bar.legend.position = "b"
    bar.height, bar.width = 7.5, 13
    ov.add_chart(bar, "F14")

    dn = DoughnutChart(holeSize=55)
    dn.title, dn.style = "Actions by priority", 10
    dn.add_data(Reference(ov, min_col=3, min_row=p_hdr, max_row=p_hdr + 3), titles_from_data=True)
    dn.set_categories(Reference(ov, min_col=2, min_row=p_hdr + 1, max_row=p_hdr + 3))
    for idx, colour in enumerate([PINK, ORANGE, "6BBF7F"]):
        pt = DataPoint(idx=idx)
        pt.graphicalProperties.solidFill = colour
        dn.series[0].dPt.append(pt)
    dn.dataLabels = DataLabelList()
    dn.dataLabels.showVal = True
    dn.dataLabels.showSerName = dn.dataLabels.showCatName = False
    dn.dataLabels.showPercent = dn.dataLabels.showLegendKey = dn.dataLabels.showLeaderLines = False
    dn.legend.position = "r"
    dn.height, dn.width = 7.5, 9
    ov.add_chart(dn, f"B{p_hdr + 5}")

    ov.page_setup.orientation = "landscape"
    ov.sheet_properties.pageSetUpPr.fitToPage = True
    ov.page_setup.fitToWidth, ov.page_setup.fitToHeight = 1, 1

    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()
