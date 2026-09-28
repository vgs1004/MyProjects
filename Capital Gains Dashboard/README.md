# Capital Gains Tax Pipeline — Greshma Shares & Stocks FY 2024-25

Python pipeline to automate FIFO-based capital gains tax computation for 23 client portfolios.

---

## Folder Structure

```
capital_gains_dashboard/
├── data/
│   ├── client_files/        ← put all 23 client .md files here
│   └── output/              ← all generated CSVs and Excel go here
├── data_loader.py
├── data_cleaner.py
├── tax_engine.py
├── excel_generator.py
└── dashboard.py
```

---

## Setup

Install dependencies:

```
pip install pandas openpyxl xlsxwriter streamlit plotly
```

---

## How to Run (in order)

**Step 1 — Load client files**
```
python data_loader.py
```
Reads all `.md` files from `client_files/` and produces `master_raw_data.csv`.

**Step 2 — Clean the data**
```
python data_cleaner.py
```
Fixes date formats, numeric columns, swapped dates. Produces `master_cleaned_data.csv`.

**Step 3 — Run tax computation**
```
python tax_engine.py
```
Applies FIFO logic, STCG/LTCG classification, Budget 2024 dual rates, Section 70 set-off. Produces `final_tax_computation.csv`.

**Step 4 — Generate Excel report**
```
python excel_generator.py
```
Produces `Greshma_Strategic_Tax_Report.xlsx` with 6 sheets.

**Step 5 — Launch dashboard**
```
streamlit run dashboard.py
```
Opens the interactive browser dashboard. Keep the terminal open while using it.

---

## Changing the Input Path

All five files use the same `BASE_DIR` variable at the top. Change it in each file to match your system:

| File | Line to change |
|---|---|
| `data_loader.py` | `BASE_DIR = r"D:\Downloads\capital_gains_dashboard"` |
| `data_cleaner.py` | `BASE_DIR = r"D:\Downloads\capital_gains_dashboard"` |
| `tax_engine.py` | `BASE_DIR = r"D:\Downloads\capital_gains_dashboard"` |
| `excel_generator.py` | `BASE_DIR = r"D:\Downloads\capital_gains_dashboard"` |
| `dashboard.py` | `BASE_DIR = r"D:\Downloads\capital_gains_dashboard"` |

Example — if your folder is on the desktop:
```python
BASE_DIR = r"C:\Users\YourName\Desktop\capital_gains_dashboard"
```

On Mac/Linux use forward slashes:
```python
BASE_DIR = "/home/yourname/capital_gains_dashboard"
```

---

## Output Files

| File | Description |
|---|---|
| `master_raw_data.csv` | Raw consolidated data from all client files |
| `master_cleaned_data.csv` | Cleaned and validated dataset |
| `final_tax_computation.csv` | Final dataset with tax fields |
| `Greshma_Strategic_Tax_Report.xlsx` | 6-sheet Excel report for the broker |

---

## Notes

- Client `.md` files must be placed in `data/client_files/` before running Step 1.
- Steps must be run in order — each script depends on the output of the previous one.
- The dashboard reads `final_tax_computation.csv` directly, so re-running Step 3 automatically refreshes it on next launch.
