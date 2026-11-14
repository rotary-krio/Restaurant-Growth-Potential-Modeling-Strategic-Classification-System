
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

# ============================================================
# 1. PAGE CONFIG & CUSTOM CSS (GLASSMORPHISM THEME)
# ============================================================
st.set_page_config(page_title="SkyCity Growth Intelligence", page_icon="✨", layout="wide")

# Custom CSS for glowing hover effects and modern UI
st.markdown("""
<style>
    /* Dark Theme Background */
    .stApp {
        background-color: #0e1117;
        color: #ffffff;
    }
    
    /* Custom KPI Cards */
    .kpi-container {
        display: flex;
        justify-content: space-between;
        gap: 15px;
        margin-bottom: 25px;
    }
    .kpi-card {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 15px;
        padding: 20px;
        flex: 1;
        text-align: center;
        backdrop-filter: blur(10px);
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    .kpi-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 20px rgba(0, 255, 255, 0.15);
        border-color: rgba(0, 255, 255, 0.4);
    }
    .kpi-title {
        font-size: 14px;
        color: #a0aab5;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 10px;
    }
    .kpi-value {
        font-size: 32px;
        font-weight: 700;
        color: #00e5ff;
        text-shadow: 0 0 10px rgba(0, 229, 255, 0.3);
    }
    
    /* Tab Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 20px;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 10px 20px;
        background-color: rgba(255, 255, 255, 0.02);
        border-radius: 10px;
        transition: all 0.3s;
    }
    .stTabs [data-baseweb="tab"]:hover {
        background-color: rgba(0, 229, 255, 0.1);
        color: #00e5ff;
    }
    .stTabs [aria-selected="true"] {
        background-color: rgba(0, 229, 255, 0.15);
        border-bottom: 2px solid #00e5ff;
        color: #00e5ff;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# 2. LOAD DATA
# ============================================================
st.title("✨ Restaurant Growth Potential & Strategic Classification")
st.markdown("<p style='color: #a0aab5;'>SkyCity Auckland Restaurants & Bars — Advanced Analytics Dashboard</p>", unsafe_allow_html=True)

script_dir = os.path.dirname(os.path.abspath(__file__))
data_path = os.path.join(script_dir, "restaurants_scored.csv")

@st.cache_data
def load_data():
    return pd.read_csv(data_path)

try:
    df = load_data()
except FileNotFoundError:
    st.error("❌ File 'restaurants_scored.csv' not found. Please run `python analysis.py` first!")
    st.stop()

# ============================================================
# 3. SIDEBAR FILTERS
# ============================================================
st.sidebar.header("🔍 Dashboard Filters")
st.sidebar.markdown("---")

subregions = st.sidebar.multiselect("Subregion", sorted(df["Subregion"].unique()))
cuisines = st.sidebar.multiselect("Cuisine Type", sorted(df["CuisineType"].unique()))
segments = st.sidebar.multiselect("Segment", sorted(df["Segment"].unique()))
gpi_range = st.sidebar.slider("GPI Percentile Range", 0, 100, (0, 100))

# Filter logic
f = df.copy()
if subregions: f = f[f["Subregion"].isin(subregions)]
if cuisines: f = f[f["CuisineType"].isin(cuisines)]
if segments: f = f[f["Segment"].isin(segments)]
f = f[f["GPI_100"].between(*gpi_range)]

st.sidebar.markdown(f"<div style='text-align: center; color: #00e5ff; font-weight: bold; margin-top: 20px;'>Showing {len(f)} restaurants</div>", unsafe_allow_html=True)

# ============================================================
# 4. ANIMATED KPI CARDS
# ============================================================
st.markdown(f"""
<div class="kpi-container">
    <div class="kpi-card">
        <div class="kpi-title">Total Restaurants</div>
        <div class="kpi-value">{len(f)}</div>
    </div>
    <div class="kpi-card">
        <div class="kpi-title">Avg GPI Score</div>
        <div class="kpi-value">{f.GPI_100.mean():.1f}</div>
    </div>
    <div class="kpi-card">
        <div class="kpi-title">Avg Net Margin</div>
        <div class="kpi-value">{f.NetMargin.mean()*100:.1f}%</div>
    </div>
    <div class="kpi-card">
        <div class="kpi-title">Avg Monthly Profit</div>
        <div class="kpi-value">${f.TotalNetProfit.mean():,.0f}</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ============================================================
# 5. TABS (Enhanced Visuals)
# ============================================================
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🗺️ Cluster Map", "📊 GPI Scorecards", "🕸️ Radar Charts", "🎯 Strategy Panel", "⚖️ Compare"
])

