import streamlit as st
import pandas as pd
import plotly.express as px
import time
from sklearn.linear_model import LinearRegression
import hashlib

# ---------- Page Config ----------
st.set_page_config(page_title="Crop Dashboard Pro", layout="wide")

# ---------- Hash Function ----------
def hash_pass(p):
    return hashlib.sha256(p.encode()).hexdigest()

# ---------- Users ----------
users = {
    "vansh": hash_pass("vansh12345678"),
    "admin": hash_pass("1234")
}

# ---------- Session ----------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# ---------- Login ----------
if not st.session_state.logged_in:
    st.title("🔐 Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username in users and users[username] == hash_pass(password):
            st.session_state.logged_in = True
            st.success("Login successful ✅")
            st.rerun()
        else:
            st.error("Wrong credentials ❌")

    st.stop()

# ---------- Glass UI ----------
st.markdown("""
<style>
.header {
    position: sticky;
    top: 0;
    backdrop-filter: blur(10px);
    background: rgba(22,163,74,0.6);
    padding: 15px;
    border-radius: 12px;
    color: white;
    margin-bottom: 20px;
}
.card {
    background: rgba(255,255,255,0.05);
    padding: 20px;
    border-radius: 15px;
    backdrop-filter: blur(8px);
}
</style>
""", unsafe_allow_html=True)

# ---------- Header ----------
st.markdown("""
<div class="header">
<h2>🌾 Crop Dashboard Pro</h2>
</div>
""", unsafe_allow_html=True)

# ---------- Load Data ----------
data = pd.read_csv("crop_data.csv")

# ---------- Sidebar ----------
st.sidebar.title("🌾 Navigation")
page = st.sidebar.radio("Go to", ["Dashboard", "Analytics", "Prediction"])

# ---------- Filters ----------
st.sidebar.markdown("### 🔍 Filters")
crop_filter = st.sidebar.selectbox("Select Crop", ["All"] + list(data['Crop'].unique()))
year_filter = st.sidebar.selectbox("Select Year", ["All"] + list(data['Year'].unique()))

filtered_data = data.copy()
if crop_filter != "All":
    filtered_data = filtered_data[filtered_data['Crop'] == crop_filter]
if year_filter != "All":
    filtered_data = filtered_data[filtered_data['Year'] == year_filter]

# ---------- Dashboard ----------
if page == "Dashboard":
    total_crops = filtered_data['Crop'].nunique()
    avg_price = filtered_data['Price'].mean()
    total_production = filtered_data['Production'].sum()
    top_crop = filtered_data.groupby('Crop')['Production'].sum().idxmax()

    col1, col2, col3, col4 = st.columns(4)
    col1.markdown(f"<div class='card'>🌱 Crops<br><h2>{total_crops}</h2></div>", unsafe_allow_html=True)
    col2.markdown(f"<div class='card'>💰 Price<br><h2>₹{avg_price:.2f}</h2></div>", unsafe_allow_html=True)
    col3.markdown(f"<div class='card'>⚖️ Production<br><h2>{total_production}</h2></div>", unsafe_allow_html=True)
    col4.markdown(f"<div class='card'>📈 Top<br><h2>{top_crop}</h2></div>", unsafe_allow_html=True)

# ---------- Analytics ----------
elif page == "Analytics":
    st.markdown("## 📊 Production")
    prod_data = filtered_data.groupby('Crop')['Production'].sum().reset_index()
    fig1 = px.bar(prod_data, x='Crop', y='Production')
    st.plotly_chart(fig1, use_container_width=True)

    st.markdown("## 🌾 Category")
    if 'Category' in filtered_data.columns:
        cat_data = filtered_data['Category'].value_counts().reset_index()
        cat_data.columns = ['Category', 'Count']
        fig2 = px.pie(cat_data, names='Category', values='Count')
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("## 💰 Price Trend")
    fig3 = px.line(filtered_data, x='Year', y='Price', color='Crop')
    st.plotly_chart(fig3, use_container_width=True)

# ---------- Prediction ----------
elif page == "Prediction":
    st.markdown("## 🤖 Price Prediction")
    model = LinearRegression()
    X = data[['Year']]
    y = data['Price']
    model.fit(X, y)

    year = st.number_input("Enter Year", 2025, 2035)
    if st.button("Predict"):
        pred = model.predict([[year]])
        st.success(f"Predicted Price: ₹{pred[0]:.2f}")
