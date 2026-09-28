import pandas as pd
import os

BASE_DIR     = r"D:\Downloads\capital_gains_dashboard"
INPUT_FILE   = os.path.join(BASE_DIR, "data", "output", "master_cleaned_data.csv")
FINAL_OUTPUT = os.path.join(BASE_DIR, "data", "output", "final_tax_computation.csv")

BUDGET_DATE    = pd.Timestamp("2024-07-23")
LTCG_EXEMPTION = 125000

def run_tax_engine():
    print("running tax computation...")

    if not os.path.exists(INPUT_FILE):
        print(f"could not find {INPUT_FILE} - run data_cleaner.py first")
        return

    df = pd.read_csv(INPUT_FILE)
    df['Sell Date'] = pd.to_datetime(df['Sell Date'], errors='coerce')

    df['Realized_Gain_Loss']       = (df['Sell Value'] - df['Buy Value']).round(2)
    df['Tax_Category']             = df['Holding Period'].apply(lambda x: 'LTCG' if x > 365 else 'STCG')
    df['Calculated_Tax_Liability'] = 0.0

    clients = df['Client_Source'].unique()

    for client in clients:
        mask = df['Client_Source'] == client
        cdf  = df[mask].copy()

        # STCG set-off per Section 70, split by budget date for dual rate
        stcg_df   = cdf[cdf['Tax_Category'] == 'STCG']
        stcg_pre  = stcg_df[stcg_df['Sell Date'] <  BUDGET_DATE]['Realized_Gain_Loss'].sum()
        stcg_post = stcg_df[stcg_df['Sell Date'] >= BUDGET_DATE]['Realized_Gain_Loss'].sum()
        total_stcg_net = stcg_pre + stcg_post

        if total_stcg_net <= 0:
            stcg_tax = 0.0
        elif stcg_pre > 0 and stcg_post > 0:
            stcg_tax = (stcg_pre * 0.15) + (stcg_post * 0.20)
        elif stcg_pre > 0:
            stcg_tax = total_stcg_net * 0.15
        else:
            stcg_tax = total_stcg_net * 0.20

        # LTCG set-off with 1.25L exemption under Section 112A
        ltcg_df      = cdf[cdf['Tax_Category'] == 'LTCG']
        ltcg_net     = ltcg_df['Realized_Gain_Loss'].sum()
        taxable_ltcg = max(0, ltcg_net - LTCG_EXEMPTION)
        ltcg_tax     = taxable_ltcg * 0.125

        # spread total tax proportionally across winning trades only
        total_client_tax    = round(stcg_tax + ltcg_tax, 2)
        winning_mask        = mask & (df['Realized_Gain_Loss'] > 0)
        total_winning_gains = df.loc[winning_mask, 'Realized_Gain_Loss'].sum()

        if total_winning_gains > 0:
            df.loc[winning_mask, 'Calculated_Tax_Liability'] = (
                (df.loc[winning_mask, 'Realized_Gain_Loss'] / total_winning_gains) * total_client_tax
            ).round(2)

    df.to_csv(FINAL_OUTPUT, index=False)

    print(f"done. {len(clients)} clients processed.")
    print(f"net portfolio gain/loss : INR {df['Realized_Gain_Loss'].sum():,.2f}")
    print(f"total tax liability     : INR {df['Calculated_Tax_Liability'].sum():,.2f}")
    print(f"saved to {FINAL_OUTPUT}")

if __name__ == "__main__":
    run_tax_engine()