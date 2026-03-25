import streamlit as st
import pandas as pd
import plotly.express as px
from sklearn.linear_model import LinearRegression
import numpy as np

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="🌾 Crop Dashboard", layout="wide")

# ---------------- LOAD DATA ----------------
@st.cache_data
def load_data():
    return pd.read_csv("crop_data.csv")

data = load_data()

# ---------------- SIDEBAR ----------------
st.sidebar.title("⚙️ Dashboard Settings")

theme = st.sidebar.radio("🎨 Theme", ["Dark", "Light"])
chart_type = st.sidebar.selectbox("📊 Chart Type", ["Line", "Bar"])
enable_prediction = st.sidebar.toggle("🤖 Enable Prediction", True)
show_table = st.sidebar.toggle("📋 Show Data Table", True)
enable_edit = st.sidebar.toggle("✏️ Enable Data Editing", False)

selected_crops = st.sidebar.multiselect(
    "🌱 Select Crops",
    options=data["Crop"].unique(),
    default=list(data["Crop"].unique())[:2]
)

year_range = st.sidebar.slider(
    "📅 Year Range",
    int(data["Year"].min()),
    int(data["Year"].max()),
    (int(data["Year"].min()), int(data["Year"].max()))
)

# ---------------- THEME ----------------
if theme == "Dark":
    st.markdown("""
        <style>
        .main { background-color: #0e1117; color: white; }
        </style>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
        <style>
        .main { background-color: white; color: black; }
        </style>
    """, unsafe_allow_html=True)

# ---------------- TITLE ----------------
st.title("🌾 Crop Price & Production Dashboard")

# ---------------- FILTER DATA ----------------
filtered_data = data[
    (data["Crop"].isin(selected_crops)) &
    (data["Year"].between(year_range[0], year_range[1]))
]

# ---------------- METRICS ----------------
col1, col2, col3 = st.columns(3)

col1.metric("🌱 Crops Selected", len(selected_crops))
col2.metric("📅 Years", f"{year_range[0]} - {year_range[1]}")
col3.metric("📊 Records", len(filtered_data))

# ---------------- CHART ----------------
st.subheader("📊 Price Trend")

if chart_type == "Line":
    fig = px.line(filtered_data, x="Year", y="Price", color="Crop", markers=True)
else:
    fig = px.bar(filtered_data, x="Year", y="Price", color="Crop")

st.plotly_chart(fig, use_container_width=True)

# ---------------- PREDICTION ----------------
if enable_prediction:
    st.subheader("🤖 Price Prediction (Next Year)")

    predictions = []

    for crop in selected_crops:
        crop_data = filtered_data[filtered_data["Crop"] == crop]

        if len(crop_data) > 1:
            X = crop_data["Year"].values.reshape(-1, 1)
            y = crop_data["Price"].values

            model = LinearRegression()
            model.fit(X, y)

            future_year = year_range[1] + 1
            pred = model.predict([[future_year]])[0]

            predictions.append([crop, future_year, round(pred, 2)])

    if predictions:
        pred_df = pd.DataFrame(predictions, columns=["Crop", "Year", "Predicted Price"])
        st.dataframe(pred_df)
    else:
        st.warning("Not enough data for prediction")

# ---------------- TABLE ----------------
if show_table:
    st.subheader("📋 Data Table")

    if enable_edit:
        edited_data = st.data_editor(filtered_data, use_container_width=True)
    else:
        st.dataframe(filtered_data, use_container_width=True)

# ---------------- DOWNLOAD ----------------
st.subheader("⬇️ Download Data")

csv = filtered_data.to_csv(index=False).encode("utf-8")

st.download_button(
    label="Download CSV",
    data=csv,
    file_name="filtered_crop_data.csv",
    mime="text/csv"
)
