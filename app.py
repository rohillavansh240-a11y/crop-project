import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3
import os

# ---------------- 1. CONFIG ----------------
st.set_page_config(page_title="AgriDash", page_icon="🌾", layout="wide")

# ---------------- 2. DATABASE ----------------
DB_FILE = "agri_data.db"

@st.cache_resource
def get_connection():
    return sqlite3.connect(DB_FILE, check_same_thread=False)

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
        c.executemany(
            "INSERT INTO crops (name, category, price, volume, region, year) VALUES (?,?,?,?,?,?)",
            seed
        )

    conn.commit()

init_db()

def get_data():
    conn = get_connection()
    return pd.read_sql_query("SELECT * FROM crops", conn)

# ---------------- 3. SIDEBAR ----------------
with st.sidebar:
    st.title("🌾 AgriDash")

    menu = st.radio("Menu", [
        "📊 Dashboard",
        "🌱 Crop Management",
        "📈 Analytics",
        "⚙️ Settings"
    ])

    st.divider()

    raw_df = get_data()

    if not raw_df.empty:
        region = st.selectbox("Region", ["All"] + sorted(raw_df["region"].unique()))
        category = st.selectbox("Category", ["All"] + sorted(raw_df["category"].unique()))

        filtered_df = raw_df.copy()

        if region != "All":
            filtered_df = filtered_df[filtered_df["region"] == region]

        if category != "All":
            filtered_df = filtered_df[filtered_df["category"] == category]
    else:
        filtered_df = raw_df

# ---------------- 4. DASHBOARD ----------------
if menu == "📊 Dashboard":
    st.title("📊 Dashboard")

    if filtered_df.empty:
        st.warning("No data available")
    else:
        c1, c2, c3 = st.columns(3)

        c1.metric("Total Crops", len(filtered_df))
        c2.metric("Avg Price", f"₹ {filtered_df['price'].mean():.2f}")
        c3.metric("Total Volume", f"{filtered_df['volume'].sum()}")

        col1, col2 = st.columns(2)

        with col1:
            fig = px.bar(filtered_df, x="name", y="volume", color="name")
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            fig = px.pie(filtered_df, values="volume", names="category")
            st.plotly_chart(fig, use_container_width=True)

# ---------------- 5. MANAGEMENT ----------------
elif menu == "🌱 Crop Management":
    st.title("🌱 Crop Management")

    tab1, tab2 = st.tabs(["Add / View", "Edit / Delete"])

    # ADD
    with tab1:
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
                    conn.execute(
                        "INSERT INTO crops (name, category, price, volume, region, year) VALUES (?,?,?,?,?,?)",
                        (name, cat, price, volume, region, year)
                    )
                    conn.commit()
                    st.success("Added")
                    st.rerun()
                else:
                    st.error("Fill all fields")

        st.dataframe(filtered_df, use_container_width=True)

    # EDIT
    with tab2:
        if raw_df.empty:
            st.info("No data")
        else:
            crop_id = st.selectbox("Select Crop ID", raw_df["id"])

            row = raw_df[raw_df["id"] == crop_id].iloc[0]

            with st.form("edit"):
                name = st.text_input("Name", row["name"])

                categories = ["Grain", "Fiber", "Vegetable", "Fruit"]
                cat_index = categories.index(row["category"]) if row["category"] in categories else 0
                cat = st.selectbox("Category", categories, index=cat_index)

                price = st.number_input("Price", value=float(row["price"]))
                volume = st.number_input("Volume", value=float(row["volume"]))

                if st.form_submit_button("Update"):
                    conn = get_connection()
                    conn.execute(
                        "UPDATE crops SET name=?, category=?, price=?, volume=? WHERE id=?",
                        (name, cat, price, volume, crop_id)
                    )
                    conn.commit()
                    st.success("Updated")
                    st.rerun()

            if st.button("Delete"):
                conn = get_connection()
                conn.execute("DELETE FROM crops WHERE id=?", (crop_id,))
                conn.commit()
                st.warning("Deleted")
                st.rerun()

# ---------------- 6. ANALYTICS ----------------
elif menu == "📈 Analytics":
    st.title("📈 Analytics")

    if not filtered_df.empty:
        fig = px.scatter(
            filtered_df,
            x="price",
            y="volume",
            size="volume",
            color="category"
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No data")

# ---------------- 7. SETTINGS ----------------
elif menu == "⚙️ Settings":
    st.title("⚙️ Settings")

    if not raw_df.empty:
        csv = raw_df.to_csv(index=False).encode()
        st.download_button("Download CSV", csv, "backup.csv")

    if st.button("RESET DATABASE"):
        if os.path.exists(DB_FILE):
            os.remove(DB_FILE)
            st.success("Reset done")
            st.rerun()
