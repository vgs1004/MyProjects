# RAID Log and Monthly Portfolio Review Tracker

An Excel RAID log (Risks, Assumptions, Issues, Dependencies) with a
monthly review summary: open-item counts by type and impact, and a
pre-filtered view of the items that need attention right now. Built to
mirror the governance artifact PMs live in day to day, in a fully
anonymized, synthetic form.

## What it is

- 55 synthetic RAID items spanning Risk, Assumption, Issue, and
  Dependency types, each with an owner, impact, likelihood, status, date
  raised, and mitigation/action.
- No real company data. All items, owners, and mitigation notes are
  generated (see `generate_data.py`).

## Tools used

- Excel (formulas, data validation, conditional formatting, native charts)
- Python (`openpyxl`) to generate the data and assemble the workbook
  programmatically. The script is included so the build is reproducible
  from scratch. Unlike the other two Excel projects in this portfolio,
  this one doesn't need PivotTables or Excel COM automation, so it's
  pure openpyxl.

## What it shows

**RAID Log sheet**
- Dropdown validation for Type, Impact, Likelihood, and Status.
- Conditional formatting (RAG) on Impact and Status.
- A whole-row highlight for any item that is both High impact and
  currently Open, the items a monthly review should focus on first.

**Monthly Review Summary sheet**
- KPI cards: Total Items, Open Items, Closed Items, High Impact Open,
  Percent Closed.
- Open Items by Type (bar chart) and Open Items by Impact (pie chart),
  both driven by live `COUNTIFS` formulas against the RAID Log.
- "Items Needing Attention" — a filtered, RAG-formatted list of every
  High impact item that is currently Open.

## Files

| File | Purpose |
|---|---|
| `RAID_Log_Portfolio_Review_Tracker.xlsx` | The finished workbook |
| `sample_raid_log_data.csv` | Standalone copy of the RAID Log sheet |
| `generate_data.py` | Generates the synthetic RAID items and builds both sheets, formulas, and charts |
| `screenshots/` | Dashboard and data views (since GitHub can't preview `.xlsx`) |

## Screenshots

- `dashboard_top.png`: KPI cards and the two summary charts
- `raid_log.png`: RAID log with RAG conditional formatting
- `attention_items.png`: the filtered High-impact/Open items list
