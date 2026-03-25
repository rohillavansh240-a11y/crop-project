import os
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# ---------------- CONFIG ----------------
st.set_page_config(page_title="AgriDash Pro", layout="wide")

# ---------------- CSS ----------------
st.markdown("""
<style>
.main { background-color: #f5f7f9; }

section[data-testid="stSidebar"] {
    background-color: #ffffff;
    border-right: 1px solid #eee;
}

/* Banner */
.banner {
    background: linear-gradient(135deg, #1b5e20, #2e7d32);
    padding: 30px;
    border-radius: 20px;
    color: white;
}

/* Cards */
.card {
    background: white;
    padding: 20px;
    border-radius: 18px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.05);
}

/* Table */
.table-card {
    background: white;
    padding: 10px;
    border-radius: 15px;
}
</style>
""", unsafe_allow_html=True)

# ---------------- SIDEBAR ----------------
st.sidebar.markdown("## 🌾 AgriDash")

menu = st.sidebar.radio("", ["Dashboard","Crop Management","Analytics"])

st.sidebar.markdown("---")
st.sidebar.markdown("👤 Vansh Rohilla")
st.sidebar.caption("Farm Manager")

# ---------------- DATA ----------------
@st.cache_data
def load_data():
    data = {
        "name": ["Wheat","Rice","Sugarcane","Maize","Potato"],
        "year": [2021,2022,2023,2024,2024],
        "price": [2000,3000,1800,2500,1200],
        "production": [1000,1500,500,800,600],
        "category": ["Grain","Grain","Sugar","Grain","Vegetable"],
        "region": ["India","India","India","India","India"]
    }
    return pd.DataFrame(data)

df = load_data()

# ---------------- TOP BAR ----------------
col1, col2 = st.columns([3,1])

with col1:
    search = st.text_input("🔍 Search crops, regions...")

with col2:
    now = datetime.now()
    st.markdown(f"**Spring Season {now.year}**")

if search:
    df = df[df["name"].str.contains(search, case=False)]

# ---------------- DASHBOARD ----------------
if menu == "Dashboard":

    st.markdown("""
    <div class="banner">
        <h1>Agricultural Overview</h1>
        <p>Track crop performance, prices and production</p>
    </div>
    """, unsafe_allow_html=True)

    st.write("")

    # KPI
    c1,c2,c3,c4 = st.columns(4)

    c1.markdown(f'<div class="card"><h4>Total Crops</h4><h2>{len(df)}</h2></div>', unsafe_allow_html=True)
    c2.markdown(f'<div class="card"><h4>Avg Price</h4><h2>₹{df["price"].mean():.0f}</h2></div>', unsafe_allow_html=True)
    c3.markdown(f'<div class="card"><h4>Total Production</h4><h2>{df["production"].sum()}</h2></div>', unsafe_allow_html=True)
    c4.markdown(f'<div class="card"><h4>Top Crop</h4><h2>{df.iloc[df["production"].idxmax()]["name"]}</h2></div>', unsafe_allow_html=True)

    st.write("")

    # Charts
    col1,col2 = st.columns(2)

    with col1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        fig = px.bar(df, x="name", y="production", title="Production Volume")
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        fig = px.pie(df, names="category", title="Category Breakdown")
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.write("")

    # Line Chart
    st.markdown('<div class="card">', unsafe_allow_html=True)
    fig = px.line(df, x="year", y="price", color="name", markers=True, title="Price Trend")
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ---------------- CROPS ----------------
elif menu == "Crop Management":

    st.title("🌱 Crop Database")

    with st.expander("➕ Add New Crop"):
        name = st.text_input("Crop Name")
        price = st.number_input("Price")
        prod = st.number_input("Production")
        if st.button("Save"):
            new_row = pd.DataFrame([{
                "name": name,
                "price": price,
                "production": prod,
                "year": datetime.now().year,
                "category": "Custom",
                "region": "India"
            }])
            df = pd.concat([df, new_row], ignore_index=True)
            st.success("Added Successfully")

    st.markdown('<div class="table-card">', unsafe_allow_html=True)
    st.dataframe(df, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ---------------- ANALYTICS ----------------
elif menu == "Analytics":

    st.title("📈 Reports & Analytics")

    col1,col2 = st.columns(2)

    with col1:
        fig = px.histogram(df, x="price", title="Price Distribution")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = px.bar(df, x="region", y="production", title="Production by Region")
        st.plotly_chart(fig, use_container_width=True)
