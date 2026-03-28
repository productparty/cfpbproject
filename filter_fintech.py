import pandas as pd
import os
import time

INPUT_PATH = r"d:\projects\cfpb\data\complaints.csv\complaints.csv"
OUTPUT_PATH = r"d:\projects\cfpb\data\cfpb_fintech_competitive.csv"
CHUNKSIZE = 500_000

# Filter criteria (case-insensitive matching on Company)
COMPANIES = {
    "jpmorgan chase & co.": "Chase",
    "ally financial inc.": "Ally",
    "capital one financial corporation": "Capital One",
    "wells fargo & company": "Wells Fargo",
    "chime financial, inc.": "Chime",
    "sofi technologies, inc.": "SoFi",
}

PRODUCTS = {
    "Checking or savings account",
    "Credit card or prepaid card",
    "Credit card",
    "Money transfer virtual currency or money service",
    "Money transfers",
    "Bank account or service",
    "Prepaid card",
}

header_written = False
total_rows = 0
start = time.time()

for i, chunk in enumerate(pd.read_csv(INPUT_PATH, chunksize=CHUNKSIZE, low_memory=False)):
    rows_in = len(chunk)
    print(f"Chunk {i}: read {rows_in:,} rows ...", end=" ")

    # Case-insensitive company match
    chunk["_company_lower"] = chunk["Company"].str.lower().str.strip()
    mask_company = chunk["_company_lower"].isin(COMPANIES.keys())
    mask_product = chunk["Product"].isin(PRODUCTS)
    filtered = chunk[mask_company & mask_product].copy()

    if len(filtered) == 0:
        print("0 matched")
        continue

    # Add derived columns
    filtered["Company_Short"] = filtered["_company_lower"].map(COMPANIES)
    filtered["Date received"] = pd.to_datetime(filtered["Date received"], errors="coerce")
    filtered["Year"] = filtered["Date received"].dt.year.astype("Int64")
    filtered["Year-Month"] = filtered["Date received"].dt.to_period("M").astype(str)
    filtered["Timely"] = (filtered["Timely response?"] == "Yes").astype(int)

    # Drop temp column
    filtered.drop(columns=["_company_lower"], inplace=True)

    # Write incrementally
    filtered.to_csv(OUTPUT_PATH, mode="a", index=False, header=not header_written)
    header_written = True
    total_rows += len(filtered)
    print(f"{len(filtered):,} matched  (running total: {total_rows:,})")

elapsed = time.time() - start
print(f"\nDone in {elapsed:.1f}s — {total_rows:,} rows written to {OUTPUT_PATH}")

# Summary stats
print("\n--- Summary ---")
df = pd.read_csv(OUTPUT_PATH, low_memory=False)
print(f"\nCompany counts:\n{df['Company_Short'].value_counts().to_string()}")
print(f"\nProduct counts:\n{df['Product'].value_counts().to_string()}")
df["Date received"] = pd.to_datetime(df["Date received"], errors="coerce")
print(f"\nDate range: {df['Date received'].min()} to {df['Date received'].max()}")
