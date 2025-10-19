import pdfplumber, re, pandas as pd
from pathlib import Path

pdf_path = "Astra-Annual-Report-2023.pdf"
out_dir = Path("extracted_csvs")
out_dir.mkdir(exist_ok=True)

keywords = ["Pendapatan Bersih","Net Revenue","Laba Tahun Berjalan","Profit for the Year",
            "Jumlah Aset","Total Assets","Arus Kas","Cash Flow","Laporan Posisi Keuangan"]

with pdfplumber.open(pdf_path) as pdf:
    n = len(pdf.pages)
    hit_pages = set()
    for i in range(0, n, 2):
        txt = (pdf.pages[i].extract_text() or "").lower()
        if any(k.lower() in txt for k in keywords):
            for p in range(max(0,i-3), min(n,i+4)):
                hit_pages.add(p+1)
    hit_pages = sorted(hit_pages)
    print("Candidate pages:", hit_pages)
    for p in hit_pages:
        page = pdf.pages[p-1]
        tables = page.extract_tables()
        for ti, t in enumerate(tables):
            df = pd.DataFrame(t).dropna(how='all').dropna(axis=1, how='all')
            if df.empty: continue
            first = " ".join(map(str, df.iloc[0].tolist())).lower()
            if any(x in first for x in ["pendapatan","net","revenue","laba","profit","aset","asset"]):
                df.columns = df.iloc[0]
                df = df.iloc[1:].reset_index(drop=True)
            csv_path = out_dir / f"{Path(pdf_path).stem}_p{p}_t{ti}.csv"
            df.to_csv(csv_path, index=False)
            print("Saved", csv_path)
