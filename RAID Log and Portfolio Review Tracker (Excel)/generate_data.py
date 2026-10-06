"""
Generate a synthetic RAID log and build the RAID Log + Monthly Review
Summary sheets entirely with openpyxl (formulas + native charts -- no
Excel COM automation needed for this one, since the brief doesn't call
for PivotTables/slicers here).
"""
import random
import sys
from datetime import date, timedelta

import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.formatting.rule import CellIsRule, FormulaRule
from openpyxl.utils import get_column_letter
from openpyxl.chart import BarChart, PieChart, Reference

sys.path.insert(0, r"C:\Users\varsh\Projects\Portfolio\_shared")
import palette as pal

random.seed(21)

TYPES = ["Risk", "Assumption", "Issue", "Dependency"]
TYPE_WEIGHTS = [0.35, 0.15, 0.30, 0.20]
IMPACT_LEVELS = ["High", "Medium", "Low"]
IMPACT_WEIGHTS = [0.25, 0.45, 0.30]
LIKELIHOOD_LEVELS = ["High", "Medium", "Low"]
LIKELIHOOD_WEIGHTS = [0.25, 0.45, 0.30]
OWNERS = ["A. Mehta", "R. Fernandes", "S. Iyer", "K. Padilla", "J. Ncube",
          "L. Duarte", "P. Osei", "M. Choudhury", "T. Alvarez", "N. Kowalski"]

SUBJECTS = [
    "third-party API integration", "regional data center migration", "customer authentication flow",
    "vendor SLA renewal", "legacy database decommission", "cross-border data residency",
    "peak-season load testing", "single sign-on rollout", "core banking cutover window",
    "payment gateway certification", "regulatory reporting deadline", "staff augmentation ramp-up",
    "disaster recovery failover test", "master data cleanup", "network firewall upgrade",
    "mobile app store approval", "translation and localization", "change freeze period",
    "budget approval for Phase 2", "key resource availability",
]

TEMPLATES = {
    "Risk": [
        "Possible delay to {s} due to resourcing constraints",
        "{s} may slip past the committed date without an earlier decision point",
        "Insufficient testing window identified for {s}",
        "Budget overrun risk on {s} if scope is not controlled",
    ],
    "Issue": [
        "{s} is currently blocked pending vendor response",
        "Defects found during {s} are delaying sign-off",
        "{s} has missed its planned milestone",
        "Data quality problems surfaced during {s}",
    ],
    "Assumption": [
        "Assuming {s} completes on the vendor's published timeline",
        "Plan assumes no additional approvals are needed for {s}",
        "Assuming current staffing levels hold through {s}",
    ],
    "Dependency": [
        "{s} depends on a sign-off from a separate workstream",
        "{s} is blocked on infrastructure provisioning from IT Ops",
        "{s} cannot start until the upstream contract is signed",
    ],
}

MITIGATION = {
    "Risk": [
        "Added buffer to the schedule and flagged to steering committee",
        "Escalated to sponsor for an early go/no-go decision",
        "Contingency budget reserved; reviewing weekly",
    ],
    "Issue": [
        "Vendor engaged with a 48-hour response SLA",
        "Fix scheduled for next release; workaround in place",
        "Root cause under investigation with the platform team",
    ],
    "Assumption": [
        "Validated with vendor in writing",
        "To be reconfirmed at next steering committee",
        "Monitoring for change; no action needed yet",
    ],
    "Dependency": [
        "Tracking with the owning workstream lead weekly",
        "Escalated to PMO for cross-team prioritization",
        "Contract finance team engaged to expedite",
    ],
}

N = 55
BASE_DATE = date(2025, 1, 1)

