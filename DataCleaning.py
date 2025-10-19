import pandas as pd, re, os

def clean_number(x):
    if pd.isna(x): return None
    s = str(x).replace(",", "").replace(".", "")
    s = re.sub(r"[^\d\-]", "", s)
    try: return int(s)
    except: return None

def clean_csv(path, year, category):
    df = pd.read_csv(path, dtype=str).dropna(how="all")
    df.columns = [c.strip().replace("\n"," ") for c in df.columns]
    # deteksi kolom tahun
    year_col = next((c for c in df.columns if str(year) in c), None)
    if not year_col: year_col = df.columns[1]
    df = df[[df.columns[0], year_col]]
    df.columns = ["account", "amount"]
    df["year"] = year
    df["category"] = category
    df["amount"] = df["amount"].apply(clean_number)
    df = df.dropna(subset=["amount"])
    return df[["year","category","account","amount"]]

# definisi file
files = {
    "summary": "Astra-2024/2024_summary_financials.csv",
    "balance_assets": "Astra-2024/2024_balance_sheet_assets.csv",
    "balance_liabilities_equity": "Astra-2024/2024_balance_sheet_liabilities_equity.csv",
    "income_statement": "Astra-2024/2024_income_statement.csv",
    "segment_revenue": "Astra-2024/2024_segment_revenue.csv",
    "segment_profit": "Astra-2024/2024_segment_profit.csv",
    "dividend": "Astra-2024/2024_dividend.csv",
}


cleaned = []
for cat, path in files.items():
    if os.path.exists(path):
        df = clean_csv(path, 2024, cat)
        cleaned.append(df)
        print(f"✅ Cleaned {cat}: {df.shape[0]} rows")

final_df = pd.concat(cleaned, ignore_index=True)
final_df.to_csv("AstraDataCleansed/financials_2024_clean.csv", index=False)
print("💾 Saved: AstraDataCleansed/financials_2024_clean.csv")
