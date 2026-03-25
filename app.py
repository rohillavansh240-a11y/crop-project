import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3
from datetime import datetime
import os

# --- 1. PAGE CONFIG ---
st.set_page_config(
    page_title="AgriDash | Local Edition",
    page_icon="🌾",
    layout="wide"
)

# --- 2. DATABASE SETUP (Local SQLite) ---
# Ye function database file banayega aur table create karengi agar nahi hai toh.
def init_db():
    conn = sqlite3.connect('agri_data.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS crops (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            category TEXT,
            price_per_unit REAL,
            production_volume REAL,
            region TEXT,
            year INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# --- 3. DATA FUNCTIONS ---
def load_data():
    conn = sqlite3.connect('agri_data.db')
    df = pd.read_sql_query("SELECT * FROM crops ORDER BY id DESC", conn)
    conn.close()
    return df

def add_crop(name, cat, price, vol, reg, year):
    conn = sqlite3.connect('agri_data.db')
    c = conn.cursor()
    c.execute('''
        INSERT INTO crops (name, category, price_per_unit, production_volume, region, year)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (name, cat, price, vol, reg, year))
    conn.commit()
    conn.close()

def delete_crop(crop_id):
    conn = sqlite3.connect('agri_data.db')
    c = conn.cursor()
    c.execute("DELETE FROM crops WHERE id=?", (crop_id,))
    conn.commit()
    conn.close()

# --- 4. THEME & SIDEBAR ---
GREEN = "#2d6a4f"
COLORS = [GREEN, "#f4a261", "#e76f51", "#457b9d", "#606c38"]

if "page" not in st.session_state:
    st.session_state.page = "Dashboard"

with st.sidebar:
    st.title("🌾 AgriDash")
    st.info("Mode: Local Database (SQLite)")
    st.markdown("---")
    for p in ["Dashboard", "Manage Crops", "Analytics"]:
        if st.button(p, use_container_width=True):
            st.session_state.page = p
            st.rerun()
    st.markdown("---")
    st.caption("Manager: Vansh Rohilla")

df = load_data()

# --- 5. PAGES ---

if st.session_state.page == "Dashboard":
    st.title("📊 Farm Overview")
    
    if df.empty:
        st.warning("Abhi tak koi data nahi hai. 'Manage Crops' mein jaakar add karein.")
    else:
        # Metrics Row
        m1, m2, m3 = st.columns(3)
        m1.metric("Total Entries", len(df))
        m2.metric("Avg Price", f"₹{df['price_per_unit'].mean():,.2f}")
        m3.metric("Total Production", f"{df['production_volume'].sum():,.0f} T")

        st.markdown("---")
        
        # Charts Row
        c1, c2 = st.columns([2, 1])
        with c1:
            st.subheader("Top Crops by Production")
            fig = px.bar(df.head(10), x="name", y="production_volume", color="category", color_discrete_sequence=COLORS)
            st.plotly_chart(fig, use_container_width=True)
        with c2:
            st.subheader("Category Breakdown")
            fig_pie = px.pie(df, names="category", hole=0.4, color_discrete_sequence=COLORS)
            st.plotly_chart(fig_pie, use_container_width=True)

elif st.session_state.page == "Manage Crops":
    st.title("🌱 Manage Crop Records")
    
    # Add Form
    with st.expander("➕ Add New Crop", expanded=True):
        with st.form("add_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("Crop Name")
                cat = st.selectbox("Category", ["Grain", "Vegetable", "Fruit", "Fiber", "Other"])
                price = st.number_input("Price (per kg)", min_value=0.0)
            with col2:
                vol = st.number_input("Production (Tons)", min_value=0.0)
                reg = st.text_input("Region")
                year = st.number_input("Year", value=2026)
            
            if st.form_submit_button("Save to Database", use_container_width=True):
                if name and reg:
                    add_crop(name, cat, price, vol, reg, year)
                    st.success(f"{name} save ho gaya!")
                    st.rerun()
                else:
                    st.error("Please Name aur Region zaroor bharein.")

    # Display Table
    st.markdown("---")
    st.subheader("Stored Data")
    st.dataframe(df, use_container_width=True, hide_index=True)

    # Delete Record
    if not df.empty:
        st.markdown("---")
        st.subheader("🗑️ Delete Record")
        id_del = st.number_input("Enter ID to delete", min_value=1, step=1)
        if st.button("Delete Permanently", type="primary"):
            delete_crop(id_del)
            st.success(f"Record {id_del} deleted!")
            st.rerun()

elif st.session_state.page == "Analytics":
    st.title("📈 Detailed Analysis")
    if not df.empty:
        fig_scatter = px.scatter(df, x="price_per_unit", y="production_volume", 
                                 size="production_volume", color="category", 
                                 hover_name="name", template="plotly_white")
        st.plotly_chart(fig_scatter, use_container_width=True)
    else:
        st.info("Analysis ke liye data zaroori hai.")
