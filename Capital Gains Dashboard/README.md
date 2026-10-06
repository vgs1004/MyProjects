# Capital Gains Tax Pipeline (Python, Streamlit)

Business Data Management project, IIT Madras Diploma in Data Science, built on real data from a stockbroking firm for FY 2024-25. The pipeline turns 23 clients' realised profit and loss statements into a per-client capital gains tax computation and an interactive dashboard.

**Client data is confidential and is not included.** The repository ships with two synthetic sample statements in `sample_data/client_files/` so the full pipeline can be run end to end.

## What it does

1. **Load** (`data_loader.py`): reads each client's statement (markdown tables), consolidates all clients into one dataset and tags each row with the client.
2. **Clean** (`data_cleaner.py`): fixes number formats, standardises scrip names and ISINs, parses mixed date formats, corrects rows where purchase and sell dates were swapped, computes the holding period, and recalculates gains where the source used a 99999.99 placeholder.
3. **Compute tax** (`tax_engine.py`): classifies each realised lot as short-term (held 365 days or less) or long-term, applies the dual rates around the Union Budget date of 23 July 2024 (STCG 15% before, 20% after; LTCG 12.5% above the 1.25 lakh exemption under Section 112A), sets off losses against gains per client (Section 70), and allocates the tax across profitable trades.
4. **Dashboard** (`dashboard.py`): Streamlit app with portfolio KPIs, tax by category, client and scrip level profit and loss, and CSV download of filtered results.

## How to run

```
pip install -r requirements.txt
python data_loader.py
python data_cleaner.py
python tax_engine.py
streamlit run dashboard.py
```

Outputs are written to `data/output/` (`master_raw_data.csv`, `master_cleaned_data.csv`, `final_tax_computation.csv`). With real data, place the client statements in `data/client_files/`; otherwise the loader uses the synthetic sample automatically.

## Files

| File | Purpose |
|---|---|
| `data_loader.py` | Consolidates client statements |
| `data_cleaner.py` | Data cleaning and validation |
| `tax_engine.py` | Tax classification, set-off and liability |
| `dashboard.py` | Streamlit dashboard |
| `sample_data/client_files/` | Two synthetic client statements |
| `requirements.txt` | Python dependencies |

Tools: Python, pandas, Streamlit, Plotly.
