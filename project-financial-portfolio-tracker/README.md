# Project Financial and Portfolio Tracker

An Excel-based PMO tool for tracking a portfolio of projects: budget vs
actual spend, schedule and risk RAG status, resource utilization, and
monthly spend trend, all rolled into a PivotTable/PivotChart dashboard.
Built to mirror portfolio-health and finance-dashboard style reporting in
a fully anonymized, synthetic form.

## What it is

- 14 synthetic projects across 8 regions, each with a budget, actual
  spend, schedule status (Green/Amber/Red), and risk level (Low/Medium/High).
- A resource timesheet log (10 resources, ~90 monthly assignment rows)
  with planned vs booked hours.
- A monthly spend breakdown per project, used to drive the trend chart.
- No real company data. All project names, regions, spend figures, and
  resource names are generated (see `generate_data.py`).

## Tools used

- Excel (formulas, data validation, conditional formatting, native
  PivotTables/PivotCharts, slicers)
- Python (`openpyxl`, `pywin32`) to generate the data and assemble the
  workbook programmatically. Scripts are included so the build is
  reproducible from scratch.

## What it shows

**Projects sheet**
- `Variance` and `PercentSpent` computed live from Budget and ActualSpend.
- RAG conditional formatting on ScheduleStatus (Green/Amber/Red) and
  RiskLevel (Low/Medium/High).

**Resources sheet**
- Planned vs booked hours per resource per month, with a computed
  `Utilization` column and conditional formatting flagging over- and
  under-booked months.

**MonthlySpend sheet**
- Each project's actual spend broken out by month, feeding the trend chart.

**Dashboard sheet**
- KPI cards: Total Budget, Total Actual Spend, Portfolio % Spent, Red
  Project count, Average Utilization.
- Four PivotCharts: Spend vs Budget by Project, RAG Summary by Schedule
  Status, Utilization by Resource, and Monthly Spend Trend.
- Region and Risk Level slicers that cross-filter the charts.
- The native PivotTables backing each chart are included below the
  charts for transparency.

## Files

| File | Purpose |
|---|---|
| `Project_Financial_Portfolio_Tracker.xlsx` | The finished workbook |
| `sample_projects_data.csv` | Standalone copy of the Projects sheet |
| `sample_resources_data.csv` | Standalone copy of the Resources sheet |
| `sample_monthlyspend_data.csv` | Standalone copy of the MonthlySpend sheet |
| `generate_data.py` | Generates the synthetic data and builds the Projects/Resources/MonthlySpend/KPI layout |
| `build_dashboard.py` | Adds the native PivotTables, PivotCharts, and slicers via Excel automation |
| `screenshots/` | Dashboard and data views (since GitHub can't preview `.xlsx`) |

## Screenshots

- `01_dashboard_overview.png`: KPI cards and the four PivotCharts
- `02_projects_sheet.png`: project list with budget, variance, and RAG formatting
