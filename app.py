import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3
import os

# ---------------- CONFIG ----------------
st.set_page_config(page_title="Farmlytics", page_icon="🌾", layout="wide")

DB_FILE = "farmlytics.db"

# ---------------- DB ----------------
def get_connection():
    return sqlite3.connect(DB_FILE)

def init_db():
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

    c.execute("SELECT COUNT(*) FROM crops")
    if c.fetchone()[0] == 0:
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

init_db()

def get_data():
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM crops", conn)
    conn.close()
    return df

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.title("🌾 Farmlytics")

    menu = st.radio("Navigation", [
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
    st.title("📊 Farmlytics Dashboard")

    if filtered_df.empty:
        st.warning("No data available")
    else:
        c1, c2, c3 = st.columns(3)
        c1.metric("Total Crops", len(filtered_df))
        c2.metric("Avg Price", f"₹ {filtered_df['price'].mean():.2f}")
        c3.metric("Total Volume", filtered_df["volume"].sum())

        st.plotly_chart(px.bar(filtered_df, x="name", y="volume", color="name"),
                        use_container_width=True)

        st.plotly_chart(px.pie(filtered_df, values="volume", names="category"),
                        use_container_width=True)

# ---------------- MANAGEMENT ----------------
elif menu == "Management":
    st.title("🌱 Crop Management")

    df = get_data()

    search = st.text_input("Search Crop")
    if search:
        df = df[df["name"].str.contains(search, case=False)]

    st.subheader("➕ Add Crop")
    with st.form("add"):
        name = st.text_input("Name")
        category = st.text_input("Category")
        price = st.number_input("Price", 0.0)
        volume = st.number_input("Volume", 0.0)
        region = st.text_input("Region")
        year = st.number_input("Year", 2024)

        if st.form_submit_button("Add"):
            conn = get_connection()
            conn.execute("""
                INSERT INTO crops (name, category, price, volume, region, year)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (name, category, price, volume, region, year))
            conn.commit()
            conn.close()
            st.success("Added")
            st.rerun()

    st.subheader("📋 Data")
    st.dataframe(df)

# ---------------- ANALYTICS ----------------
elif menu == "Analytics":
    st.title("📈 Analytics")

    if filtered_df.empty:
        st.warning("No data")
    else:
        df = filtered_df.copy()

        df["profit"] = df["price"] * df["volume"]

        st.metric("Top Crop", df.groupby("name")["volume"].sum().idxmax())

        st.plotly_chart(px.scatter(df, x="price", y="volume",
                                   size="volume", color="category"),
                        use_container_width=True)

        st.plotly_chart(px.bar(df, x="name", y="profit", color="category"),
                        use_container_width=True)

# ---------------- SETTINGS ----------------
elif menu == "Settings":
    st.title("⚙️ Settings")

    if not raw_df.empty:
        csv = raw_df.to_csv(index=False).encode()
        st.download_button("Download CSV", csv, "farmlytics_data.csv")

    if st.button("Reset Database"):
        if os.path.exists(DB_FILE):
            os.remove(DB_FILE)
            st.success("Reset Done")
            st.rerun()
