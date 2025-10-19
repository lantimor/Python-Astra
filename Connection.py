import pandas as pd
import pyodbc

# --- koneksi ke SQL Server ---
conn = pyodbc.connect(
    "DRIVER={ODBC Driver 18 for SQL Server};"
    "SERVER=LAPTOP-EL3VF6SH\\SQLEXPRESS;"
    "DATABASE=AstraDB;"
    "Trusted_Connection=yes;"
    "Encrypt=no;"
)
cur = conn.cursor()

# --- load dan cleaning ---
df = pd.read_csv("AstraDataCleansed/financials_2024_clean.csv")
df["year"] = df["year"].astype(int)
df["category"] = df["category"].astype(str)
df["account"] = df["account"].astype(str)
df["amount"] = pd.to_numeric(df["amount"], errors="coerce").fillna(0).astype(float)

# --- insert ---
sql = "INSERT INTO fact_financials (year, category, account, amount) VALUES (?, ?, ?, ?)"

for i, row in enumerate(df.itertuples(index=False, name=None), start=1):
    try:
        cur.execute(sql, row)
    except Exception as e:
        print(f"❌ Error di baris {i}: {row}")
        print(e)
        break

conn.commit()
conn.close()
print("🎉 Semua data berhasil masuk ke SQL Server!")
