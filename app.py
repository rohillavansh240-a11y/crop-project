import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide")

# ---------------- UI CSS ----------------
st.markdown("""
<style>
/* Background */
.main {
    background-color: #f6f8fa;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: #ffffff;
    border-right: 1px solid #eee;
}

/* Cards */
.card {
    background: white;
    padding: 20px;
    border-radius: 15px;
    box-shadow: 0px 4px 15px rgba(0,0,0,0.05);
}

/* Header Banner */
.banner {
    background: linear-gradient(135deg, #1b5e20, #2e7d32);
    padding: 30px;
    border-radius: 20px;
    color: white;
}

/* Titles */
h1, h2, h3 {
    color: #1b4332;
}
</style>
""", unsafe_allow_html=True)

# ---------------- Sidebar ----------------
st.sidebar.title("🌾 AgriDash")

menu = st.sidebar.radio("Menu", [
    "Dashboard",
    "Crop Management",
    "Analytics"
])

# ---------------- Dummy Data ----------------
data = {
    "name": ["Wheat","Rice","Sugarcane","Maize"],
    "price": [2200,3000,1800,2500],
    "production": [1000,1500,500,800],
    "category": ["Grain","Grain","Sugar","Grain"]
}

df = pd.DataFrame(data)

# ---------------- Dashboard ----------------
if menu == "Dashboard":

    # Banner
    st.markdown("""
    <div class="banner">
        <h1>Agricultural Overview</h1>
        <p>Track crop performance, market prices, and production volumes</p>
    </div>
    """, unsafe_allow_html=True)

    st.write("")

    # KPI Cards
    c1, c2, c3, c4 = st.columns(4)

    c1.markdown(f'<div class="card"><h3>Total Crops</h3><h2>{len(df)}</h2></div>', unsafe_allow_html=True)
    c2.markdown(f'<div class="card"><h3>Avg Price</h3><h2>₹{df["price"].mean():.0f}</h2></div>', unsafe_allow_html=True)
    c3.markdown(f'<div class="card"><h3>Total Production</h3><h2>{df["production"].sum()}</h2></div>', unsafe_allow_html=True)
    c4.markdown(f'<div class="card"><h3>Top Crop</h3><h2>{df.iloc[df["production"].idxmax()]["name"]}</h2></div>', unsafe_allow_html=True)

    st.write("")

    # Charts
    col1, col2 = st.columns(2)

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

# ---------------- Crop Page ----------------
elif menu == "Crop Management":
    st.title("🌱 Crop Management")

    st.dataframe(df, use_container_width=True)

# ---------------- Analytics ----------------
elif menu == "Analytics":
    st.title("📈 Analytics")

    fig = px.line(df, x="name", y="price", markers=True)
    st.plotly_chart(fig, use_container_width=True)
