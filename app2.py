# app_fixed_map.py

import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(
    page_title="Japan Inbound Immigration Dashboard",
    layout="wide"
)

# -----------------------------
# LOAD DATA
# -----------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("japan_immigration_statistics_inbound.csv")
    return df

df = load_data()

# -----------------------------
# PREPROCESSING
# -----------------------------
df_long = df.melt(id_vars=["year"], var_name="country", value_name="visitors")

exclude_cols = ["total", "stateless", "unknown_other"]
df_long = df_long[~df_long["country"].isin(exclude_cols)]

df_long = df_long.dropna()
df_long["country"] = df_long["country"].str.replace("_", " ").str.title()

# Limit years
df_long = df_long[(df_long["year"] >= 1950) & (df_long["year"] <= 2005)]

# -----------------------------
# REGION MAPPING
# -----------------------------
region_map = {
    "Asia": ["China", "South Korea", "Thailand", "India"],
    "Europe": ["France", "Germany", "United Kingdom"],
    "Americas": ["United States", "Canada", "Brazil"],
    "Oceania": ["Australia", "New Zealand"],
}

def assign_region(country):
    for reg, countries in region_map.items():
        if country in countries:
            return reg
    return "Other"

df_long["region"] = df_long["country"].apply(assign_region)

# -----------------------------
# SIDEBAR
# -----------------------------
st.sidebar.title("🔍 Filters")

year_range = st.sidebar.slider(
    "Year Range",
    1950,
    2005,
    (1950, 2005)
)

selected_regions = st.sidebar.multiselect(
    "Select Region(s)",
    options=df_long["region"].unique(),
    default=df_long["region"].unique()
)

filtered_df = df_long[
    (df_long["year"] >= year_range[0]) &
    (df_long["year"] <= year_range[1]) &
    (df_long["region"].isin(selected_regions))
]

# -----------------------------
# TITLE
# -----------------------------
st.title("🌏 Japan Inbound Immigration Dashboard")
st.markdown("Interactive analysis of visitor flows to Japan (1950–2005).")

# -----------------------------
# KPI CARDS
# -----------------------------
total_visitors = int(filtered_df["visitors"].sum())

top_country = (
    filtered_df.groupby("country")["visitors"]
    .sum()
    .idxmax()
)

top_value = (
    filtered_df.groupby("country")["visitors"]
    .sum()
    .max()
)

col1, col2, col3 = st.columns(3)

col1.metric("Total Visitors", f"{total_visitors:,}")
col2.metric("Top Country", top_country)
col3.metric("Visitors from Top Country", f"{top_value:,}")

st.markdown("---")

# -----------------------------
# COLOR SCALE FIX (🔥 IMPORTANT)
# -----------------------------
COLOR_SCALE = "Blues"

# -----------------------------
# LAYOUT
# -----------------------------
col_left, col_right = st.columns(2)

# -----------------------------
# CHOROPLETH MAP (FIXED)
# -----------------------------
with col_left:
    st.subheader("🌍 Visitor Distribution by Country")

    map_df = filtered_df.groupby("country")["visitors"].sum().reset_index()

    # 🔥 LOG TRANSFORMATION (KEY FIX)
    map_df["visitors_log"] = np.log1p(map_df["visitors"])

    fig_map = px.choropleth(
        map_df,
        locations="country",
        locationmode="country names",
        color="visitors_log",  # use log scale
        color_continuous_scale=COLOR_SCALE,
        labels={"visitors_log": "Visitors (log scale)"},
    )

    fig_map.update_traces(
        hovertemplate="<b>%{location}</b><br>Visitors: %{customdata:,}",
        customdata=map_df["visitors"]
    )

    fig_map.update_layout(margin=dict(l=0, r=0, t=30, b=0))

    st.plotly_chart(fig_map, use_container_width=True)

# -----------------------------
# LINE CHART
# -----------------------------
with col_right:
    st.subheader("📈 Trend Over Time")

    line_df = filtered_df.groupby("year")["visitors"].sum().reset_index()

    fig_line = px.line(
        line_df,
        x="year",
        y="visitors",
        markers=True,
    )

    fig_line.update_traces(
        hovertemplate="Year: %{x}<br>Visitors: %{y:,}"
    )

    fig_line.update_layout(
        xaxis_title="Year",
        yaxis_title="Visitors",
    )

    st.plotly_chart(fig_line, use_container_width=True)

# -----------------------------
# SECOND ROW
# -----------------------------
col_bottom_left, col_bottom_right = st.columns(2)

# -----------------------------
# BAR CHART
# -----------------------------
with col_bottom_left:
    st.subheader("🏆 Top 10 Countries")

    top_df = (
        filtered_df.groupby("country")["visitors"]
        .sum()
        .nlargest(10)
        .reset_index()
    )

    fig_bar = px.bar(
        top_df,
        x="visitors",
        y="country",
        orientation="h",
        text="visitors",
        color="visitors",
        color_continuous_scale=COLOR_SCALE
    )

    fig_bar.update_layout(
        yaxis=dict(autorange="reversed"),
        xaxis_title="Visitors",
        yaxis_title=""
    )

    st.plotly_chart(fig_bar, use_container_width=True)

# -----------------------------
# PIE CHART
# -----------------------------
with col_bottom_right:
    st.subheader("🥧 Regional Share")

    pie_df = filtered_df.groupby("region")["visitors"].sum().reset_index()

    fig_pie = px.pie(
        pie_df,
        names="region",
        values="visitors",
        hole=0.4
    )

    fig_pie.update_traces(
        textinfo="percent+label",
        hovertemplate="%{label}: %{value:,} visitors"
    )

    st.plotly_chart(fig_pie, use_container_width=True)

# -----------------------------
# FOOTER
# -----------------------------
st.markdown("---")
st.caption("Data Source: Kaggle | Map improved using log scale to reduce skew")