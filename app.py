import streamlit as st
import pandas as pd
import plotly.express as px
import time

# Page config
st.set_page_config(page_title="Crop Dashboard", layout="wide")

# ---------- Fake Loading ----------
with st.spinner("Gathering harvest data..."):
    time.sleep(1)

# ---------- Load Data ----------
data = pd.read_csv("crop_data.csv")

# ---------- Stats ----------
total_crops = data['Crop'].nunique()
avg_price = data['Price'].mean()
total_production = data['Production'].sum()
top_crop = data.groupby('Crop')['Production'].sum().idxmax()

# ---------- Hero Section ----------
st.markdown("""
<div style="background: linear-gradient(90deg,#16a34a,#22c55e);
padding:30px;border-radius:20px;color:white">
<h1>Agricultural Overview</h1>
<p>Track crop performance, market prices, and production volumes.</p>
</div>
""", unsafe_allow_html=True)

# ---------- Stats Grid ----------
col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Crops", total_crops)
col2.metric("Avg Price", f"₹{avg_price:.2f}")
col3.metric("Total Production", f"{total_production}")
col4.metric("Top Crop", top_crop)

# ---------- Charts ----------
st.markdown("## 📊 Production Volume")

prod_data = data.groupby('Crop')['Production'].sum().reset_index()
fig1 = px.bar(prod_data, x='Crop', y='Production')
st.plotly_chart(fig1, use_container_width=True)

# ---------- Category Distribution ----------
st.markdown("## 🌾 Category Distribution")

if 'Category' in data.columns:
    cat_data = data['Category'].value_counts().reset_index()
    cat_data.columns = ['Category', 'Count']
    fig2 = px.pie(cat_data, names='Category', values='Count')
    st.plotly_chart(fig2, use_container_width=True)

# ---------- Price Trend ----------
st.markdown("## 💰 Price Trend")

if 'Year' in data.columns:
    fig3 = px.line(data, x='Year', y='Price', color='Crop')
    st.plotly_chart(fig3, use_container_width=True)
