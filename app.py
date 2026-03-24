import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Page config
st.set_page_config(page_title="Crop Dashboard", layout="wide")

# Title / Hero Section
st.title("🌾 Agricultural Overview")
st.markdown("Track crop performance, market prices, and production volumes")

# Load data
data = pd.read_csv("crop_data.csv")

# ===== STATS =====
total_crops = data['Crop'].nunique()
avg_price = data['Price'].mean()
total_production = data['Production'].sum()
top_crop = data.groupby('Crop')['Production'].sum().idxmax()

# ===== STAT CARDS =====
col1, col2, col3, col4 = st.columns(4)

col1.metric("🌱 Total Crops", total_crops)
col2.metric("💰 Avg Price", f"{avg_price:.2f}")
col3.metric("⚖️ Total Production", f"{total_production:.0f}")
col4.metric("📈 Top Crop", top_crop)

# ===== SIDEBAR =====
st.sidebar.header("Filter")
crop = st.sidebar.selectbox("Select Crop", data['Crop'].unique())

filtered = data[data['Crop'] == crop]

# ===== CHART 1: Production =====
st.subheader("📊 Production Volume")

fig1, ax1 = plt.subplots()
ax1.bar(filtered['Year'], filtered['Production'])
ax1.set_xlabel("Year")
ax1.set_ylabel("Production")

st.pyplot(fig1)

# ===== CHART 2: Price Trend =====
st.subheader("💰 Price Trend")

fig2, ax2 = plt.subplots()
ax2.plot(filtered['Year'], filtered['Price'])
ax2.set_xlabel("Year")
ax2.set_ylabel("Price")

st.pyplot(fig2)

# ===== CHART 3: Category Distribution =====
st.subheader("📦 Crop Distribution")

dist = data['Crop'].value_counts()

fig3, ax3 = plt.subplots()
ax3.pie(dist, labels=dist.index, autopct='%1.1f%%')

st.pyplot(fig3)