items = []
for i in range(1, N + 1):
    item_id = f"RAID-{i:03d}"
    itype = random.choices(TYPES, weights=TYPE_WEIGHTS)[0]
    subject = random.choice(SUBJECTS)
    description = random.choice(TEMPLATES[itype]).format(s=subject)
    owner = random.choice(OWNERS)
    impact = random.choices(IMPACT_LEVELS, weights=IMPACT_WEIGHTS)[0]
    likelihood = random.choices(LIKELIHOOD_LEVELS, weights=LIKELIHOOD_WEIGHTS)[0]
    date_raised = BASE_DATE + timedelta(days=random.randint(0, 300))
    # Older items are more likely closed
    days_old = (date(2025, 10, 27) - date_raised).days
    close_chance = min(0.85, max(0.15, days_old / 300))
    status = "Closed" if random.random() < close_chance else "Open"
    mitigation = random.choice(MITIGATION[itype])
    items.append({
        "id": item_id, "type": itype, "description": description, "owner": owner,
        "impact": impact, "likelihood": likelihood, "status": status,
        "date_raised": date_raised, "mitigation": mitigation,
    })

wb = openpyxl.Workbook()
ws = wb.active
ws.title = "RAID Log"

headers = ["ID", "Type", "Description", "Owner", "Impact", "Likelihood",
           "Status", "DateRaised", "Mitigation / Action"]
ws.append(headers)

header_fill = PatternFill("solid", fgColor=pal.INK)
header_font = Font(color="FFFFFF", bold=True)
for col in range(1, len(headers) + 1):
    c = ws.cell(row=1, column=col)
    c.fill = header_fill
    c.font = header_font
    c.alignment = Alignment(horizontal="center", vertical="center")

for r, it in enumerate(items, start=2):
    ws.cell(row=r, column=1, value=it["id"])
    ws.cell(row=r, column=2, value=it["type"])
    ws.cell(row=r, column=3, value=it["description"])
    ws.cell(row=r, column=4, value=it["owner"])
    ws.cell(row=r, column=5, value=it["impact"])
    ws.cell(row=r, column=6, value=it["likelihood"])
    ws.cell(row=r, column=7, value=it["status"])
    ws.cell(row=r, column=8, value=it["date_raised"]).number_format = "yyyy-mm-dd"
    ws.cell(row=r, column=9, value=it["mitigation"])
    ws.cell(row=r, column=3).alignment = Alignment(wrap_text=False)
    ws.cell(row=r, column=9).alignment = Alignment(wrap_text=False)

widths = [10, 12, 46, 14, 9, 11, 9, 12, 42]
for i, w in enumerate(widths, start=1):
    ws.column_dimensions[get_column_letter(i)].width = w

last_row = N + 1

dv_type = DataValidation(type="list", formula1='"Risk,Assumption,Issue,Dependency"', allow_blank=False)
dv_level = DataValidation(type="list", formula1='"High,Medium,Low"', allow_blank=False)
dv_status = DataValidation(type="list", formula1='"Open,Closed"', allow_blank=False)
for dv in (dv_type, dv_level, dv_status):
    ws.add_data_validation(dv)
dv_type.add(f"B2:B{last_row}")
dv_level.add(f"E2:E{last_row}")
dv_level.add(f"F2:F{last_row}")
dv_status.add(f"G2:G{last_row}")

green_fill = PatternFill("solid", fgColor=pal.MET_FILL)
green_font = Font(color=pal.MET_FONT)
red_fill = PatternFill("solid", fgColor=pal.BREACH_FILL)
red_font = Font(color=pal.BREACH_FONT)
amber_fill = PatternFill("solid", fgColor=pal.OPEN_FILL)
amber_font = Font(color=pal.OPEN_FONT)

impact_rng = f"E2:E{last_row}"
ws.conditional_formatting.add(impact_rng, CellIsRule(operator="equal", formula=['"High"'], fill=red_fill, font=red_font))
ws.conditional_formatting.add(impact_rng, CellIsRule(operator="equal", formula=['"Medium"'], fill=amber_fill, font=amber_font))
ws.conditional_formatting.add(impact_rng, CellIsRule(operator="equal", formula=['"Low"'], fill=green_fill, font=green_font))

status_rng = f"G2:G{last_row}"
ws.conditional_formatting.add(status_rng, CellIsRule(operator="equal", formula=['"Open"'], fill=amber_fill, font=amber_font))
ws.conditional_formatting.add(status_rng, CellIsRule(operator="equal", formula=['"Closed"'], fill=green_fill, font=green_font))

