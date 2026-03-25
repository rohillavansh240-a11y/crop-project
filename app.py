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
    st.title("⚙️ Advanced Settings")

    CONFIG_FILE = "config.json"

    # ---------- LOAD CONFIG ----------
    def load_config():
        if os.path.exists(CONFIG_FILE):
            return pd.read_json(CONFIG_FILE, typ="series").to_dict()
        return {"theme": "Light", "name": "User"}

    def save_config(data):
        pd.Series(data).to_json(CONFIG_FILE)

    config = load_config()

    # ---------- PROFILE ----------
    st.subheader("👤 Profile Settings")
    col1, col2 = st.columns(2)

    with col1:
        name = st.text_input("Your Name", config.get("name", "User"))
    with col2:
        theme = st.selectbox("Theme", ["Light", "Dark"],
                             index=0 if config.get("theme") == "Light" else 1)

    if st.button("💾 Save Profile"):
        save_config({"name": name, "theme": theme})
        st.success("Profile Saved")
        st.rerun()

    # ---------- THEME APPLY ----------
    if config.get("theme") == "Dark":
        st.markdown("""
        <style>
        .main { background-color: #0e1117; color: white; }
        </style>
        """, unsafe_allow_html=True)

    st.divider()

    # ---------- DATA EXPORT ----------
    st.subheader("📤 Data Export")

    if not raw_df.empty:
        csv = raw_df.to_csv(index=False).encode()
        json_data = raw_df.to_json().encode()

        col1, col2 = st.columns(2)
        col1.download_button("Download CSV", csv, "agri_data.csv")
        col2.download_button("Download JSON", json_data, "agri_data.json")
    else:
        st.warning("No data to export")

    st.divider()

    # ---------- AUTO BACKUP ----------
    st.subheader("💾 Backup System")

    if st.button("Create Backup"):
        backup_file = f"backup_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv"
        raw_df.to_csv(backup_file, index=False)
        st.success(f"Backup created: {backup_file}")

    st.divider()

    # ---------- APP STATS ----------
    st.subheader("📊 App Statistics")

    if not raw_df.empty:
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Records", len(raw_df))
        col2.metric("Avg Price", f"₹ {raw_df['price'].mean():.2f}")
        col3.metric("Regions", raw_df['region'].nunique())
    else:
        st.info("No data available")

    st.divider()

    # ---------- DANGER ZONE ----------
    st.subheader("🚨 Danger Zone")

    confirm = st.checkbox("I understand this will delete ALL data")

    if st.button("🔴 Reset Database"):
        if confirm:
            if os.path.exists(DB_FILE):
                os.remove(DB_FILE)
                st.success("Database Reset Successfully")
                st.rerun()
        else:
            st.warning("Please confirm before resetting")
