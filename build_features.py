import pandas as pd

INPUT_PATH = "cms_providers_step1_clean.csv"
OUTPUT_PATH = "cms_providers_step2_features.csv"

# 1. Load step-1 cleaned data
df = pd.read_csv(INPUT_PATH)
print("Loaded shape:", df.shape)
print("Columns:", df.columns.tolist())

npi_col = "Rndrng_NPI"

# 2. Make sure key columns exist
required_cols = [
    npi_col,
    "Tot_Benes",
    "Tot_Srvcs",
    "Tot_Sbmtd_Chrg",
    "Tot_Mdcr_Alowd_Amt",
    "Tot_Mdcr_Pymt_Amt",
]

for col in required_cols:
    if col not in df.columns:
        raise ValueError(f"Missing required column: {col}")

# 3. Drop rows where Tot_Benes or Tot_Srvcs are 0 or NaN (can't form ratios)
df = df.copy()
df = df[(df["Tot_Benes"] > 0) & (df["Tot_Srvcs"] > 0)]
print("After dropping zero benes/services:", df.shape)

# 4. Create derived billing features (behavioral ratios)

df["allowed_per_bene"] = df["Tot_Mdcr_Alowd_Amt"] / df["Tot_Benes"]
df["payment_per_bene"] = df["Tot_Mdcr_Pymt_Amt"] / df["Tot_Benes"]
df["submitted_per_bene"] = df["Tot_Sbmtd_Chrg"] / df["Tot_Benes"]

df["allowed_per_srv"] = df["Tot_Mdcr_Alowd_Amt"] / df["Tot_Srvcs"]
df["payment_per_srv"] = df["Tot_Mdcr_Pymt_Amt"] / df["Tot_Srvcs"]
df["submitted_per_srv"] = df["Tot_Sbmtd_Chrg"] / df["Tot_Srvcs"]

df["submitted_allowed_ratio"] = df["Tot_Sbmtd_Chrg"] / df["Tot_Mdcr_Alowd_Amt"]

# 5. (Optional) Keep just what we really need going forward
keep_cols = [
    npi_col,
    "Rndrng_Prvdr_Type",
    "Rndrng_Prvdr_State_Abrvtn",
    "Tot_HCPCS_Cds",
    "Tot_Benes",
    "Tot_Srvcs",
    "Tot_Sbmtd_Chrg",
    "Tot_Mdcr_Alowd_Amt",
    "Tot_Mdcr_Pymt_Amt",
    "Tot_Mdcr_Stdzd_Amt",
    "allowed_per_bene",
    "payment_per_bene",
    "submitted_per_bene",
    "allowed_per_srv",
    "payment_per_srv",
    "submitted_per_srv",
    "submitted_allowed_ratio",
]

keep_cols = [c for c in keep_cols if c in df.columns]
df_out = df[keep_cols].copy()

print("Final feature shape:", df_out.shape)
print(df_out.head())

# 6. Save
df_out.to_csv(OUTPUT_PATH, index=False)
print(f"Saved step-2 feature file to: {OUTPUT_PATH}")