# Whole-row highlight for High impact + Open (the items needing attention)
attention_font = Font(color=pal.BREACH_FONT, bold=True)
attention_fill = PatternFill("solid", fgColor=pal.BREACH_FILL)
ws.conditional_formatting.add(
    f"A2:I{last_row}",
    FormulaRule(formula=[f'AND($E2="High",$G2="Open")'], fill=attention_fill, font=attention_font),
)

ws.freeze_panes = "A2"
ws.auto_filter.ref = f"A1:I{last_row}"

# ---------- Monthly Review Summary sheet ----------
dash = wb.create_sheet("Monthly Review Summary")
dash.sheet_view.showGridLines = False

dash["B2"] = "RAID Log: Monthly Review Summary"
dash["B2"].font = Font(size=16, bold=True, color=pal.INK)

kpi_labels = ["Total Items", "Open Items", "Closed Items", "High Impact Open", "Percent Closed"]
kpi_formulas = [
    f"=COUNTA('RAID Log'!A2:A{last_row})",
    f'=COUNTIF(\'RAID Log\'!G2:G{last_row},"Open")',
    f'=COUNTIF(\'RAID Log\'!G2:G{last_row},"Closed")',
    f'=COUNTIFS(\'RAID Log\'!E2:E{last_row},"High",\'RAID Log\'!G2:G{last_row},"Open")',
    f'=COUNTIF(\'RAID Log\'!G2:G{last_row},"Closed")/COUNTA(\'RAID Log\'!A2:A{last_row})',
]
kpi_fmt = [None, None, None, None, "0.0%"]

card_fill = PatternFill("solid", fgColor=pal.CARD_FILL)
label_font = Font(size=10, color=pal.LABEL_GRAY)
value_font = Font(size=20, bold=True, color=pal.RAID_PRIMARY)
thin = Side(style="thin", color=pal.CARD_BORDER)
box_border = Border(left=thin, right=thin, top=thin, bottom=thin)

card_col_width = 20
spacer_col_width = 8
start_col = 2

for i, (label, formula, fmt) in enumerate(zip(kpi_labels, kpi_formulas, kpi_fmt)):
    col = start_col + i * 2
    col_l = get_column_letter(col)
    lbl_cell = dash[f"{col_l}4"]
    lbl_cell.value = label
    lbl_cell.font = label_font
    lbl_cell.alignment = Alignment(horizontal="left", vertical="center")
    val_cell = dash[f"{col_l}5"]
    val_cell.value = formula
    if fmt:
        val_cell.number_format = fmt
    val_cell.font = value_font
    val_cell.alignment = Alignment(horizontal="left", vertical="center")
    for r in (4, 5, 6):
        dash.cell(row=r, column=col).fill = card_fill
        dash.cell(row=r, column=col).border = box_border
    dash.row_dimensions[6].height = 6

dash.column_dimensions["A"].width = 2
for i in range(5):
    col = start_col + i * 2
    dash.column_dimensions[get_column_letter(col)].width = card_col_width
    dash.column_dimensions[get_column_letter(col + 1)].width = spacer_col_width

# ---- Open items by Type (formula table + bar chart) ----
dash["B8"] = "Open Items by Type"
dash["B8"].font = Font(size=12, bold=True, color=pal.INK)
dash["B9"] = "Type"
dash["C9"] = "Open Count"
for c in ("B9", "C9"):
    dash[c].font = Font(bold=True, color=pal.INK)
    dash[c].fill = PatternFill("solid", fgColor=pal.CARD_FILL)
for i, t in enumerate(TYPES, start=10):
    dash.cell(row=i, column=2, value=t)
    dash.cell(row=i, column=3,
              value=f'=COUNTIFS(\'RAID Log\'!$B$2:$B${last_row},B{i},\'RAID Log\'!$G$2:$G${last_row},"Open")')

# ---- Open items by Impact (formula table + pie chart) ----
dash["F8"] = "Open Items by Impact"
dash["F8"].font = Font(size=12, bold=True, color=pal.INK)
dash["F9"] = "Impact"
dash["G9"] = "Open Count"
for c in ("F9", "G9"):
    dash[c].font = Font(bold=True, color=pal.INK)
    dash[c].fill = PatternFill("solid", fgColor=pal.CARD_FILL)
