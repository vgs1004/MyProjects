import pandas as pd
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_FILE = os.path.join(BASE_DIR, "data", "output", "master_raw_data.csv")
OUTPUT_FILE = os.path.join(BASE_DIR, "data", "output", "master_cleaned_data.csv")

def clean_portfolio_data(input_path, output_path):
    print("cleaning raw data...")

    df = pd.read_csv(input_path)

    # strip whitespace from column names just in case
    df.columns = [c.strip() for c in df.columns]
    print(f"columns loaded: {df.columns.tolist()}")
 
    # numeric columns had commas and currency symbols from the markdown export
    cols_to_fix = [
        'Buy Value', 'Sell Value', 'Buy Price', 'Sell Price',
        'Short Term Realised Gain', 'Long Term Realised Gain',
        'Speculative Gain/Loss'
    ]

    for col in cols_to_fix:
        if col in df.columns:
            df[col] = df[col].astype(str).str.replace(',', '').str.replace(' ', '').str.strip()
            df[col] = pd.to_numeric(df[col], errors='coerce')
        else:
            print(f"column '{col}' not found, skipping")

    # scrip name and ISIN cleanup
    if 'Scrip Name' in df.columns:
        df['Scrip Name'] = df['Scrip Name'].str.strip().str.upper()
    if 'ISIN' in df.columns:
        df['ISIN'] = df['ISIN'].str.strip().str.upper()

    # date parsing - mixed formats across client files needed format='mixed'
    df['Purchase Date'] = pd.to_datetime(df['Purchase Date'], format='mixed', dayfirst=True, errors='coerce')
    df['Sell Date']     = pd.to_datetime(df['Sell Date'],     format='mixed', dayfirst=True, errors='coerce')

    # check for swapped dates and fix them
    swapped_mask = (
        (df['Sell Date'] < df['Purchase Date']) &
        (df['Sell Date'].notna()) &
        (df['Purchase Date'].notna())
    )
    print(f"{swapped_mask.sum()} rows had swapped dates, fixing...")
    df.loc[swapped_mask, ['Purchase Date', 'Sell Date']] = (
        df.loc[swapped_mask, ['Sell Date', 'Purchase Date']].values
    )

    # holding period in calendar days
    df['Holding Period'] = (df['Sell Date'] - df['Purchase Date']).dt.days

    # round prices to 2 decimal places
    df['Sell Price'] = df['Sell Price'].round(2)
    df['Buy Price']  = df['Buy Price'].round(2)

    # realized gain = sell - buy, needed before fixing placeholders below
    df['Realized_Gain_Loss'] = df['Sell Value'] - df['Buy Value']

    # some rows had 99999.99 as a placeholder in the source files
    placeholder_mask = (
        (df['Short Term Realised Gain'] == 99999.99) |
        (df['Long Term Realised Gain']  == 99999.99)
    )
    print(f"{placeholder_mask.sum()} rows with 99999.99 placeholder, recalculating from buy/sell values...")

    df.loc[placeholder_mask & (df['Holding Period'] <= 365), 'Short Term Realised Gain'] = \
        df.loc[placeholder_mask & (df['Holding Period'] <= 365), 'Realized_Gain_Loss']

    df.loc[placeholder_mask & (df['Holding Period'] > 365), 'Long Term Realised Gain'] = \
        df.loc[placeholder_mask & (df['Holding Period'] > 365), 'Realized_Gain_Loss']

    df.to_csv(output_path, index=False)
    print(f"done. saved to {output_path}")
    return df

if __name__ == "__main__":
    if os.path.exists(INPUT_FILE):
        try:
            clean_portfolio_data(INPUT_FILE, OUTPUT_FILE)
        except Exception as e:
            print(f"something went wrong: {e}")
    else:
        print(f"could not find {INPUT_FILE} - run data_loader.py first")