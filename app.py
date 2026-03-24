import streamlit as st
import pandas as pd
import plotly.express as px

# Page config
st.set_page_config(page_title="Crop Dashboard", layout="wide")

# Custom CSS (Modern UI)
st.markdown("""
<style>
.main {
    background-color: #0e1117;
}
h1, h2, h3, h4 {
    color: white;
}
.metric-box {
    background: #1c1f26;
    padding: 20px;
    border-radius: 15px;
    text-align: center;
    box-shadow: 0px 4px 10px rgba(0,0,0,0.3);
}
</style>
""", unsafe_allow_html=True)

# Title
st.title("🌾 Smart Crop Dashboard")

# Load data
data = pd.read_csv("crop_data.csv")

# ===== STATS =====
total_crops = data['Crop'].nunique()
avg_price = data['Price'].mean()
total_production = data['Production'].sum()
top_crop = data.groupby('Crop')['Production'].sum().idxmax()

# ===== STAT CARDS =====
col1, col2, col3, col4 = st.columns(4)

col1.markdown(f"<div class='metric-box'><h3>Total Crops</h3><h2>{total_crops}</h2></div>", unsafe_allow_html=True)
col2.markdown(f"<div class='metric-box'><h3>Avg Price</h3><h2>{avg_price:.2f}</h2></div>", unsafe_allow_html=True)
col3.markdown(f"<div class='metric-box'><h3>Total Production</h3><h2>{total_production:.0f}</h2></div>", unsafe_allow_html=True)
col4.markdown(f"<div class='metric-box'><h3>Top Crop</h3><h2>{top_crop}</h2></div>", unsafe_allow_html=True)

# ===== SIDEBAR =====
search = st.sidebar.text_input("🔍 Search Crop")
filtered = filtered[filtered['Crop'].str.contains(search, case=False, na=False)]
crop = st.sidebar.selectbox("Select Crop", data['Crop'].unique())
theme = st.sidebar.radio("Theme", ["Dark", "Light"])

filtered = csv = filtered.to_csv(index=False)
st.download_button("⬇️ Download Data", csv, "crop_data.csv")

# ===== CHARTS =====
st.markdown("## 📊 Analytics")

col5, col6 = st.columns(2)

# Production Chart
fig1 = px.bar(filtered, x='Year', y='Production', title="Production Volume", color='Production')
col5.plotly_chart(fig1, use_container_width=True)

# Price Chart
fig2 = px.line(filtered, x='Year', y='Price', title="Price Trend", markers=True)
col6.plotly_chart(fig2, use_container_width=True)

# ===== FULL WIDTH CHART =====
st.markdown("## 📦 Crop Distribution")

fig3 = px.pie(data, names='Crop', title="Crop Distribution")
st.plotly_chart(fig3, use_container_width=True)