# --- TAB 1: CLUSTER MAP ---
with tab1:
    st.subheader("Interactive Cluster Map")
    st.markdown("<p style='color: #a0aab5;'>Hover over the glowing dots to see restaurant details. The UMAP algorithm places similar restaurants close together.</p>", unsafe_allow_html=True)

    fig = px.scatter(
        f, x="umap_x", y="umap_y", color="cluster_label", hover_name="RestaurantName",
        hover_data={
            "Subregion": True, "Segment": True, "GPI_100": ":.1f", 
            "TotalNetProfit": ":,.0f", "umap_x": False, "umap_y": False
        },
        color_discrete_sequence=px.colors.qualitative.Pastel,
        template="plotly_dark"
    )
    # Enhance hover effect with marker sizing
    fig.update_traces(
        marker=dict(size=12, line=dict(width=1, color='white'), opacity=0.9),
        hoverlabel=dict(bgcolor="black", font_size=14, font_family="Arial")
    )
    fig.update_layout(height=600, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Cuisine Breakdown by Cluster")
    sun = px.sunburst(
        f, path=["cluster_label", "CuisineType"], values="MonthlyOrders",
        color="cluster_label", color_discrete_sequence=px.colors.qualitative.Pastel,
        template="plotly_dark"
    )
    sun.update_layout(height=500, paper_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(sun, use_container_width=True)

# --- TAB 2: GPI SCORECARDS ---
with tab2:
    st.subheader("Top & Bottom Performers")
    col1, col2 = st.columns(2)

    with col1:
        st.write("🏆 **Top 20 (Scale-Ready)**")
        top20 = f.nlargest(20, "GPI_100")[["RestaurantName", "cluster_label", "GPI_100"]]
        fig_top = px.bar(
            top20, x="GPI_100", y="RestaurantName", orientation="h", 
            color="GPI_100", color_continuous_scale="Viridis", template="plotly_dark"
        )
        fig_top.update_layout(height=600, yaxis=dict(autorange="reversed"), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        fig_top.update_traces(marker=dict(line=dict(width=1, color='white')))
        st.plotly_chart(fig_top, use_container_width=True)

    with col2:
        st.write("⚠️ **Bottom 20 (Restructure)**")
        bot20 = f.nsmallest(20, "GPI_100")[["RestaurantName", "cluster_label", "GPI_100"]]
        fig_bot = px.bar(
            bot20, x="GPI_100", y="RestaurantName", orientation="h", 
            color="GPI_100", color_continuous_scale="Inferno", template="plotly_dark"
        )
        fig_bot.update_layout(height=600, yaxis=dict(autorange="reversed"), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        fig_bot.update_traces(marker=dict(line=dict(width=1, color='white')))
        st.plotly_chart(fig_bot, use_container_width=True)

# --- TAB 3: RADAR CHARTS ---
with tab3:
    st.subheader("Restaurant DNA Comparison")
    st.markdown("<p style='color: #a0aab5;'>Select up to 3 restaurants to compare their 5 core growth KPIs.</p>", unsafe_allow_html=True)
    
    selected = st.multiselect("Select restaurants", sorted(f["RestaurantName"].unique()), max_selections=3)

    kpi_names = ["Scale", "CostDiscipline", "ChannelBalance", "ExpansionHeadroom", "RevenueQuality"]
    pretty_names = ["Scale", "Cost Discipline", "Channel Balance", "Expansion Headroom", "Revenue Quality"]

    if selected:
        fig_radar = go.Figure()
        colors = ['#00e5ff', '#ff00ea', '#00ff7f'] # Cyan, Pink, Neon Green
        
        for i, name in enumerate(selected):
            row = f[f["RestaurantName"] == name].iloc[0]
            values = [row[k] for k in kpi_names]
            
            # Simple RGBA strings for Plotly fills
            fill_colors = ['rgba(0, 229, 255, 0.2)', 'rgba(255, 0, 234, 0.2)', 'rgba(0, 255, 127, 0.2)']
            
            fig_radar.add_trace(go.Scatterpolar(
                r=values + [values[0]], 
                theta=pretty_names + [pretty_names[0]], 
                fill="toself", 
                name=name,
                line=dict(color=colors[i], width=3),
                fillcolor=fill_colors[i]
            ))
            
        fig_radar.update_layout(
            polar=dict(
                bgcolor="rgba(255,255,255,0.05)",
                radialaxis=dict(visible=True, range=[0, 1], gridcolor="rgba(255,255,255,0.1)"),
                angularaxis=dict(gridcolor="rgba(255,255,255,0.1)")
            ),
            template="plotly_dark",
            height=600,
            paper_bgcolor="rgba(0,0,0,0)",
            showlegend=True
        )
        st.plotly_chart(fig_radar, use_container_width=True)
    else:
        st.info("👆 Select at least one restaurant above.")

# --- TAB 4: STRATEGY PANEL ---
with tab4:
    st.subheader("Strategic Recommendations")
    
    rec_counts = f["Recommendation"].value_counts().reset_index()
    rec_counts.columns = ["Recommendation", "Count"]
    
    fig_rec = px.bar(
        rec_counts, x="Count", y="Recommendation", orientation="h",
        color="Count", color_continuous_scale="Teal", template="plotly_dark"
    )
    fig_rec.update_layout(height=400, yaxis=dict(autorange="reversed"), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    fig_rec.update_traces(marker=dict(line=dict(width=1, color='white')))
    st.plotly_chart(fig_rec, use_container_width=True)

    st.subheader("Cluster vs. Strategy Heatmap")
    heat = pd.crosstab(f["cluster_label"], f["Recommendation"])
    fig_heat = px.imshow(
        heat, text_auto=True, aspect="auto", color_continuous_scale="Teal", template="plotly_dark"
    )
    fig_heat.update_layout(height=400, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig_heat, use_container_width=True)

    csv = f[["RestaurantName", "cluster_label", "GPI_100", "Recommendation"]].to_csv(index=False)
    st.download_button(
        label="⬇️ Download Strategy Report (CSV)",
        data=csv,
        file_name="strategy_recommendations.csv",
        mime="text/csv",
    )

# --- TAB 5: COMPARE ---
with tab5:
    st.subheader("Side-by-Side Financial Comparison")
    picks = st.multiselect("Pick 2-5 restaurants to compare", sorted(f["RestaurantName"].unique()), max_selections=5)

    if len(picks) >= 2:
        compare = f[f["RestaurantName"].isin(picks)][[
            "RestaurantName", "cluster_label", "GPI_100", "TotalNetProfit", 
            "NetMargin", "AggregatorSharePct", "CostLoad", "MonthlyOrders", "AOV"
        ]].set_index("RestaurantName")
        
        # FIXED: Removed background_gradient styling to prevent KeyError on duplicate names
        st.dataframe(compare.round(3), use_container_width=True)

        long = compare.reset_index().melt(id_vars="RestaurantName", value_vars=["GPI_100", "TotalNetProfit", "NetMargin"])
        fig_bar = px.bar(
            long, x="RestaurantName", y="value", color="variable", barmode="group",
            template="plotly_dark", color_discrete_sequence=px.colors.qualitative.Pastel
        )
        fig_bar.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.info("👆 Pick at least 2 restaurants above to generate the comparison view.")
