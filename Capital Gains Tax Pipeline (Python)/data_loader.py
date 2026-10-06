import pandas as pd
import os
import io

BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
DATA_SOURCE = os.path.join(BASE_DIR, "data", "client_files")
OUTPUT_DIR  = os.path.join(BASE_DIR, "data", "output")

def load_and_consolidate_reports(source_path, output_path):
    if not os.path.exists(output_path): os.makedirs(output_path)
    all_client_data = []

    for filename in os.listdir(source_path):
        if filename.endswith(".md"):
            with open(os.path.join(source_path, filename), 'r', encoding='utf-8') as f:
                lines = f.readlines()

            table_lines = []
            for l in lines:
                clean_l = l.strip().strip('|')
                if clean_l.count("|") >= 10 and "---" not in clean_l:
                    table_lines.append(clean_l)

            if table_lines:
                df = pd.read_csv(io.StringIO("\n".join(table_lines)), sep="|", skipinitialspace=True)
                df.columns = [c.strip() for c in df.columns]

                df = df[df['Scrip Name'].str.contains('Scrip Name') == False]

                df['Client_Source'] = "-".join(filename.split("-")[2:-3])
                df['Original_File'] = filename
                all_client_data.append(df)

    if all_client_data:
        master_df = pd.concat(all_client_data, ignore_index=True)
        master_df.to_csv(os.path.join(output_path, "master_raw_data.csv"), index=False)
        print(f"done. consolidated {len(all_client_data)} client files.")
        return master_df

SAMPLE_SOURCE = os.path.join(BASE_DIR, "sample_data", "client_files")

if __name__ == "__main__":
    # real client files are not published; fall back to the synthetic sample
    source = DATA_SOURCE if os.path.isdir(DATA_SOURCE) and os.listdir(DATA_SOURCE) else SAMPLE_SOURCE
    print(f"reading client files from {source}")
    load_and_consolidate_reports(source, OUTPUT_DIR)