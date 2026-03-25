import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3
from datetime import datetime
import os

# ---------------- 1. CONFIG ----------------
st.set_page_config(page_title="AgriDash | Vansh Rohilla", page_icon="🌾", layout="wide")

# Dark Theme Card Style
st.markdown("""
    <style>
    .metric-card {
        padding: 20px;
        border-radius: 15px;
        background: #1e293b;
        color: white;
        text-align: center;
        border: 1px solid #334155;
    }
    </style>
    """, unsafe_allow_html=True)

# ---------------- 2. DATABASE ENGINE ----------------
DB_FILE = "agri_data.db"

def get_connection():
    return sqlite3.connect(DB_FILE, check_same_thread=False)

def init_db():
    conn = get_connection()
    c = conn.cursor()
    # Hum 'price' aur 'volume' column use kar rahe hain dashboard charts ke liye
    c.execute('''CREATE TABLE IF NOT EXISTS crops (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT, category TEXT, price REAL, 
                volume REAL, region TEXT, year INTEGER)''')
    
    c.execute("SELECT COUNT(*) FROM crops")
    if c.fetchone()[0] == 0:
        data = [('Wheat', 'Grain', 2200, 110, 'North', 2023),
                ('Rice', 'Grain', 2100, 130, 'East', 2023),
                ('Cotton', 'Fiber', 6000, 60, 'West', 2023)]
        c.executemany("INSERT INTO crops (name, category, price, volume, region, year) VALUES (?,?,?,?,?,?)", data)
    conn.commit()
    conn.close()

init_db()

# ---------------- 3. SIDEBAR & FILTERS ----------------
with st.sidebar:
    st.title("🌾 AgriDash")
    menu = st.radio("Main Menu", ["📊 Dashboard", "🌱 Crop Management", "📈 Analytics", "⚙️ Settings"])
    
    st.divider()
    conn = get_connection()
    raw_df = pd.read_sql_query("SELECT * FROM crops", conn)
    conn.close()

    if not raw_df.empty:
        st.subheader("🔍 Filters")
        f_region = st.selectbox("Region", ["All"] + sorted(list(raw_df["region"].unique())))
        f_cat = st.selectbox("Category", ["All"] + sorted(list(raw_df["category"].unique())))
        
        filtered_df = raw_df.copy()
        if f_region != "All": filtered_df = filtered_df[filtered_df["region"] == f_region]
        if f_cat != "All": filtered_df = filtered_df[filtered_df["category"] == f_cat]
    else:
        filtered_df = raw_df

# ---------------- 4. PAGES ----------------

if menu == "📊 Dashboard":
    st.title("📊 Strategic Overview")
    
    if filtered_df.empty:
        st.info("No data available. Please add data in Management.")
    else:
        # Metrics
        c1, c2, c3 = st.columns(3)
        c1.markdown(f"<div class='metric-card'><h3>{len(filtered_df)}</h3><p>Total Varieties</p></div>", unsafe_allow_html=True)
        c2.markdown(f"<div class='metric-card'><h3>₹ {filtered_df['price'].mean():,.2f}</h3><p>Avg Price</p></div>", unsafe_allow_html=True)
        c3.markdown(f"<div class='metric-card'><h3>{filtered_df['volume'].sum()}</h3><p>Total Vol (Lakh MT)</p></div>", unsafe_allow_html=True)

        st.divider()
        # Charts
        v1, v2 = st.columns(2)
        with v1:
            st.plotly_chart(px.bar(filtered_df, x="name", y="volume", color="category", title="Production"), use_container_width=True)
        with v2:
            st.plotly_chart(px.pie(filtered_df, names="category", values="volume", hole=0.4, title="Category Share"), use_container_width=True)

elif menu == "🌱 Crop Management":
    st.title("🌱 Crop Management")
    t1, t2 = st.tabs(["Add New", "Edit/Delete"])
    
    with t1:
        with st.form("add_crop"):
            name = st.text_input("Crop Name")
            cat = st.selectbox("Category", ["Grain", "Fiber", "Vegetable", "Fruit", "Other"])
            col_a, col_b = st.columns(2)
            prc = col_a.number_input("Price", min_value=0.0)
            vlm = col_b.number_input("Volume", min_value=0.0)
            reg = st.text_input("Region")
            yr = st.number_input("Year", value=2026)
            if st.form_submit_button("Save Record"):
                conn = get_connection()
                conn.execute("INSERT INTO crops (name, category, price, volume, region, year) VALUES (?,?,?,?,?,?)", (name, cat, prc, vlm, reg, yr))
                conn.commit()
                conn.close()
                st.success("Data Saved!")
                st.rerun()
        
        st.dataframe(filtered_df, use_container_width=True, hide_index=True)

    with t2:
        if not raw_df.empty:
            target = st.selectbox("Select Record", [f"{r['id']} | {r['name']}" for _, r in raw_df.iterrows()])
            tid = int(target.split(" | ")[0])
            if st.button("🗑️ Delete Permanently"):
                conn = get_connection()
                conn.execute("DELETE FROM crops WHERE id=?", (tid,))
                conn.commit()
                conn.close()
                st.warning("Deleted!")
                st.rerun()

elif menu == "📈 Analytics":
    st.title("📈 Market Trends")
    if not filtered_df.empty:
        st.plotly_chart(px.scatter(filtered_df, x="price", y="volume", size="volume", color="category", hover_name="name"), use_container_width=True)

elif menu == "⚙️ Settings":
    st.title("⚙️ Control Panel")
    st.subheader("Database Maintenance")
    if st.button("🔴 RESET DATABASE (Fix Column Error)", type="primary"):
        if os.path.exists(DB_FILE):
            os.remove(DB_FILE)
            st.success("Database deleted! Table structure updated. Refreshing...")
            st.rerun()
