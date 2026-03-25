import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3
import os

# ---------------- CONFIG ----------------
st.set_page_config(page_title="AgriDash", layout="wide")

DB_FILE = "agri_data.db"

# ---------------- DB CONNECTION ----------------
def get_connection():
    return sqlite3.connect(DB_FILE)

def init_db():
    try:
        conn = get_connection()
        c = conn.cursor()

        c.execute("""
            CREATE TABLE IF NOT EXISTS crops (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                category TEXT,
                price REAL,
                volume REAL,
                region TEXT,
                year INTEGER
            )
        """)

        # insert only if empty
        c.execute("SELECT COUNT(*) FROM crops")
        count = c.fetchone()[0]

        if count == 0:
            seed = [
                ('Wheat', 'Grain', 2200, 110, 'North', 2023),
                ('Rice', 'Grain', 2100, 130, 'East', 2023),
                ('Cotton', 'Fiber', 6000, 60, 'West', 2023)
            ]

            c.executemany("""
                INSERT INTO crops (name, category, price, volume, region, year)
                VALUES (?, ?, ?, ?, ?, ?)
            """, seed)

        conn.commit()
        conn.close()

    except Exception as e:
        st.error(f"DB Error: {e}")

init_db()

def get_data():
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM crops", conn)
    conn.close()
    return df

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.title("🌾 AgriDash")

    menu = st.radio("Menu", [
        "Dashboard",
        "Management",
        "Analytics",
        "Settings"
    ])

    raw_df = get_data()

    if not raw_df.empty:
        region = st.selectbox("Region", ["All"] + list(raw_df["region"].unique()))
        category = st.selectbox("Category", ["All"] + list(raw_df["category"].unique()))

        filtered_df = raw_df.copy()

        if region != "All":
            filtered_df = filtered_df[filtered_df["region"] == region]

        if category != "All":
            filtered_df = filtered_df[filtered_df["category"] == category]
    else:
        filtered_df = raw_df

# ---------------- DASHBOARD ----------------
if menu == "Dashboard":
    st.title("📊 Dashboard")

    if filtered_df.empty:
        st.warning("No data")
    else:
        c1, c2, c3 = st.columns(3)
        c1.metric("Total Crops", len(filtered_df))
        c2.metric("Avg Price", f"₹ {filtered_df['price'].mean():.2f}")
        c3.metric("Total Volume", filtered_df["volume"].sum())

        st.plotly_chart(px.bar(filtered_df, x="name", y="volume"), use_container_width=True)
        st.plotly_chart(px.pie(filtered_df, values="volume", names="category"), use_container_width=True)

# ---------------- MANAGEMENT ----------------
elif menu == "Management":
    st.title("🌱 Crop Management")

    with st.form("add"):
        name = st.text_input("Name")
        cat = st.selectbox("Category", ["Grain", "Fiber", "Vegetable", "Fruit"])
        price = st.number_input("Price", 0.0)
        volume = st.number_input("Volume", 0.0)
        region = st.text_input("Region")
        year = st.number_input("Year", 2024)

        if st.form_submit_button("Add"):
            if name and region:
                conn = get_connection()
                conn.execute("""
                    INSERT INTO crops (name, category, price, volume, region, year)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (name, cat, price, volume, region, year))
                conn.commit()
                conn.close()
                st.success("Added")
                st.rerun()

    st.dataframe(filtered_df)

# ---------------- ANALYTICS ----------------
elif menu == "Analytics":
    st.title("📈 Analytics")

    if not filtered_df.empty:
        fig = px.scatter(filtered_df, x="price", y="volume", size="volume", color="category")
        st.plotly_chart(fig, use_container_width=True)

# ---------------- SETTINGS ----------------
elif menu == "Settings":
    st.title("⚙️ Settings")

    if st.button("RESET DATABASE"):
        if os.path.exists(DB_FILE):
            os.remove(DB_FILE)
            st.success("Reset done")
            st.rerun()