for i, lvl in enumerate(IMPACT_LEVELS, start=10):
    dash.cell(row=i, column=6, value=lvl)
    dash.cell(row=i, column=7,
              value=f'=COUNTIFS(\'RAID Log\'!$E$2:$E${last_row},F{i},\'RAID Log\'!$G$2:$G${last_row},"Open")')

# Bar chart: Open items by Type
bar = BarChart()
bar.type = "col"
bar.title = "Open Items by Type"
bar.y_axis.title = None
bar.x_axis.title = None
bar.legend = None
bar.y_axis.delete = False
bar.x_axis.delete = False
bar.y_axis.numFmt = "0"
bar.y_axis.majorTickMark = "out"
bar.x_axis.majorTickMark = "out"
data = Reference(dash, min_col=3, min_row=9, max_row=9 + len(TYPES))
cats = Reference(dash, min_col=2, min_row=10, max_row=9 + len(TYPES))
bar.add_data(data, titles_from_data=True)
bar.set_categories(cats)
bar.series[0].graphicalProperties.solidFill = pal.RAID_PRIMARY
bar.width, bar.height = 12, 8
dash.add_chart(bar, "B15")

# Pie chart: Open items by Impact
pie = PieChart()
pie.title = "Open Items by Impact"
data2 = Reference(dash, min_col=7, min_row=9, max_row=9 + len(IMPACT_LEVELS))
cats2 = Reference(dash, min_col=6, min_row=10, max_row=9 + len(IMPACT_LEVELS))
pie.add_data(data2, titles_from_data=True)
pie.set_categories(cats2)
# High, Medium, Low -> semantic RAG colors
from openpyxl.chart.marker import DataPoint
pie.series[0].data_points = [
    DataPoint(idx=0, spPr=None), DataPoint(idx=1, spPr=None), DataPoint(idx=2, spPr=None),
]
slice_colors = [pal.BREACH_FONT, pal.OPEN_FONT, pal.MET_FONT]
for idx, color in enumerate(slice_colors):
    pt = pie.series[0].data_points[idx]
    pt.graphicalProperties.solidFill = color
pie.width, pie.height = 12, 8
dash.add_chart(pie, "F15")

# ---- Items needing attention this month (High impact + Open), precomputed ----
dash["B33"] = "Items Needing Attention (High Impact, Currently Open)"
dash["B33"].font = Font(size=12, bold=True, color=pal.INK)

attn_headers = ["ID", "Type", "Owner", "Description", "Mitigation / Action"]
for j, h in enumerate(attn_headers):
    c = dash.cell(row=34, column=2 + j, value=h)
    c.font = Font(bold=True, color="FFFFFF")
    c.fill = PatternFill("solid", fgColor=pal.INK)

attention_items = [it for it in items if it["impact"] == "High" and it["status"] == "Open"]
for r, it in enumerate(attention_items, start=35):
    dash.cell(row=r, column=2, value=it["id"])
    dash.cell(row=r, column=3, value=it["type"])
    dash.cell(row=r, column=4, value=it["owner"])
    dash.cell(row=r, column=5, value=it["description"])
    dash.cell(row=r, column=6, value=it["mitigation"])
    for col in range(2, 7):
        dash.cell(row=r, column=col).fill = PatternFill("solid", fgColor=pal.BREACH_FILL)
        dash.cell(row=r, column=col).font = Font(color=pal.BREACH_FONT)

dash.column_dimensions["D"].width = 14
dash.column_dimensions["E"].width = 46
dash.column_dimensions["F"].width = 8
dash.column_dimensions["G"].width = 42

dash["B4"].alignment = Alignment(horizontal="left")  # no-op, keeps title row untouched

out_path = r"C:\Users\varsh\Projects\Portfolio\04-raid-log-portfolio-review-excel\RAID_Log_Portfolio_Review_Tracker.xlsx"
wb.save(out_path)
print("Saved", out_path, "items:", N, "attention items:", len(attention_items))
