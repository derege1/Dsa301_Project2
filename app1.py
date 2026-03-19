# app.py

import streamlit as st
import pandas as pd
import plotly.express as px

# -----------------------------
# Page Config
# -----------------------------
st.set_page_config(
    page_title="Japan Inbound Immigration Dashboard",
    layout="wide"
)

# -----------------------------
# Load Data
# -----------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("japan_immigration_statistics_inbound.csv")
    return df

df = load_data()

# -----------------------------
# Data Preprocessing
# -----------------------------
# Convert wide → long format
df_long = df.melt(id_vars=["year"], var_name="country", value_name="visitors")

# Remove totals and irrelevant columns
exclude_cols = ["total", "stateless", "unknown_other"]
df_long = df_long[~df_long["country"].isin(exclude_cols)]

# Drop missing values
df_long = df_long.dropna()

# Capitalize country names
df_long["country"] = df_long["country"].str.replace("_", " ").str.title()

# -----------------------------
# Sidebar Filters
# -----------------------------
st.sidebar.title("🔍 Filters")

year_range = st.sidebar.slider(
    "Year Range",
    1950,   # ✅ fixed min
    2005,   # ✅ fixed max
    (1950, 2005)
)

# Simple region grouping (can be improved if dataset has explicit mapping)
region_map = {
    "Asia": ["China", "South Korea", "Thailand", "India"],
    "Europe": ["France", "Germany", "United Kingdom"],
    "Americas": ["United States", "Canada", "Brazil"],
    "Oceania": ["Australia", "New Zealand"],
}

region = st.sidebar.selectbox(
    "Select Region",
    ["All"] + list(region_map.keys())
)

# Apply filters
filtered_df = df_long[
    (df_long["year"] >= year_range[0]) &
    (df_long["year"] <= year_range[1])
]

if region != "All":
    filtered_df = filtered_df[
        filtered_df["country"].isin(region_map[region])
    ]

# -----------------------------
# Title
# -----------------------------
st.title("🌏 Japan Inbound Immigration Dashboard")
st.markdown("Explore visitor trends to Japan by country and region over time.")

# -----------------------------
# Choropleth Map
# -----------------------------
st.subheader("🌍 Global Visitor Distribution")

map_df = filtered_df.groupby("country")["visitors"].sum().reset_index()

fig_map = px.choropleth(
    map_df,
    locations="country",
    locationmode="country names",
    color="visitors",
    color_continuous_scale="Blues",
    title="Visitor Counts by Country"
)

st.plotly_chart(fig_map, use_container_width=True)

# -----------------------------
# Line Chart (Trends)
# -----------------------------
st.subheader("📈 Visitor Trends Over Time")

line_df = filtered_df.groupby(["year"])["visitors"].sum().reset_index()

fig_line = px.line(
    line_df,
    x="year",
    y="visitors",
    markers=True,
    title="Total Visitors Over Time"
)

st.plotly_chart(fig_line, use_container_width=True)

# -----------------------------
# Top 10 Countries Bar Chart
# -----------------------------
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
    title="Top 10 Countries by Visitors",
    text="visitors"
)

fig_bar.update_layout(yaxis=dict(autorange="reversed"))

st.plotly_chart(fig_bar, use_container_width=True)

# -----------------------------
# Pie Chart (Optional)
# -----------------------------
st.subheader("🥧 Regional Distribution")

# Simple grouping (approximation)
def assign_region(country):
    for reg, countries in region_map.items():
        if country in countries:
            return reg
    return "Other"

filtered_df["region"] = filtered_df["country"].apply(assign_region)

pie_df = filtered_df.groupby("region")["visitors"].sum().reset_index()

fig_pie = px.pie(
    pie_df,
    names="region",
    values="visitors",
    title="Visitors by Region"
)

st.plotly_chart(fig_pie, use_container_width=True)

# -----------------------------
# Footer
# -----------------------------
st.markdown("---")
st.caption("Data Source: Kaggle - Japan Inbound Immigration by Nationality")