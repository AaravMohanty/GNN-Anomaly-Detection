import pandas as pd

# 1. Path to the raw CMS CSV you downloaded
CSV_PATH = r"C:\Users\mohan\GNN-Anomaly-Detection\Data\Medicare_Physician_Other_Practitioners_by_Provider_2023.csv"

# 2. Load the raw CSV
df_raw = pd.read_csv(CSV_PATH, low_memory=False)
print("Number of rows:", len(df_raw))
print("Sample columns:", df_raw.columns[:20])

# 3. Figure out the NPI column name (case-insensitive search for 'npi')
npi_candidates = [c for c in df_raw.columns if "npi" in c.lower()]
print("NPI candidates:", npi_candidates)

if not npi_candidates:
    raise ValueError("Could not find an NPI-like column. Check df_raw.columns.")
npi_col = npi_candidates[0]  # should be 'Rndrng_NPI'
print("Using NPI column:", npi_col)

# 4. Columns we care about right now (match EXACT names from your file)
context_cols = [
    "Rndrng_Prvdr_Type",          # provider specialty
    "Rndrng_Prvdr_State_Abrvtn",  # state
    # you can add 'Rndrng_Prvdr_Zip5' later if you want ZIP
]

billing_cols = [
    "Tot_HCPCS_Cds",        # total unique HCPCS codes
    "Tot_Benes",            # total beneficiaries
    "Tot_Srvcs",            # total services
    "Tot_Sbmtd_Chrg",       # total submitted charges
    "Tot_Mdcr_Alowd_Amt",   # total Medicare allowed
    "Tot_Mdcr_Pymt_Amt",    # total Medicare payment
    "Tot_Mdcr_Stdzd_Amt",   # standardized payment (optional but useful)
]

# Keep only columns that actually exist in the file
keep_cols = [npi_col] + [c for c in context_cols + billing_cols if c in df_raw.columns]
df = df_raw[keep_cols].copy()

print("Columns kept:", df.columns.tolist())

# 5. Convert billing columns to numeric (important for later math)
for col in billing_cols:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

# 6. Drop rows without NPI
df = df.dropna(subset=[npi_col])

print("Cleaned shape:", df.shape)
print(df.head())

# 7. Save this as the Step 1 output
OUTPUT_PATH = "cms_providers_step1_clean.csv"
df.to_csv(OUTPUT_PATH, index=False)
print(f"Saved step-1 cleaned file to: {OUTPUT_PATH}")
