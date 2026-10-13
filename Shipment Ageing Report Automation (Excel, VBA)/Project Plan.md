# Shipment Ageing Report Automation (Excel, VBA): Project Plan

## 1. The story
At Flipkart (Ekart Logistics) I produced a daily ageing report on last-mile externalization shipments: download the ERP data, remove closed statuses, build pivots by region and zone, and email the pending list to the hub teams. I automated it with an Excel VBA macro. This project rebuilds that automation on a large public supply chain dataset, so the method can be shown without company data.

**One button ("Run Daily Report") turns a raw export of 180,000+ order lines into a filtered ageing report, region pivots, a KPI summary, a dated report file and one email draft per region.**

## 2. Data
- Kaggle: DataCo Smart Supply Chain for Big Data Analysis (shashwatwork)
  https://www.kaggle.com/datasets/shashwatwork/dataco-smart-supply-chain-for-big-data-analysis
- File: `DataCoSupplyChainDataset.csv`, 180,519 rows x 53 columns, orders 2015 to 2019
- Encoding is Latin-1, not UTF-8. In Excel import choose "1252: Western European", in VBA use `Origin:=1252`.
- Save it in `Job Search\05 Projects\Shipment Ageing Report Automation (Excel, VBA)\Data\`

Columns used (about 16 of 53):
Order Id, Order Item Id, order date (DateOrders), shipping date (DateOrders), Days for shipping (real), Days for shipment (scheduled), Delivery Status, Late_delivery_risk, Order Status, Shipping Mode, Market, Order Region, Order Country, Order City, Category Name, Sales.

**First step in the build chat: load the file and list the exact values of Delivery Status and Order Status, then confirm the filter rules below before writing the macro.**

## 3. Report logic
The data is historical, so the user sets a **Report Date** on the Settings sheet and the macro treats it as "today".

- **Scope:** order lines with a shipping date in the lookback window before the Report Date (default 30 days).
- **Exclude (closed or not relevant):** Order Status CANCELED and SUSPECTED_FRAUD, Delivery Status "Shipping canceled".
- **Exception (goes on the report):** Delivery Status "Late delivery", or an open Order Status (for example PENDING, PROCESSING, ON_HOLD, PENDING_PAYMENT, PAYMENT_REVIEW).
- **Delay Days** = Days for shipping (real) minus Days for shipment (scheduled).
- **Ageing Bucket:** On schedule, 1 day late, 2 days late, 3+ days late.
- All rules (excluded statuses, open statuses, lookback, bucket limits) live on the Settings sheet, not in the code, so a business user can change them.

## 4. Workbook layout (`Shipment_Ageing_Report.xlsm`)
| Sheet | Purpose |
|---|---|
| Control | "Run Daily Report" button, last run time, rows processed, runtime |
| Settings | Report Date, lookback days, status lists, bucket limits, region to email table (dummy addresses) |
| RawData | Imported export (cleared each run) |
| Exceptions | Filtered exception lines with Delay Days and Ageing Bucket, conditional formatting by bucket |
| Pivots | Region x Ageing Bucket, Market x Shipping Mode, top 10 cities by late lines |
| Summary | KPI cards: exception lines, % late, average delay, share 3+ days late, top region |
| Run Log | One row per run: date, report date, rows in, rows out, seconds |

## 5. VBA modules
1. `ImportData`: file picker, imports the CSV with `Origin:=1252`, keeps only the needed columns.
2. `CleanAndFilter`: reads data into arrays (not cell by cell, for speed on 180k rows), applies the Settings rules, adds Delay Days and Ageing Bucket, writes the Exceptions sheet in one block.
3. `BuildPivots`: rebuilds the three PivotTables from the Exceptions table.
4. `BuildSummary`: fills the KPI cards and applies conditional formatting.
5. `ExportReport`: saves a values-only copy as `Reports\Shipment_Ageing_Report_YYYY-MM-DD.xlsx`.
6. `DraftEmails`: for each region, filters its exceptions to a small attachment and creates an Outlook draft with `.Display` (never `.Send`), using the email text from Settings: "Please find the pending last-mile shipments for your region. We request you to proceed with these on priority."
7. `RunDailyReport`: master macro calling 1 to 6, with `Application.ScreenUpdating = False`, `Calculation = xlCalculationManual`, error handling, and a Run Log entry.

Target: full run on 180,000+ rows in under 30 seconds.

## 6. GitHub deliverables
Folder `Shipment Ageing Report Automation (Excel, VBA)` in MyProjects:
- `Shipment_Ageing_Report.xlsm`
- `vba/` with each module exported as `.bas` (so the code is readable on GitHub)
- `sample_data/` with the first 1,000 rows only (the full CSV is about 95 MB; link to Kaggle instead)
- `screenshots/`: Control, Exceptions, Pivots, Summary, an Outlook draft (blur any address)
- `README.md`: business problem, data source, report rules, how to run, before and after (manual steps vs one click), runtime

## 7. CV line (update once built)
**Shipment Ageing Report Automation | Excel, VBA**
One-click VBA automation that turns a 180,000-line supply chain export into a filtered ageing report, region pivots, KPI summary and per-region email drafts, recreating the daily last-mile report automated at Flipkart.

## 8. Interview talking points
- Real problem first: the same report was built by hand every morning, so automating it removed a daily repetitive task.
- Business rules live on a Settings sheet, so operations can change statuses or thresholds without touching code.
- Arrays instead of cell loops keep 180,000 rows fast; email drafts are displayed, never auto-sent, as a control.

---

## Data profiling results (confirmed before writing the macro)

Loaded `Data/DataCoSupplyChainDataset.csv` with `cp1252` encoding: 180,519 rows x 53 columns, matches the plan.

**Delivery Status** (4 values): Late delivery 98,977 | Advance shipping 41,592 | Shipping on time 32,196 | Shipping canceled 7,754

**Order Status** (9 values): COMPLETE 59,491 | PENDING_PAYMENT 39,832 | PROCESSING 21,902 | PENDING 20,227 | CLOSED 19,616 | ON_HOLD 9,804 | SUSPECTED_FRAUD 4,062 | CANCELED 3,692 | PAYMENT_REVIEW 1,893

Shipping date range: 2015-01-03 to 2018-02-06. Delay Days (real minus scheduled) ranges -2 to 4.

### Filter rule fix (required, not optional)

The plan's exception rule as written -- "Delivery Status = Late delivery, OR an open Order Status" -- has a bug: **45,308 of the 98,977 "Late delivery" rows belong to orders already COMPLETE or CLOSED** (checked via crosstab). Those orders need no action from a hub team; they already happened and were closed out. Filtering on Delivery Status alone pulls them in as false "pending" exceptions.

**Fix:** add `COMPLETE` and `CLOSED` to the excluded Order Status list (they belong there anyway -- the plan's own Exclude step is titled "closed or not relevant"). With that one change, the exception rule collapses to: *scope = any order status except CANCELED / SUSPECTED_FRAUD / COMPLETE / CLOSED, delivery status except Shipping canceled, shipping date in the lookback window.* Delay Days then only decides which ageing bucket a row lands in (On schedule / 1 / 2 / 3+ days late) -- it no longer gates inclusion.

Checked against a 30-day lookback ending at the last shipping date in the data (2018-02-06):
- **Fixed rule: 954 exception rows** -- On schedule 393, 1 day late 310, 2 days late 157, 3+ days late 94. A realistic, demo-ready spread.
- Old rule as literally written: 1,462 rows, 508 of which are already-closed orders that need no action.

**Settings sheet excluded-status list should read:** `CANCELED, SUSPECTED_FRAUD, COMPLETE, CLOSED` (was: `CANCELED, SUSPECTED_FRAUD`).
