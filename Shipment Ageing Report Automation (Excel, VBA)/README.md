# Shipment Ageing Report Automation (Excel, VBA)

A one-click VBA macro that turns a 180,000-line supply chain export into
a filtered ageing report, region pivots, a KPI summary, a dated report
file, and (optionally) one Outlook email draft per region. Rebuilds the
daily last-mile ageing report automated at Flipkart (Ekart Logistics),
on a large public dataset so the method can be shown without company data.

## Business problem

A fraud/logistics team runs a daily report by hand: download the ERP
export, remove closed statuses, build pivots by region, and email the
pending list to hub teams. `RunDailyReport` does all of that in one
click, in under 15 seconds, on 180,000+ rows.

## Data

- Kaggle: DataCo Smart Supply Chain for Big Data Analysis (shashwatwork)
  https://www.kaggle.com/datasets/shashwatwork/dataco-smart-supply-chain-for-big-data-analysis
- File: `DataCoSupplyChainDataset.csv`, 180,519 rows x 53 columns, orders
  2015 to 2019, Latin-1 (cp1252) encoded
- The full CSV (~95 MB) isn't included here; `sample_data/` has the
  first 1,000 rows. Grab the full file from Kaggle to reproduce.

## Report logic

Since the data is historical, the Settings sheet has a **Report Date**
the macro treats as "today," plus a lookback window (default 30 days).

- **Scope**: shipping date inside the lookback window.
- **Excluded**: `CANCELED`, `SUSPECTED_FRAUD`, `COMPLETE`, `CLOSED` order
  statuses, and `Shipping canceled` delivery status.
- **Ageing bucket**: Delay Days (actual minus scheduled shipping days)
  bucketed into On schedule / 1 day late / 2 days late / 3+ days late.
- All of the above (status lists, lookback days, bucket limits, region
  email table) live on the **Settings** sheet, not in the code.

### A real bug caught before writing any code

The plan's original exception rule was "Delivery Status = Late delivery,
**OR** an open Order Status." Profiling the data first (as the plan
itself required) showed that **45,308 of 98,977 "Late delivery" rows
belong to orders already COMPLETE or CLOSED** — already resolved, no
action needed. The fix: `COMPLETE` and `CLOSED` belong on the excluded
list too (they're "closed" by the plan's own definition). With that one
change, a 30-day window ending at the last date in the data produces
977 exception lines with a believable spread (393 on schedule, 310 one
day late, 157 two days late, 94 three-plus days late) instead of 1,462
rows padded with already-closed orders. Full writeup: `Project Plan.md`.

## Tools used

- Excel VBA: `Workbooks.OpenText` with `Origin:=1252` for the encoding,
  array-based processing (not cell-by-cell) for speed on 180k+ rows,
  native PivotTables, Outlook automation via `.Display` (never `.Send`)
- Python (`pandas`) for upstream data profiling and verification only —
  the actual report pipeline is 100% VBA, nothing is pre-computed

## Verified run

| Metric | Value |
|---|---|
| Rows imported | 180,519 |
| Exception lines | 977 |
| Runtime | 13.4 seconds |
| % Late | 58.2% |
| Average delay | 0.66 days |
| Share 3+ days late | 9.7% |
| Top region by exception count | Southeast Asia |

## Workbook sheets

| Sheet | Purpose |
|---|---|
| Control | Run Daily Report / Re-import CSV / Draft Emails Only buttons, last run status |
| Settings | Report Date, lookback days, status lists, bucket limits, region-to-email table |
| RawData | Imported export (cleared and repopulated each import) |
| Exceptions | Filtered exception lines with Delay Days and Ageing Bucket, RAG conditional formatting |
| Pivots | Region x Ageing Bucket and Market x Shipping Mode (native PivotTables), plus a computed Top 10 Cities by Late Lines table |
| Summary | Live-formula KPI cards, colour-coded by severity |
| Run Log | One row per run: date, report date, rows in, rows out, seconds, drafts created |

## VBA modules (`vba/`)

- `modImportData` — file picker, `OpenText` with `Origin:=1252`, keeps
  only the 16 columns the report needs
- `modCleanAndFilter` — array-based filter against the Settings rules,
  writes Exceptions in one block
- `modBuildPivots` — the 2 native PivotTables + the computed top-cities
  table
- `modBuildSummary` — colours the KPI cards by severity threshold
- `modExportReport` — saves a values-only dated snapshot to `Reports/`
- `modDraftEmails` — one Outlook draft per region with pending lines,
  `.Display` only, never `.Send`
- `modRunDailyReport` — the master macro; also exposes `ReimportCsv` and
  `RunDraftEmailsOnly` as separate buttons

Two implementation details worth knowing if you read the code: `Workbooks.OpenText`'s
`xlSkipColumn` leaves a skipped column's position blank rather than
compacting the remaining columns (easy to get wrong, and I did on the
first pass — see the comment in `modImportData.bas`), and Form Control
buttons and PivotTables both turned out to interfere with
clipboard-based `CopyPicture` screenshot capture under headless
automation, which is a build-tooling quirk, not a workbook defect.

## How to run

1. Open `Shipment_Ageing_Report.xlsm`, enable macros.
2. Click **Run Daily Report**. First run prompts for the CSV (point it
   at `Data/DataCoSupplyChainDataset.csv`); later runs reuse the
   imported data until you click **Re-import CSV**.
3. To send the region emails, set `Settings!B16` to `Yes` (or click
   **Draft Emails Only**) — drafts open in Outlook for review, nothing
   is sent automatically.

## Files

| File | Purpose |
|---|---|
| `Shipment_Ageing_Report.xlsm` | The workbook |
| `vba/*.bas` | Each module's source, readable on GitHub |
| `sample_data/` | First 1,000 rows of the source CSV |
| `Reports/` | A sample dated report export from a verified run |
| `Project Plan.md` | Original plan plus the profiling results and filter-rule fix |
| `screenshots/` | Workbook views |

## Before and after

**Before**: download the export by hand, filter out closed statuses in
Excel, build 2-3 pivots manually, write up a KPI summary, save a dated
copy, draft an email per region.

**After**: one click, 13.4 seconds, same output, every rule
business-editable on the Settings sheet.
