"""
Builds the base workbook (all 7 sheets, Settings values, Summary
formulas, Control/Run Log layout) with openpyxl. VBA modules and the
Control-sheet buttons are added afterwards via Excel COM
(inject_and_run.py), since openpyxl can't touch the VBA project or
create Form Control button shapes.
"""
import datetime
import os

import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ---- palette (warm, no blue; distinct from the other 4 Excel projects) ----
INK = "3A332C"
ACCENT = "6B4C3A"      # umber -- KPI values, headers
CARD_FILL = "F4EFE7"
CARD_BORDER = "E1D6C4"
LABEL_GRAY = "8A7F73"
MET_FILL, MET_FONT = "DCE7D2", "4B6142"
OPEN_FILL, OPEN_FONT = "F5E7C9", "8C6A22"
MID_FILL, MID_FONT = "F0CDAA", "994C00"
BREACH_FILL, BREACH_FONT = "F0DCD6", "8C4B3A"

REGIONS = [
    "Canada", "Caribbean", "Central Africa", "Central America", "Central Asia",
    "East Africa", "East of USA", "Eastern Asia", "Eastern Europe", "North Africa",
    "Northern Europe", "Oceania", "South America", "South Asia", "South of USA",
    "Southeast Asia", "Southern Africa", "Southern Europe", "US Center",
    "West Africa", "West Asia", "West of USA", "Western Europe",
]


def slug(region):
    return region.lower().replace(" ", "")


wb = openpyxl.Workbook()
header_fill = PatternFill("solid", fgColor=INK)
header_font = Font(color="FFFFFF", bold=True)
card_fill = PatternFill("solid", fgColor=CARD_FILL)
label_font = Font(size=10, color=LABEL_GRAY)
value_font = Font(size=20, bold=True, color=ACCENT)
thin = Side(style="thin", color=CARD_BORDER)
box_border = Border(left=thin, right=thin, top=thin, bottom=thin)

# ============================== Control ==============================
ws = wb.active
ws.title = "Control"
ws.sheet_view.showGridLines = False
ws["D2"] = "Shipment Ageing Report Automation"
ws["D2"].font = Font(size=16, bold=True, color=INK)
ws["D4"] = "Buttons are added to the right of this block once the macros are loaded."
ws["D4"].font = Font(size=9, italic=True, color=LABEL_GRAY)

# These exact cells (A2:B5) are what modRunDailyReport.bas writes to
# (Control!B2 = last run, B3 = exception lines, B4 = runtime, B5 = status)
# -- keep label/value cells aligned with the .bas files if this changes.
status_rows = [(2, "Last Run"), (3, "Exception Lines"), (4, "Runtime"), (5, "Status"), (6, "Error Detail")]
for row, lab in status_rows:
    ws.cell(row=row, column=1, value=lab).font = Font(bold=True, color=INK)
    ws.cell(row=row, column=2).font = Font(color=ACCENT, bold=True)
    for c in (1, 2):
        ws.cell(row=row, column=c).fill = card_fill
        ws.cell(row=row, column=c).border = box_border
ws.column_dimensions["A"].width = 18
ws.column_dimensions["B"].width = 20
ws.column_dimensions["C"].width = 3
ws.column_dimensions["D"].width = 36

# ============================== Settings ==============================
ws = wb.create_sheet("Settings")
ws.sheet_view.showGridLines = False
ws["A1"] = "SETTINGS"
ws["A1"].font = Font(size=14, bold=True, color=INK)

settings_rows = [
    (3, "Report Date", datetime.date(2018, 2, 6)),
    (4, "Lookback Days", 30),
    (6, "Excluded Order Statuses (comma, no spaces)", "CANCELED,SUSPECTED_FRAUD,COMPLETE,CLOSED"),
    (7, "Excluded Delivery Status", "Shipping canceled"),
    (9, "On-schedule max delay (days)", 0),
    (10, "Day-1 bucket max delay", 1),
    (11, "Day-2 bucket max delay", 2),
    (13, "Email Subject", "Daily Shipment Ageing Report"),
    (14, "Email Body", "Please find the pending last-mile shipments for your region. "
                        "We request you to proceed with these on priority."),
    (16, "Draft Emails on Run (Yes/No)", "No"),
]
for row, label, value in settings_rows:
    ws.cell(row=row, column=1, value=label).font = Font(color=INK)
    c = ws.cell(row=row, column=2, value=value)
    c.font = Font(bold=True, color=ACCENT)
    if isinstance(value, datetime.date):
        c.number_format = "yyyy-mm-dd"

