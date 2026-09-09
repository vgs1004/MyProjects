"""
Generate synthetic project portfolio / financial data and build the
Projects, Resources, and MonthlySpend sheets (raw data + formulas +
validation + conditional formatting) with openpyxl. The Dashboard sheet
(pivots/charts/slicers) is added afterwards via COM in build_dashboard.py.
"""
import random
import sys
from datetime import date, timedelta
import calendar

import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.formatting.rule import CellIsRule
from openpyxl.utils import get_column_letter

sys.path.insert(0, r"C:\Users\varsh\Projects\Portfolio\_shared")
import palette as pal

random.seed(7)

REGIONS = ["India", "United Kingdom", "Germany", "United States", "Brazil",
           "Singapore", "United Arab Emirates", "South Africa"]
PMS = ["A. Mehta", "R. Fernandes", "S. Iyer", "K. Padilla", "J. Ncube",
       "L. Duarte", "P. Osei", "M. Choudhury"]
PROJECT_THEMES = [
    "Core Banking Migration", "Claims Automation", "Data Warehouse Modernization",
    "Customer Portal Revamp", "Regulatory Reporting Upgrade", "ERP Rollout",
    "Payments Platform Refresh", "HR System Consolidation", "Cloud Cost Optimization",
    "Fraud Detection Enhancement", "Supply Chain Visibility", "Digital Onboarding",
    "Master Data Governance", "Network Resilience Program", "Analytics Center of Excellence",
]
SCHEDULE_STATUS = ["Green", "Amber", "Red"]
SCHEDULE_WEIGHTS = [0.55, 0.30, 0.15]
RISK_LEVELS = ["Low", "Medium", "High"]
RISK_WEIGHTS = [0.45, 0.4, 0.15]

N_PROJECTS = 14
BASE_START = date(2025, 1, 1)

# ---------- Projects sheet ----------
projects = []
for i in range(1, N_PROJECTS + 1):
    pid = f"PRJ-{i:03d}"
    name = PROJECT_THEMES[i - 1]
    region = random.choice(REGIONS)
    pm = random.choice(PMS)
    start = BASE_START + timedelta(days=random.randint(0, 150))
    duration_months = random.randint(3, 11)
    end_year = start.year + (start.month - 1 + duration_months) // 12
    end_month = (start.month - 1 + duration_months) % 12 + 1
    end_day = min(start.day, calendar.monthrange(end_year, end_month)[1])
    end = date(end_year, end_month, end_day)
    budget = random.randint(80, 950) * 1000
    spend_ratio = random.uniform(0.55, 1.25)
    actual_spend = round(budget * spend_ratio, -2)
    schedule = random.choices(SCHEDULE_STATUS, weights=SCHEDULE_WEIGHTS)[0]
    risk = random.choices(RISK_LEVELS, weights=RISK_WEIGHTS)[0]
    projects.append({
        "id": pid, "name": name, "region": region, "pm": pm,
        "start": start, "end": end, "budget": budget, "actual": actual_spend,
        "schedule": schedule, "risk": risk,
    })

wb = openpyxl.Workbook()
ws = wb.active
ws.title = "Projects"

headers = ["ProjectID", "ProjectName", "Region", "PM", "StartDate", "EndDate",
           "Budget", "ActualSpend", "Variance", "PercentSpent",
           "ScheduleStatus", "RiskLevel"]
ws.append(headers)

header_fill = PatternFill("solid", fgColor=pal.INK)
header_font = Font(color="FFFFFF", bold=True)
for col in range(1, len(headers) + 1):
    c = ws.cell(row=1, column=col)
    c.fill = header_fill
    c.font = header_font
    c.alignment = Alignment(horizontal="center", vertical="center")

for r, p in enumerate(projects, start=2):
    ws.cell(row=r, column=1, value=p["id"])
    ws.cell(row=r, column=2, value=p["name"])
    ws.cell(row=r, column=3, value=p["region"])
    ws.cell(row=r, column=4, value=p["pm"])
    ws.cell(row=r, column=5, value=p["start"]).number_format = "yyyy-mm-dd"
    ws.cell(row=r, column=6, value=p["end"]).number_format = "yyyy-mm-dd"
    ws.cell(row=r, column=7, value=p["budget"]).number_format = '#,##0,"K"'
    ws.cell(row=r, column=8, value=p["actual"]).number_format = '#,##0,"K"'
    ws.cell(row=r, column=9, value=f"=G{r}-H{r}").number_format = '#,##0,"K"'
    ws.cell(row=r, column=10, value=f"=H{r}/G{r}").number_format = "0.0%"
    ws.cell(row=r, column=11, value=p["schedule"])
    ws.cell(row=r, column=12, value=p["risk"])

