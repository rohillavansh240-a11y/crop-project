import streamlit as st
import pandas as pd
import plotly.express as px
from sklearn.linear_model import LinearRegression
import numpy as np

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="AgriVision Dashboard", layout="wide")

# ---------------- CUSTOM CSS ----------------
st.markdown("""
<style>
body {
    background-color: #0e1117;
    color: white;
}
.main-title {
    font-size: 40px;
    font-weight: bold;
    color: #00ffcc;
}
.card {
    background-color: #1c1f26;
    padding: 20px;
    border-radius: 15px;
    box-shadow: 0px 0px 10px rgba(0,255,200,0.2);
}
</style>
""", unsafe_allow_html=True)

# ---------------- TITLE ----------------
st.markdown('<p class="main-title">🌾 AgriVision: Crop Dashboard</p>', unsafe_allow_html=True)

# ---------------- LOAD DATA ----------------
@st.cache_data
def load_data():
    return pd.read_csv("crop_data.csv")

df = load_data()

# ---------------- SIDEBAR ----------------
st.sidebar.title("⚙️ Settings")

crop = st.sidebar.selectbox("Select Crop", df["Crop"].unique())
year_range = st.sidebar.slider("Select Year Range",
                               int(df["Year"].min()),
                               int(df["Year"].max()),
                               (2018, 2022))

# FILTER DATA
filtered = df[(df["Crop"] == crop) &
              (df["Year"] >= year_range[0]) &
              (df["Year"] <= year_range[1])]

# ---------------- METRICS ----------------
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.metric("📦 Total Production", f"{filtered['Production'].sum()} MT")
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.metric("💰 Avg Price", f"₹{int(filtered['Price'].mean())}")
    st.markdown('</div>', unsafe_allow_html=True)

with col3:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.metric("📅 Years Covered", f"{filtered['Year'].nunique()}")
    st.markdown('</div>', unsafe_allow_html=True)

# ---------------- CHARTS ----------------
st.subheader("📈 Price Trend")
fig1 = px.line(filtered, x="Year", y="Price", markers=True, color_discrete_sequence=["#00ffcc"])
st.plotly_chart(fig1, use_container_width=True)

st.subheader("🌱 Production Trend")
fig2 = px.bar(filtered, x="Year", y="Production", color="Production", color_continuous_scale="greens")
st.plotly_chart(fig2, use_container_width=True)

# ---------------- PREDICTION ----------------
st.subheader("🔮 Price Prediction")

# Prepare data
X = filtered["Year"].values.reshape(-1, 1)
y = filtered["Price"].values

if len(X) > 1:
    model = LinearRegression()
    model.fit(X, y)

    future_year = st.number_input("Enter Future Year", min_value=2023, max_value=2035, value=2025)

    prediction = model.predict([[future_year]])[0]

    st.success(f"Predicted Price for {future_year}: ₹{int(prediction)}")

    # Prediction graph
    future_years = np.array(range(int(df["Year"].min()), future_year + 1)).reshape(-1, 1)
    predicted_prices = model.predict(future_years)

    pred_df = pd.DataFrame({
        "Year": future_years.flatten(),
        "Predicted Price": predicted_prices
    })

    fig3 = px.line(pred_df, x="Year", y="Predicted Price",
                   title="Future Price Prediction",
                   color_discrete_sequence=["orange"])
    st.plotly_chart(fig3, use_container_width=True)

else:
    st.warning("Not enough data for prediction")

# ---------------- DATA TABLE ----------------
st.subheader("📋 Data Table")
st.dataframe(filtered, use_container_width=True)

# ---------------- DOWNLOAD ----------------
csv = filtered.to_csv(index=False).encode('utf-8')
st.download_button("⬇️ Download Data", csv, "filtered_data.csv", "text/csv")