ws["A17"] = "Region"
ws["B17"] = "Email"
for cell in ("A17", "B17"):
    ws[cell].font = header_font
    ws[cell].fill = header_fill
for i, region in enumerate(REGIONS, start=18):
    ws.cell(row=i, column=1, value=region)
    ws.cell(row=i, column=2, value=f"{slug(region)}@example.com")

ws.column_dimensions["A"].width = 44
ws.column_dimensions["B"].width = 40

# ============================== RawData ==============================
ws = wb.create_sheet("RawData")
ws["A1"] = "Populated by Run Daily Report / Re-import CSV. Safe to ignore between runs."
ws["A1"].font = Font(size=9, italic=True, color=LABEL_GRAY)

# ============================== Exceptions ==============================
ws = wb.create_sheet("Exceptions")
ws["A1"] = "Populated by Run Daily Report."
ws["A1"].font = Font(size=9, italic=True, color=LABEL_GRAY)

# ============================== Pivots ==============================
ws = wb.create_sheet("Pivots")
ws["A1"] = "Populated by Run Daily Report."
ws["A1"].font = Font(size=9, italic=True, color=LABEL_GRAY)

# ============================== Summary ==============================
ws = wb.create_sheet("Summary")
ws.sheet_view.showGridLines = False
ws["B2"] = "Shipment Ageing: Daily Summary"
ws["B2"].font = Font(size=16, bold=True, color=INK)

kpi_labels = ["Exception Lines", "% Late", "Average Delay (days)", "Share 3+ Days Late", "Top Region"]
kpi_formulas = [
    '=COUNTIFS(Exceptions!A2:A1048576,"<>")',
    '=IFERROR(COUNTIFS(Exceptions!R2:R1048576,"<>On schedule",Exceptions!A2:A1048576,"<>")/$B$5,0)',
    '=IFERROR(AVERAGEIFS(Exceptions!Q2:Q1048576,Exceptions!A2:A1048576,"<>"),0)',
    '=IFERROR(COUNTIFS(Exceptions!R2:R1048576,"3+ days late",Exceptions!A2:A1048576,"<>")/$B$5,0)',
    '=IFERROR(INDEX($N$5:$N$27,MATCH(MAX($O$5:$O$27),$O$5:$O$27,0)),"")',
]
kpi_fmt = [None, "0.0%", "0.00", "0.0%", None]

start_col = 2
for i, (label, formula, fmt) in enumerate(zip(kpi_labels, kpi_formulas, kpi_fmt)):
    col = start_col + i * 2
    col_l = get_column_letter(col)
    ws[f"{col_l}4"] = label
    ws[f"{col_l}4"].font = label_font
    val_cell = ws[f"{col_l}5"]
    val_cell.value = formula
    if fmt:
        val_cell.number_format = fmt
    val_cell.font = value_font
    for r in (4, 5, 6):
        ws.cell(row=r, column=col).fill = card_fill
        ws.cell(row=r, column=col).border = box_border
    ws.column_dimensions[col_l].width = 20
    ws.column_dimensions[get_column_letter(col + 1)].width = 8

# Top-Region helper table (hidden): region list + live count per region
ws["N4"] = "Region (helper)"
ws["O4"] = "Count"
for i, region in enumerate(REGIONS, start=5):
    ws.cell(row=i, column=14, value=f"=Settings!A{13 + i}")  # Settings!A18 -> Summary!N5, etc.
    ws.cell(row=i, column=15, value=f'=COUNTIFS(Exceptions!L2:L1048576,N{i},Exceptions!A2:A1048576,"<>")')
ws.column_dimensions["N"].hidden = True
ws.column_dimensions["O"].hidden = True

ws["B8"] = "Exception Lines, % Late and Share 3+ Days Late are live formulas against the " \
           "Exceptions sheet; they update the moment Run Daily Report finishes."
ws["B8"].font = Font(size=9, italic=True, color=LABEL_GRAY)

# ============================== Run Log ==============================
ws = wb.create_sheet("Run Log")
headers = ["Date Run", "Report Date", "Rows In", "Rows Out", "Seconds", "Drafts Created"]
ws.append(headers)
for col in range(1, len(headers) + 1):
    c = ws.cell(row=1, column=col)
    c.fill = header_fill
    c.font = header_font
widths = [20, 14, 10, 10, 10, 14]
for i, w in enumerate(widths, start=1):
    ws.column_dimensions[get_column_letter(i)].width = w

out_path = os.path.join(HERE, "Shipment_Ageing_Report_base.xlsx")
wb.save(out_path)
print("Saved", out_path)