widths = [10, 30, 20, 14, 12, 12, 12, 13, 12, 12, 14, 10]
for i, w in enumerate(widths, start=1):
    ws.column_dimensions[get_column_letter(i)].width = w

last_row = N_PROJECTS + 1

dv_schedule = DataValidation(type="list", formula1='"Green,Amber,Red"', allow_blank=False)
dv_risk = DataValidation(type="list", formula1='"Low,Medium,High"', allow_blank=False)
for dv in (dv_schedule, dv_risk):
    ws.add_data_validation(dv)
dv_schedule.add(f"K2:K{last_row}")
dv_risk.add(f"L2:L{last_row}")

green_fill = PatternFill("solid", fgColor=pal.MET_FILL)
green_font = Font(color=pal.MET_FONT)
red_fill = PatternFill("solid", fgColor=pal.BREACH_FILL)
red_font = Font(color=pal.BREACH_FONT)
amber_fill = PatternFill("solid", fgColor=pal.OPEN_FILL)
amber_font = Font(color=pal.OPEN_FONT)

rag_rng = f"K2:K{last_row}"
ws.conditional_formatting.add(rag_rng, CellIsRule(operator="equal", formula=['"Green"'], fill=green_fill, font=green_font))
ws.conditional_formatting.add(rag_rng, CellIsRule(operator="equal", formula=['"Red"'], fill=red_fill, font=red_font))
ws.conditional_formatting.add(rag_rng, CellIsRule(operator="equal", formula=['"Amber"'], fill=amber_fill, font=amber_font))

risk_rng = f"L2:L{last_row}"
ws.conditional_formatting.add(risk_rng, CellIsRule(operator="equal", formula=['"High"'], fill=red_fill, font=red_font))
ws.conditional_formatting.add(risk_rng, CellIsRule(operator="equal", formula=['"Medium"'], fill=amber_fill, font=amber_font))
ws.conditional_formatting.add(risk_rng, CellIsRule(operator="equal", formula=['"Low"'], fill=green_fill, font=green_font))

ws.freeze_panes = "A2"
ws.auto_filter.ref = f"A1:L{last_row}"

# ---------- Resources / Timesheets sheet ----------
ws2 = wb.create_sheet("Resources")
res_headers = ["Resource", "Project", "Month", "PlannedHours", "BookedHours", "Utilization"]
ws2.append(res_headers)
for col in range(1, len(res_headers) + 1):
    c = ws2.cell(row=1, column=col)
    c.fill = header_fill
    c.font = header_font
    c.alignment = Alignment(horizontal="center", vertical="center")

RESOURCES = ["N. Kowalski", "T. Alvarez", "M. Choudhury", "J. Ncube", "S. Iyer",
             "P. Osei", "K. Padilla", "L. Duarte", "A. Mehta", "R. Fernandes"]

res_rows = []
for resource in RESOURCES:
    assigned_projects = random.sample(projects, k=random.randint(2, 4))
    for p in assigned_projects:
        n_months = random.randint(2, 5)
        start_month = p["start"].replace(day=1)
        for m in range(n_months):
            month_num = start_month.month - 1 + m
            year = start_month.year + month_num // 12
            month = month_num % 12 + 1
            month_date = date(year, month, 1)
            planned = random.choice([40, 60, 80, 100, 120, 160])
            booked = round(planned * random.uniform(0.6, 1.25))
            res_rows.append((resource, p["name"], month_date, planned, booked))

for r, (resource, proj, month_date, planned, booked) in enumerate(res_rows, start=2):
    ws2.cell(row=r, column=1, value=resource)
    ws2.cell(row=r, column=2, value=proj)
    ws2.cell(row=r, column=3, value=month_date).number_format = "mmm-yyyy"
    ws2.cell(row=r, column=4, value=planned)
    ws2.cell(row=r, column=5, value=booked)
    ws2.cell(row=r, column=6, value=f"=E{r}/D{r}").number_format = "0.0%"

res_last_row = len(res_rows) + 1
res_widths = [16, 30, 12, 14, 14, 12]
for i, w in enumerate(res_widths, start=1):
    ws2.column_dimensions[get_column_letter(i)].width = w
