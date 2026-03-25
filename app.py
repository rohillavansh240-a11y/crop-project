import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

st.set_page_config(layout="wide")

# ---------------- CSS ----------------
st.markdown("""
<style>
.main { background-color: #f5f7f9; }

section[data-testid="stSidebar"] {
    background-color: #ffffff;
    border-right: 1px solid #eee;
}

.banner {
    background: linear-gradient(135deg, #1b5e20, #2e7d32);
    padding: 30px;
    border-radius: 20px;
    color: white;
}

.card {
    background: white;
    padding: 20px;
    border-radius: 18px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.05);
}

.topbar {
    background: white;
    padding: 10px;
    border-radius: 10px;
}
</style>
""", unsafe_allow_html=True)

# ---------------- SESSION MENU ----------------
if "menu" not in st.session_state:
    st.session_state.menu = "Dashboard"

# ---------------- SIDEBAR ----------------
st.sidebar.markdown("## 🌾 AgriDash")

menu = st.sidebar.radio(
    "",
    ["Dashboard", "Crop Management", "Analytics", "Settings"],
    index=["Dashboard", "Crop Management", "Analytics", "Settings"].index(st.session_state.menu)
)

st.session_state.menu = menu

# ---------------- SIDEBAR PROFILE ----------------
st.sidebar.markdown("---")

st.sidebar.markdown("""
<div style="background:#f5efe6;padding:15px;border-radius:15px;">
    <div style="display:flex;align-items:center;">
        <div style="background:#cdeac0;border-radius:50%;width:40px;height:40px;
        display:flex;align-items:center;justify-content:center;font-weight:bold;margin-right:10px;">
        VR
        </div>
        <div>
            <b>Vansh Rohilla</b><br>
            <small>Farm Manager</small>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

if st.sidebar.button("⚙️ Settings"):
    st.session_state.menu = "Settings"

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
    st.markdown(f'<div class="topbar"><b>Spring Season {now.year}</b></div>', unsafe_allow_html=True)

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

    c1,c2,c3,c4 = st.columns(4)

    # Safe Top Crop
    if not df.empty and "production" in df.columns:
        top_crop = df.loc[df["production"].idxmax(), "name"]
    else:
        top_crop = "N/A"

    c1.markdown(f'<div class="card"><h4>Total Crops</h4><h2>{len(df)}</h2></div>', unsafe_allow_html=True)
    c2.markdown(f'<div class="card"><h4>Avg Price</h4><h2>₹{df["price"].mean():.0f}</h2></div>', unsafe_allow_html=True)
    c3.markdown(f'<div class="card"><h4>Total Production</h4><h2>{df["production"].sum()}</h2></div>', unsafe_allow_html=True)
    c4.markdown(f'<div class="card"><h4>Top Crop</h4><h2>{top_crop}</h2></div>', unsafe_allow_html=True)

    st.write("")

    col1,col2 = st.columns(2)

    with col1:
        fig = px.bar(df, x="name", y="production")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = px.pie(df, names="category")
        st.plotly_chart(fig, use_container_width=True)

    fig = px.line(df, x="year", y="price", color="name", markers=True)
    st.plotly_chart(fig, use_container_width=True)

# ---------------- CROP MANAGEMENT ----------------
elif menu == "Crop Management":

    st.title("🌱 Crop Database")

    with st.expander("➕ Add New Crop"):
        name = st.text_input("Crop Name")
        price = st.number_input("Price")
        production = st.number_input("Production")

        if st.button("Save Crop"):
            new_row = pd.DataFrame([{
                "name": name,
                "price": price,
                "production": production,
                "year": datetime.now().year,
                "category": "Custom",
                "region": "India"
            }])
            df = pd.concat([df, new_row], ignore_index=True)
            st.success("Crop Added ✅")

    st.dataframe(df, use_container_width=True)

# ---------------- ANALYTICS ----------------
elif menu == "Analytics":

    st.title("📈 Advanced Analytics")

    if not df.empty:
        min_year = int(df["year"].min())
        max_year = int(df["year"].max())

        col1, col2, col3 = st.columns(3)

        crop_filter = col1.multiselect("Crop", df["name"].unique(), default=df["name"].unique())
        year_filter = col2.slider("Year", min_year, max_year, (min_year, max_year))
        region_filter = col3.multiselect("Region", df["region"].unique(), default=df["region"].unique())

        df_filtered = df[
            (df["name"].isin(crop_filter)) &
            (df["region"].isin(region_filter)) &
            (df["year"].between(year_filter[0], year_filter[1]))
        ]

        tab1, tab2, tab3 = st.tabs(["📊 Trends", "📉 Distribution", "📦 Comparison"])

        with tab1:
            st.plotly_chart(px.line(df_filtered, x="year", y="price", color="name"), use_container_width=True)

        with tab2:
            st.plotly_chart(px.histogram(df_filtered, x="price"), use_container_width=True)

        with tab3:
            st.plotly_chart(px.bar(df_filtered, x="name", y="production"), use_container_width=True)

        st.download_button("⬇ Download Data", df_filtered.to_csv(index=False), "data.csv")

# ---------------- SETTINGS ----------------
elif menu == "Settings":

    st.title("⚙️ Settings")

    theme = st.selectbox("Theme", ["Light", "Dark"])
    currency = st.selectbox("Currency", ["₹ INR", "$ USD"])

    chart_type = st.selectbox("Chart Type", ["Bar", "Line", "Pie"])
    alert = st.slider("Price Alert %", 1, 50, 10)

    st.success("Settings Saved ✅")
