import streamlit as st
import pandas as pd
import plotly.express as px
from sklearn.linear_model import LinearRegression
import numpy as np

# ---------------- CONFIG ----------------
st.set_page_config(page_title="AgriVision Pro", layout="wide")

# ---------------- THEME SETTINGS ----------------
st.sidebar.title("⚙️ Dashboard Settings")

theme = st.sidebar.selectbox("Theme", ["Dark", "Light"])
show_prediction = st.sidebar.toggle("Enable Prediction", True)
show_table = st.sidebar.toggle("Show Data Table", True)
edit_data = st.sidebar.toggle("Enable Data Editing", False)
chart_type = st.sidebar.selectbox("Chart Type", ["Line", "Bar"])

# ---------------- THEME CSS ----------------
if theme == "Dark":
    st.markdown("""
    <style>
    body { background-color: #0e1117; color: white; }
    .card {
        background-color: #1c1f26;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0px 0px 10px rgba(0,255,200,0.2);
    }
    </style>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <style>
    body { background-color: #ffffff; color: black; }
    .card {
        background-color: #f5f5f5;
        padding: 20px;
        border-radius: 15px;
    }
    </style>
    """, unsafe_allow_html=True)

# ---------------- TITLE ----------------
st.title("🌾 AgriVision Pro Dashboard")

# ---------------- LOAD DATA ----------------
@st.cache_data
def load_data():
    return pd.read_csv("crop_data.csv")

df = load_data()

# ---------------- FILTERS ----------------
st.sidebar.subheader("📊 Filters")

crop = st.sidebar.multiselect("Select Crop", df["Crop"].unique(), default=df["Crop"].unique())

year_range = st.sidebar.slider(
    "Year Range",
    int(df["Year"].min()),
    int(df["Year"].max()),
    (2018, 2022)
)

# Filter Data
filtered = df[
    (df["Crop"].isin(crop)) &
    (df["Year"] >= year_range[0]) &
    (df["Year"] <= year_range[1])
]

# ---------------- METRICS ----------------
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.metric("📦 Production", int(filtered["Production"].sum()))
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.metric("💰 Avg Price", f"₹{int(filtered['Price'].mean())}")
    st.markdown('</div>', unsafe_allow_html=True)

with col3:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.metric("📅 Years", filtered["Year"].nunique())
    st.markdown('</div>', unsafe_allow_html=True)

# ---------------- CHART ----------------
st.subheader("📈 Trend Analysis")

if chart_type == "Line":
    fig = px.line(filtered, x="Year", y="Price", color="Crop", markers=True)
else:
    fig = px.bar(filtered, x="Year", y="Price", color="Crop")

st.plotly_chart(fig, use_container_width=True)

# ---------------- PRODUCTION CHART ----------------
st.subheader("🌱 Production")

fig2 = px.area(filtered, x="Year", y="Production", color="Crop")
st.plotly_chart(fig2, use_container_width=True)

# ---------------- PREDICTION ----------------
if show_prediction:
    st.subheader("🔮 Price Prediction")

    if len(filtered) > 1:
        X = filtered["Year"].values.reshape(-1, 1)
        y = filtered["Price"].values

        model = LinearRegression()
        model.fit(X, y)

        future_year = st.number_input("Future Year", 2023, 2035, 2025)

        pred = model.predict([[future_year]])[0]

        st.success(f"Predicted Price: ₹{int(pred)}")

# ---------------- DATA TABLE ----------------
if show_table:
    st.subheader("📋 Data Table")

    if edit_data:
        edited_df = st.data_editor(filtered)
    else:
        st.dataframe(filtered)

# ---------------- DOWNLOAD ----------------
csv = filtered.to_csv(index=False).encode("utf-8")
st.download_button("⬇️ Download CSV", csv, "data.csv", "text/csv")
