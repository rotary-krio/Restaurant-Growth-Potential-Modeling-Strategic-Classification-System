# 🍽️ SkyCity Restaurant Growth Intelligence

An end-to-end Data Science and Machine Learning pipeline designed to classify 1,000 SkyCity Auckland restaurant branches into strategic growth archetypes. This project moves beyond traditional descriptive analytics, providing a prescriptive framework to score, cluster, and recommend expansion strategies based on operational, financial, and channel data.

## 📖 Project Overview
Not all restaurants should pursue the same growth strategy. Traditional models optimize for current profit but fail to assess structural readiness for expansion. This project utilizes unsupervised machine learning to discover hidden patterns across 30+ dimensions, classifying venues into distinct profiles (e.g., "Aggregator-Dependent Low-Margin" vs. "Scalable Self-Delivery Leaders"). 

It culminates in a **Growth Potential Index (GPI)** and an interactive, premium dark-mode dashboard for live analytics and strategic decision-making.

---

## 🚀 Key Features

*   **Advanced Dimensionality Reduction:** Uses PCA (Principal Component Analysis) to uncover latent business factors (Cost Pressure, Channel Leverage, Growth Momentum) and UMAP to project non-linear relationships into a 2D visual space.
*   **Machine Learning Clustering:** Implements K-Means clustering (validated via Hierarchical Ward clustering) to segment the market into **5 distinct restaurant archetypes**.
*   **Growth Potential Index (GPI):** A proprietary scoring model (0–100) that evaluates every venue across 5 weighted KPIs:
    *   *Scale* (Orders × GrowthFactor)
    *   *Cost Discipline* (COGS + OPEX stability)
    *   *Channel Balance* (Aggregator vs. Self-Delivery)
    *   *Expansion Headroom* (Delivery Radius vs. Demand)
    *   *Revenue Quality* (AOV × Margin)
*   **Prescriptive Strategy Engine:** Automatically assigns one of four actionable strategies to every restaurant: `Scale`, `Rebalance Channels`, `Optimize`, or `Restructure`.
*   **Live Streamlit Dashboard:** A highly interactive, glassmorphism-styled web app featuring:
    *   🗺️ **Interactive Cluster Map:** Hoverable 2D UMAP scatter plot with dynamic sunburst charts for cuisine breakdowns.
    *   📊 **GPI Scorecards:** Auto-generated Top 20 and Bottom 20 leaderboards.
    *   🕸️ **Radar Charts:** Visual "DNA" comparison of up to 3 restaurants across the 5 KPIs.
    *   🎯 **Strategy Panel:** Heatmaps and downloadable CSV reports for government/stakeholder funding allocations.
    *   ⚖️ **Side-by-Side Comparison:** Compare financial metrics and margins of multiple venues.

---
## 🛠️ Tech Stack
Programming Language: Python 3.10+

Data Manipulation & Math: pandas, numpy

Machine Learning & Dimensionality Reduction: scikit-learn (StandardScaler, MinMaxScaler, PCA, KMeans), umap-learn

Data Visualization & Dashboarding: streamlit, plotly (plotly.express, plotly.graph_objects)
---

## 🧠 Algorithms Used
Principal Component Analysis (PCA): Used to compress 30+ features into 10 principal components, reducing dimensionality and uncovering latent factors (e.g., separating "Scale" from "Cost Pressure").

Uniform Manifold Approximation and Projection (UMAP): Used for advanced non-linear dimensionality reduction to create the 2D coordinates (umap_x, umap_y) used for the interactive scatter map.

K-Means Clustering: The core unsupervised learning algorithm used to group 1,000 restaurants into 5 distinct operational archetypes based on their PCA-reduced features.

Hierarchical Clustering (Ward's Method): Used as a robustness check to validate the K-Means results (achieved a strong Adjusted Rand Index agreement).

Min-Max & Standard Scaling: Algorithms used to normalize varying numerical scales (preventing revenue in thousands from dominating percentage rates).

---

## 👤 Author Info
Name: Krishiv Kage \
Role: Data Science Intern \
Project: SkyCity Auckland Restaurants & Bars – Growth Potential Modeling \
Email: rotarykrio@gmail.com

---

## 📂 Repository Structure

```text
skycity_growth_intelligence/
│
├── data.csv                        # Raw dataset (1000 restaurants, 30+ features)
├── analysis.py                     # ML Pipeline: Preprocessing -> PCA -> UMAP -> K-Means -> GPI
├── app.py                          # Streamlit Dashboard (Live Analytics)
├── restaurants_scored.csv          # Final output dataset (Clusters + GPI Scores + Recommendations)
├── requirements.txt                # Python dependencies
├── Executive_Summary.docx          # Strategic summary for government stakeholders
├── Research_Paper.pdf              # Detailed methodology, EDA, and insights
└── README.md                       # Project documentation (this file)