ws2.freeze_panes = "A2"
ws2.auto_filter.ref = f"A1:F{res_last_row}"

util_rng = f"F2:F{res_last_row}"
ws2.conditional_formatting.add(util_rng, CellIsRule(operator="greaterThan", formula=["1.1"], fill=red_fill, font=red_font))
ws2.conditional_formatting.add(util_rng, CellIsRule(operator="between", formula=["0.85", "1.1"], fill=green_fill, font=green_font))
ws2.conditional_formatting.add(util_rng, CellIsRule(operator="lessThan", formula=["0.85"], fill=amber_fill, font=amber_font))

# ---------- MonthlySpend sheet (feeds the "monthly spend trend" chart) ----------
ws3 = wb.create_sheet("MonthlySpend")
ms_headers = ["ProjectID", "ProjectName", "Month", "ActualSpendThatMonth"]
ws3.append(ms_headers)
for col in range(1, len(ms_headers) + 1):
    c = ws3.cell(row=1, column=col)
    c.fill = header_fill
    c.font = header_font
    c.alignment = Alignment(horizontal="center", vertical="center")

ms_rows = []
for p in projects:
    start_month = p["start"].replace(day=1)
    end_month = p["end"].replace(day=1)
    months = []
    cur = start_month
    while cur <= end_month:
        months.append(cur)
        month_num = cur.month - 1 + 1
        year = cur.year + month_num // 12
        month = month_num % 12 + 1
        cur = date(year, month, 1)
    if not months:
        months = [start_month]
    # Distribute actual spend across months with some randomness, summing back to actual.
    weights = [random.uniform(0.5, 1.5) for _ in months]
    total_w = sum(weights)
    for month_date, w in zip(months, weights):
        amount = round(p["actual"] * (w / total_w), -1)
        ms_rows.append((p["id"], p["name"], month_date, amount))

for r, (pid, name, month_date, amount) in enumerate(ms_rows, start=2):
    ws3.cell(row=r, column=1, value=pid)
    ws3.cell(row=r, column=2, value=name)
    ws3.cell(row=r, column=3, value=month_date).number_format = "mmm-yyyy"
    ws3.cell(row=r, column=4, value=amount).number_format = '#,##0,"K"'

ms_last_row = len(ms_rows) + 1
for i, w in enumerate([10, 30, 12, 18], start=1):
    ws3.column_dimensions[get_column_letter(i)].width = w
ws3.freeze_panes = "A2"
ws3.auto_filter.ref = f"A1:D{ms_last_row}"

# ---------- Dashboard sheet: title + KPI cards ----------
dash = wb.create_sheet("Dashboard")
dash.sheet_view.showGridLines = False

dash["B2"] = "Project Financial and Portfolio Tracker: Dashboard"
dash["B2"].font = Font(size=16, bold=True, color=pal.INK)

kpi_labels = ["Total Budget", "Total Actual Spend", "Portfolio % Spent", "Red Projects", "Avg Utilization"]
kpi_formulas = [
    f"=SUM(Projects!G2:G{last_row})",
    f"=SUM(Projects!H2:H{last_row})",
    f"=SUM(Projects!H2:H{last_row})/SUM(Projects!G2:G{last_row})",
    f'=COUNTIF(Projects!K2:K{last_row},"Red")',
    f"=AVERAGE(Resources!F2:F{res_last_row})",
]
# $M-scale format for the two large aggregate sums -- sidesteps Windows
# regional settings (e.g. Indian digit grouping) rendering large numbers
# ambiguously; individual project-level amounts stay under 1M so they're
# unaffected either way.
kpi_fmt = ['0.0,,"M"', '0.0,,"M"', "0.0%", None, "0.0%"]

card_fill = PatternFill("solid", fgColor=pal.CARD_FILL)
label_font = Font(size=10, color=pal.LABEL_GRAY)
value_font = Font(size=20, bold=True, color=pal.FIN_PRIMARY)
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

dash["B8"] = "Charts above are PivotCharts with Region and RiskLevel slicers. Supporting PivotTables are below."
dash["B8"].font = Font(size=9, italic=True, color=pal.LABEL_GRAY)

out_path = r"C:\Users\varsh\Projects\Portfolio\03-project-financial-portfolio-tracker-excel\Project_Financial_Portfolio_Tracker.xlsx"
wb.save(out_path)
print("Saved", out_path, "projects:", N_PROJECTS, "resource rows:", len(res_rows), "monthly spend rows:", len(ms_rows))
