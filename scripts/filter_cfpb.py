import pandas as pd
import zipfile
import os
import sys

# --- CONFIG ---
INPUT_ZIP = sys.argv[1] if len(sys.argv) > 1 else "complaints.csv.zip"
OUTPUT_CSV = "cfpb_fintech_competitive.csv"

# Target companies (using parent company names as they appear in CFPB data)
TARGET_COMPANIES = [
    "JPMORGAN CHASE & CO.",
    "ALLY FINANCIAL INC.",
    "CAPITAL ONE FINANCIAL CORPORATION",
    "WELLS FARGO & COMPANY",
    "CHIME FINANCIAL, INC.",
    "SOFI TECHNOLOGIES, INC.",
]

# Fintech-relevant products
TARGET_PRODUCTS = [
    "Checking or savings account",
    "Credit card or prepaid card",
    "Credit card",
    "Money transfer, virtual currency, or money service",
    "Money transfers",
    "Bank account or service",
    "Prepaid card",
]

# --- EXTRACT ---
print(f"Reading {INPUT_ZIP}...")
if INPUT_ZIP.endswith(".zip"):
    with zipfile.ZipFile(INPUT_ZIP, "r") as z:
        csv_name = [f for f in z.namelist() if f.endswith(".csv")][0]
        print(f"  Extracting {csv_name}...")
        df = pd.read_csv(z.open(csv_name), low_memory=False)
else:
    df = pd.read_csv(INPUT_ZIP, low_memory=False)

print(f"  Total rows: {len(df):,}")
print(f"  Columns: {list(df.columns)}")

# --- FILTER ---
# Normalize company names for matching
df["company_upper"] = df["Company"].str.upper().str.strip()
target_upper = [c.upper() for c in TARGET_COMPANIES]

df_filtered = df[
    (df["company_upper"].isin(target_upper))
    & (df["Product"].isin(TARGET_PRODUCTS))
].copy()

df_filtered.drop(columns=["company_upper"], inplace=True)

print(f"\n  After filtering: {len(df_filtered):,} rows")
print(f"\n  Companies found:")
for co in df_filtered["Company"].value_counts().items():
    print(f"    {co[0]}: {co[1]:,}")
print(f"\n  Products:")
for prod in df_filtered["Product"].value_counts().items():
    print(f"    {prod[0]}: {prod[1]:,}")
print(f"\n  Date range: {df_filtered['Date received'].min()} to {df_filtered['Date received'].max()}")

# --- ADD HELPER COLUMNS FOR TABLEAU ---
df_filtered["Date received"] = pd.to_datetime(df_filtered["Date received"])
df_filtered["Year"] = df_filtered["Date received"].dt.year
df_filtered["Year-Month"] = df_filtered["Date received"].dt.to_period("M").astype(str)
df_filtered["Timely"] = (df_filtered["Timely response?"] == "Yes").astype(int)

# Simplified company names for cleaner viz labels
name_map = {
    "JPMORGAN CHASE & CO.": "Chase",
    "ALLY FINANCIAL INC.": "Ally",
    "CAPITAL ONE FINANCIAL CORPORATION": "Capital One",
    "WELLS FARGO & COMPANY": "Wells Fargo",
    "CHIME FINANCIAL, INC.": "Chime",
    "SOFI TECHNOLOGIES, INC.": "SoFi",
}
df_filtered["Company_Short"] = (
    df_filtered["Company"].str.upper().str.strip().map(name_map)
)

# --- SAVE ---
df_filtered.to_csv(OUTPUT_CSV, index=False)
print(f"\n  Saved to {OUTPUT_CSV} ({os.path.getsize(OUTPUT_CSV) / 1024 / 1024:.1f} MB)")
print("  Ready for Tableau Cloud upload.")
