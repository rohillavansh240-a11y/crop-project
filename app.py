import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

st.set_page_config(layout="wide")

# ---------------- CSS ----------------
st.markdown("""
<style>
.main { background-color: #f5f7f9; }

/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: #ffffff;
    border-right: 1px solid #eee;
}

/* Top Bar */
.topbar {
    background: white;
    padding: 12px 20px;
    border-radius: 12px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
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

/* Buttons */
.stButton>button {
    border-radius: 10px;
    background-color: #2e7d32;
    color: white;
}
</style>
""", unsafe_allow_html=True)

# ---------------- Sidebar ----------------
st.sidebar.markdown("## 🌾 AgriDash")

menu = st.sidebar.radio("", [
    "Dashboard",
    "Crop Management",
    "Analytics"
])

# ---------------- Data ----------------
data = {
    "name": ["Wheat","Wheat","Wheat","Wheat","Rice","Sugarcane"],
    "year": [2021,2022,2023,2024,2024,2024],
    "price": [2015,2125,2275,2400,3000,1800],
    "production": [1095,1105,1120,1150,1500,500],
    "category": ["Grain","Grain","Grain","Grain","Grain","Sugar"],
    "region": ["India","India","India","India","India","India"]
}

df = pd.DataFrame(data)

# ---------------- Top Bar ----------------
col1, col2 = st.columns([3,1])

with col1:
    st.text_input("🔍 Search crops, regions...")

with col2:
    now = datetime.now()
    st.markdown(f"""
    <div class="topbar">
        <b>Spring Season {now.year}</b>
    </div>
    """, unsafe_allow_html=True)

# ---------------- DASHBOARD ----------------
if menu == "Dashboard":

    st.markdown("""
    <div class="banner">
        <h1>Agricultural Overview</h1>
        <p>Track crop performance, market prices, and production volumes</p>
    </div>
    """, unsafe_allow_html=True)

    st.write("")

    # KPI Cards
    c1, c2, c3, c4 = st.columns(4)

    c1.markdown(f'<div class="card"><h4>Total Crops</h4><h2>{len(df)}</h2></div>', unsafe_allow_html=True)
    c2.markdown(f'<div class="card"><h4>Average Price</h4><h2>${df["price"].mean():.2f}</h2></div>', unsafe_allow_html=True)
    c3.markdown(f'<div class="card"><h4>Total Production</h4><h2>{df["production"].sum():,}</h2></div>', unsafe_allow_html=True)
    c4.markdown(f'<div class="card"><h4>Top Performing</h4><h2>{df.iloc[df["production"].idxmax()]["name"]}</h2></div>', unsafe_allow_html=True)

    st.write("")

    # Charts
    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        fig = px.bar(df, x="name", y="production", title="Production Volumes")
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        fig = px.pie(df, names="category", title="Category Breakdown")
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.write("")

    # Line Chart (like your screenshot)
    st.markdown('<div class="card">', unsafe_allow_html=True)
    fig = px.line(df, x="year", y="price", color="name", markers=True, title="Market Price Comparison")
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ---------------- CROPS PAGE ----------------
elif menu == "Crop Management":

    st.title("🌱 Crop Database")

    col1, col2 = st.columns([3,1])

    with col1:
        search = st.text_input("Search crop...")

    with col2:
        st.button("➕ Add New Crop")

    if search:
        df = df[df["name"].str.contains(search, case=False)]

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.dataframe(df, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ---------------- ANALYTICS ----------------
elif menu == "Analytics":

    st.title("📈 Reports & Analytics")

    col1, col2 = st.columns(2)

    with col1:
        fig = px.histogram(df, x="price", title="Price Distribution")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = px.bar(df, x="region", y="production", title="Production by Region")
        st.plotly_chart(fig, use_container_width=True)
