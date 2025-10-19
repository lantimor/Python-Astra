import cv2
import pytesseract
import pandas as pd
import os
import re

# --- SETUP PATH ---
IMG_DIR = r"d:\Astra Annual Report\public"   # folder tempat kamu simpan file PNG
OUTPUT_PATH = r"d:\Astra Annual Report\data_clean\financials_2019_2023.csv"

# --- KONFIGURASI OCR ---
# Pastikan kamu sudah install Tesseract dan tambahkan path-nya
# Misal di Windows:
# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# --- FUNGSI BERSIHIN ANGKA ---
def clean_number(val):
    val = re.sub(r"[^\d\-]", "", val)  # hapus non-digit kecuali minus
    return int(val) if val else None

# --- FUNGSI EKSTRAK TEKS DARI GAMBAR ---
def extract_text_from_image(image_path):
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
    text = pytesseract.image_to_string(gray, lang="eng+ind")
    return text

# --- FUNGSI PARSE TEKS KE TABEL ---
def parse_financial_text(text, year_label):
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    data = []
    section = None

    for line in lines:
        # Deteksi bagian laporan
        if "Laporan Laba Rugi" in line:
            section = "income_statement"
        elif "Posisi Keuangan" in line or "Neraca" in line:
            section = "balance_sheet"
        elif "Rasio" in line:
            section = "ratio_analysis"
        elif "Dividen" in line:
            section = "dividend"

        # Ambil angka (nilai dalam miliar)
        match = re.match(r"^(.*?)\s+([\d,]+)\s*$", line)
        if match:
            account = match.group(1).strip()
            amount = clean_number(match.group(2))
            if account and amount:
                data.append({
                    "year": year_label,
                    "category": section or "summary",
                    "account": account,
                    "amount": amount
                })

    return pd.DataFrame(data)

# --- PROSES SEMUA GAMBAR ---
all_data = []
for img_file in os.listdir(IMG_DIR):
    if img_file.endswith(".png"):
        year_match = re.search(r"(2019|2020|2021|2022|2023)", img_file)
        if year_match:
            year = int(year_match.group(1))
            print(f"🔍 Processing {img_file} (year={year})...")
            text = extract_text_from_image(os.path.join(IMG_DIR, img_file))
            df = parse_financial_text(text, year)
            print(f"✅ {len(df)} rows extracted from {img_file}")
            all_data.append(df)

# --- GABUNG SEMUA ---
final_df = pd.concat(all_data, ignore_index=True)
final_df.to_csv(OUTPUT_PATH, index=False)
print(f"\n✅ Data gabungan disimpan di: {OUTPUT_PATH}")
