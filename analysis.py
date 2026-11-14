"""
analysis.py
------------
Complete pipeline: Data Cleaning -> PCA -> UMAP -> K-Means Clustering -> GPI Scoring -> Recommendations.
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, MinMaxScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
import umap
import warnings
import os

warnings.filterwarnings("ignore")

# ============================================================
# STEP 0: FIX FILE PATH ISSUES
# ============================================================
# This finds the exact folder where analysis.py is located
script_dir = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(script_dir, "data.csv")

print(f"Looking for data at: {csv_path}")

# ============================================================
# STEP 1: LOAD DATA
# ============================================================
print("Loading data...")
try:
    df = pd.read_csv(csv_path)
    print(f"Loaded {len(df)} restaurants with {df.shape[1]} columns")
except FileNotFoundError:
    print("\n❌ ERROR: Could not find 'data.csv'. Please make sure you renamed your CSV file to 'data.csv' and it is in the same folder as this script.")
    exit()


# ============================================================
# STEP 2: CREATE NEW BUSINESS FEATURES
# ============================================================
print("Creating new features...")

df["TotalRevenue"] = (df["InStoreRevenue"] + df["UberEatsRevenue"]
                      + df["DoorDashRevenue"] + df["SelfDeliveryRevenue"])

df["TotalNetProfit"] = (df["InStoreNetProfit"] + df["UberEatsNetProfit"]
                        + df["DoorDashNetProfit"] + df["SelfDeliveryNetProfit"])

df["NetMargin"] = df["TotalNetProfit"] / df["TotalRevenue"].replace(0, np.nan)
df["AggregatorOrders"] = df["UberEatsOrders"] + df["DoorDashOrders"]
df["AggregatorSharePct"] = df["AggregatorOrders"] / df["MonthlyOrders"]
df["SelfDeliverySharePct"] = df["SelfDeliveryOrders"] / df["MonthlyOrders"]
df["OrdersPerKM"] = df["MonthlyOrders"] / df["DeliveryRadiusKM"]
df["CostLoad"] = df["COGSRate"] + df["OPEXRate"]
df["RevenuePerOrder"] = df["TotalRevenue"] / df["MonthlyOrders"]

print("Features created successfully")


# ============================================================
# STEP 3: PREPARE FEATURES FOR MACHINE LEARNING
# ============================================================
print("Preparing ML features...")

log_cols = ["MonthlyOrders", "TotalRevenue", "TotalNetProfit", "AOV",
            "SD_DeliveryTotalCost", "DeliveryCostPerOrder"]
for c in log_cols:
    df[f"log_{c}"] = np.log1p(df[c].clip(lower=0))

num_features = [
    "log_MonthlyOrders", "GrowthFactor", "AOV", "log_TotalRevenue",
    "COGSRate", "OPEXRate", "CommissionRate", "DeliveryRadiusKM",
    "DeliveryCostPerOrder", "log_SD_DeliveryTotalCost",
    "NetMargin", "AggregatorSharePct", "SelfDeliverySharePct",
    "OrdersPerKM", "CostLoad", "RevenuePerOrder"
]

cat_features = ["CuisineType", "Segment", "Subregion"]

preprocessor = ColumnTransformer([
    ("num", StandardScaler(), num_features),
    ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), cat_features)
])

X = preprocessor.fit_transform(df)
print(f"Feature matrix shape: {X.shape}")


# ============================================================
# STEP 4: PCA
# ============================================================
print("Running PCA...")
pca = PCA(n_components=10, random_state=42)
X_pca = pca.fit_transform(X)


# ============================================================
# STEP 5: UMAP (2D Map)
# ============================================================
print("Running UMAP (this may take 20-30 seconds)...")
reducer = umap.UMAP(n_neighbors=30, min_dist=0.1, random_state=42)
X_umap = reducer.fit_transform(X_pca[:, :10])
df["umap_x"] = X_umap[:, 0]
df["umap_y"] = X_umap[:, 1]
print("UMAP done")


# ============================================================
# STEP 6: K-MEANS CLUSTERING
# ============================================================
print("Running K-Means clustering...")
kmeans = KMeans(n_clusters=5, n_init=50, random_state=42)
df["cluster"] = kmeans.fit_predict(X_pca[:, :10])

sil = silhouette_score(X_pca[:, :10], df["cluster"])
print(f"Silhouette score: {sil:.3f}")


# ============================================================
# STEP 7: NAME THE CLUSTERS
# ============================================================
print("Profiling clusters...")

cluster_stats = df.groupby("cluster").agg({
    "NetMargin": "mean",
    "AggregatorSharePct": "mean",
    "SelfDeliverySharePct": "mean",
    "GrowthFactor": "mean",
    "CostLoad": "mean",
    "MonthlyOrders": "mean",
    "TotalNetProfit": "mean"
}).round(3)

def name_cluster(cluster_id):
    row = cluster_stats.loc[cluster_id]
    
    if row["TotalNetProfit"] < 3000 and row["CostLoad"] > 0.80:
        return "Overextended Low-Return"
    if row["AggregatorSharePct"] > 0.75:
        return "Aggregator-Dependent Low-Margin"
    if row["SelfDeliverySharePct"] > 0.28 and row["NetMargin"] > 0.10:
        return "Scalable Self-Delivery Leaders"
    if row["GrowthFactor"] > 1.035 and row["CostLoad"] > 0.70:
        return "High-Growth / High-Risk"
    return "Stable Local Performers"

df["cluster_label"] = df["cluster"].apply(name_cluster)


# ============================================================
# STEP 8: GROWTH POTENTIAL INDEX (GPI)
# ============================================================
print("Computing GPI...")

df["Scale_raw"] = df["MonthlyOrders"] * df["GrowthFactor"]
df["CostDiscipline_raw"] = 1 - df["CostLoad"]
df["ChannelBalance_raw"] = 1 - df["AggregatorSharePct"]
df["ExpansionHeadroom_raw"] = (df["DeliveryRadiusKM"] / df["DeliveryRadiusKM"].max()) * df["OrdersPerKM"]
df["RevenueQuality_raw"] = df["AOV"] * df["NetMargin"].fillna(0)

kpi_cols = ["Scale_raw", "CostDiscipline_raw", "ChannelBalance_raw",
            "ExpansionHeadroom_raw", "RevenueQuality_raw"]
mm = MinMaxScaler()
kpi_norm = pd.DataFrame(
    mm.fit_transform(df[kpi_cols]),
    columns=kpi_cols, index=df.index
)

weights = {
    "Scale_raw": 0.25,
    "CostDiscipline_raw": 0.25,
    "ChannelBalance_raw": 0.20,
    "ExpansionHeadroom_raw": 0.15,
    "RevenueQuality_raw": 0.15
}
df["GPI"] = sum(kpi_norm[col] * w for col, w in weights.items())

for col in kpi_cols:
    df[col.replace("_raw", "")] = kpi_norm[col]

df["GPI_100"] = df["GPI"].rank(pct=True) * 100


# ============================================================
# STEP 9: STRATEGY RECOMMENDATION
# ============================================================
print("Assigning strategy recommendations...")

def recommend(row):
    if row["cluster_label"] == "Overextended Low-Return" or row["GPI_100"] < 20:
        return "Restructure / contract: reduce radius, renegotiate aggregator terms"
    if row["cluster_label"] == "Aggregator-Dependent Low-Margin" or row["AggregatorSharePct"] > 0.78:
        return "Rebalance channels: grow self-delivery, cap UE/DD dependence"
    if row["cluster_label"] == "High-Growth / High-Risk":
        return "Optimize before scaling: cut cost load, then expand"
    if row["cluster_label"] == "Scalable Self-Delivery Leaders" and row["GPI_100"] > 65:
        return "Scale: replicate SD-led model in adjacent subregions"
    return "Hold / stabilize: protect margin, selective local expansion"

df["Recommendation"] = df.apply(recommend, axis=1)


# ============================================================
# STEP 10: SAVE RESULTS
# ============================================================
print("Saving results...")
output_cols = [
    "RestaurantID", "RestaurantName", "CuisineType", "Segment", "Subregion",
    "GrowthFactor", "AOV", "MonthlyOrders", "TotalRevenue", "TotalNetProfit",
    "NetMargin", "AggregatorSharePct", "SelfDeliverySharePct",
    "CostLoad", "DeliveryRadiusKM",
    "umap_x", "umap_y", "cluster", "cluster_label",
    "GPI", "GPI_100",
    "Scale", "CostDiscipline", "ChannelBalance",
    "ExpansionHeadroom", "RevenueQuality",
    "Recommendation"
]

# Save the output right next to the script
output_path = os.path.join(script_dir, "restaurants_scored.csv")
df[output_cols].to_csv(output_path, index=False)

print("\n✅ Done! Saved 'restaurants_scored.csv'")
print(f"   Rows: {len(df)}")