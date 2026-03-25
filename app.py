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
    st.title("🌱 Smart Crop Management")

    df = get_data()

    # ---------- SEARCH & FILTER ----------
    st.subheader("🔍 Search & Filter")

    col1, col2 = st.columns(2)
    search = col1.text_input("Search Crop Name")
    category_filter = col2.selectbox("Filter Category", ["All"] + list(df["category"].unique()))

    filtered = df.copy()

    if search:
        filtered = filtered[filtered["name"].str.contains(search, case=False)]

    if category_filter != "All":
        filtered = filtered[filtered["category"] == category_filter]

    st.divider()

    # ---------- ADD NEW ----------
    st.subheader("➕ Add Crop")

    with st.form("add_crop"):
        c1, c2 = st.columns(2)

        name = c1.text_input("Crop Name")
        category = c1.text_input("Category")
        price = c2.number_input("Price", 0.0)
        volume = c2.number_input("Volume", 0.0)
        region = st.text_input("Region")
        year = st.number_input("Year", 2024)

        if st.form_submit_button("Add Crop"):
            if name and category and region:
                conn = get_connection()
                conn.execute("""
                    INSERT INTO crops (name, category, price, volume, region, year)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (name, category, price, volume, region, year))
                conn.commit()
                conn.close()
                st.success("Crop Added")
                st.rerun()
            else:
                st.error("Fill all fields")

    st.divider()

    # ---------- BULK UPLOAD ----------
    st.subheader("📥 Bulk Upload CSV")

    file = st.file_uploader("Upload CSV", type=["csv"])

    if file:
        new_df = pd.read_csv(file)

        required_cols = {"name", "category", "price", "volume", "region", "year"}
        if required_cols.issubset(set(new_df.columns)):
            conn = get_connection()
            new_df.to_sql("crops", conn, if_exists="append", index=False)
            conn.close()
            st.success("Bulk Upload Successful")
            st.rerun()
        else:
            st.error("CSV must contain: name, category, price, volume, region, year")

    st.divider()

    # ---------- DATA TABLE ----------
    st.subheader("📋 Data Editor")

    if not filtered.empty:
        # Add calculated column
        filtered["profit"] = filtered["price"] * filtered["volume"]

        edited_df = st.data_editor(
            filtered,
            use_container_width=True,
            num_rows="dynamic"
        )

        # ---------- SAVE EDIT ----------
        if st.button("💾 Save Changes"):
            conn = get_connection()

            for _, row in edited_df.iterrows():
                conn.execute("""
                    UPDATE crops
                    SET name=?, category=?, price=?, volume=?, region=?, year=?
                    WHERE id=?
                """, (row["name"], row["category"], row["price"],
                      row["volume"], row["region"], row["year"], row["id"]))

            conn.commit()
            conn.close()
            st.success("Changes Saved")
            st.rerun()

        # ---------- BULK DELETE ----------
        st.subheader("🗑 Bulk Delete")

        delete_ids = st.multiselect("Select IDs to delete", edited_df["id"])

        if st.button("Delete Selected"):
            if delete_ids:
                conn = get_connection()
                conn.executemany("DELETE FROM crops WHERE id=?", [(i,) for i in delete_ids])
                conn.commit()
                conn.close()
                st.warning("Deleted Selected Records")
                st.rerun()

        # ---------- EXPORT ----------
        st.subheader("📤 Export Data")

        csv = edited_df.to_csv(index=False).encode()
        st.download_button("Download Filtered Data", csv, "filtered_data.csv")

    else:
        st.warning("No data found")

# ---------------- ANALYTICS ----------------
elif menu == "Analytics":
    st.title("📈 Advanced Analytics Dashboard")

    if filtered_df.empty:
        st.warning("No data available")
    else:
        df = filtered_df.copy()

        # ---------- KPI CARDS ----------
        st.subheader("📊 Key Insights")

        top_crop = df.groupby("name")["volume"].sum().idxmax()
        avg_price = df["price"].mean()
        total_value = (df["price"] * df["volume"]).sum()

        c1, c2, c3 = st.columns(3)
        c1.metric("Top Crop", top_crop)
        c2.metric("Avg Price", f"₹ {avg_price:.2f}")
        c3.metric("Market Value", f"₹ {total_value:,.0f}")

        st.divider()

        # ---------- TREND ANALYSIS ----------
        st.subheader("📉 Year-wise Trend")

        if "year" in df.columns:
            trend = df.groupby("year")[["price", "volume"]].mean().reset_index()

            fig_trend = px.line(trend, x="year", y=["price", "volume"],
                                markers=True, template="plotly_white")
            st.plotly_chart(fig_trend, use_container_width=True)

        # ---------- PROFIT ESTIMATION ----------
        st.subheader("💰 Profit Estimation")

        df["estimated_profit"] = df["price"] * df["volume"]

        fig_profit = px.bar(df, x="name", y="estimated_profit",
                            color="category", title="Profit by Crop")
        st.plotly_chart(fig_profit, use_container_width=True)

        st.divider()

        # ---------- HEATMAP STYLE (CATEGORY VS REGION) ----------
        st.subheader("🌍 Region vs Category")

        pivot = df.pivot_table(values="volume",
                               index="region",
                               columns="category",
                               aggfunc="sum",
                               fill_value=0)

        st.dataframe(pivot, use_container_width=True)

        st.divider()

        # ---------- SCATTER ANALYSIS ----------
        st.subheader("🔍 Price vs Volume Analysis")

        fig_scatter = px.scatter(df,
                                x="price",
                                y="volume",
                                size="volume",
                                color="category",
                                hover_name="name")
        st.plotly_chart(fig_scatter, use_container_width=True)

        st.divider()

        # ---------- SIMPLE FORECAST ----------
        st.subheader("🔮 Future Prediction (Basic)")

        if len(df["year"].unique()) > 1:
            growth = df.groupby("year")["price"].mean().pct_change().mean()
            next_price = avg_price * (1 + growth)

            st.success(f"Estimated Next Year Avg Price: ₹ {next_price:.2f}")
        else:
            st.info("Need multiple years data for prediction")

        st.divider()

        # ---------- SMART INSIGHTS ----------
        st.subheader("🤖 Smart Insights")

        insights = []

        if df["price"].mean() > 3000:
            insights.append("High-value crops dominate the market")

        if df["volume"].sum() > 200:
            insights.append("Production volume is strong")

        if len(df["region"].unique()) > 2:
            insights.append("Diverse regional distribution")

        if insights:
            for i in insights:
                st.success(i)
        else:
            st.info("No strong insights yet")

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
