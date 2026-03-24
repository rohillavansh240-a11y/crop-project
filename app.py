import streamlit as st
import pandas as pd
import plotly.express as px
import time

# ---------- Page Config ----------
st.set_page_config(page_title="Crop Dashboard", layout="wide")

# ---------- Loading ----------
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
<div style="
background: linear-gradient(90deg,#16a34a,#22c55e);
padding:40px;
border-radius:25px;
color:white;
box-shadow:0 10px 30px rgba(0,0,0,0.2);
">
<h1 style="font-size:40px;">🌾 Agricultural Overview</h1>
<p style="font-size:18px;opacity:0.9;">
Track crop performance, market prices, and production volumes.
</p>
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ---------- Stats Cards ----------
col1, col2, col3, col4 = st.columns(4)

col1.markdown(f"""
<div style="background:#111;padding:20px;border-radius:15px">
<h4>🌱 Total Crops</h4>
<h2>{total_crops}</h2>
</div>
""", unsafe_allow_html=True)

col2.markdown(f"""
<div style="background:#111;padding:20px;border-radius:15px">
<h4>💰 Avg Price</h4>
<h2>₹{avg_price:.2f}</h2>
</div>
""", unsafe_allow_html=True)

col3.markdown(f"""
<div style="background:#111;padding:20px;border-radius:15px">
<h4>⚖️ Production</h4>
<h2>{total_production}</h2>
</div>
""", unsafe_allow_html=True)

col4.markdown(f"""
<div style="background:#111;padding:20px;border-radius:15px">
<h4>📈 Top Crop</h4>
<h2>{top_crop}</h2>
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ---------- Charts Grid ----------
colA, colB = st.columns([2,1])

# Production Chart (big)
with colA:
    st.markdown("### 📊 Production Volumes")
    prod_data = data.groupby('Crop')['Production'].sum().reset_index()
    fig1 = px.bar(prod_data, x='Crop', y='Production')
    st.plotly_chart(fig1, use_container_width=True)

# Category Chart
with colB:
    st.markdown("### 🌾 Category Breakdown")
    if 'Category' in data.columns:
        cat_data = data['Category'].value_counts().reset_index()
        cat_data.columns = ['Category', 'Count']
        fig2 = px.pie(cat_data, names='Category', values='Count')
        st.plotly_chart(fig2, use_container_width=True)

# Full Width Price Chart
st.markdown("### 💰 Market Price Comparison")

if 'Year' in data.columns:
    fig3 = px.line(data, x='Year', y='Price', color='Crop')
    st.plotly_chart(fig3, use_container_width=True)
