import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler

INPUT_PATH = "cms_providers_step2_features.csv"
OUTPUT_FEATURES_PATH = "provider_features_matrix.csv"
OUTPUT_LOOKUP_PATH = "provider_node_lookup.csv"

df = pd.read_csv(INPUT_PATH)
print("Loaded shape:", df.shape)

npi_col = "Rndrng_NPI"

# 1. Define numeric feature columns
numeric_cols = [
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

numeric_cols = [c for c in numeric_cols if c in df.columns]
print("Numeric cols:", numeric_cols)

# 2. Replace inf with NaN
df = df.replace([np.inf, -np.inf], np.nan)

# 3. Impute missing numeric values with column median (simple + robust)
# 3. Impute missing numeric values
for col in numeric_cols:
    if df[col].notna().any():
        median_val = df[col].median()
        df[col] = df[col].fillna(median_val)
    else:
        # column is entirely NaN -> set to 0
        df[col] = 0

print("Any NaNs left in numeric cols?",
      df[numeric_cols].isna().any().any())


# 4. Create integer IDs for provider, specialty, and state
df = df.copy()

df["prov_id"] = df[npi_col].astype("category").cat.codes

if "Rndrng_Prvdr_Type" in df.columns:
    df["spec_id"] = df["Rndrng_Prvdr_Type"].astype("category").cat.codes
else:
    df["spec_id"] = -1

if "Rndrng_Prvdr_State_Abrvtn" in df.columns:
    df["state_id"] = df["Rndrng_Prvdr_State_Abrvtn"].astype("category").cat.codes
else:
    df["state_id"] = -1

print("Example IDs:")
print(df[[npi_col, "prov_id", "Rndrng_Prvdr_Type", "spec_id",
          "Rndrng_Prvdr_State_Abrvtn", "state_id"]].head())

# 5. Standardize numeric features
scaler = StandardScaler()
X = scaler.fit_transform(df[numeric_cols])

# 6. Save feature matrix (one row per provider_id) and lookup
features_df = pd.DataFrame(X, columns=numeric_cols)
features_df.insert(0, "prov_id", df["prov_id"].values)

features_df.to_csv(OUTPUT_FEATURES_PATH, index=False)
print(f"Saved provider feature matrix to: {OUTPUT_FEATURES_PATH}")

lookup_cols = [
    npi_col,
    "prov_id",
    "Rndrng_Prvdr_Type",
    "spec_id",
    "Rndrng_Prvdr_State_Abrvtn",
    "state_id",
]
lookup_cols = [c for c in lookup_cols if c in df.columns]
lookup_df = df[lookup_cols].drop_duplicates(subset=["prov_id"])

lookup_df.to_csv(OUTPUT_LOOKUP_PATH, index=False)
print(f"Saved provider node lookup table to: {OUTPUT_LOOKUP_PATH}")
