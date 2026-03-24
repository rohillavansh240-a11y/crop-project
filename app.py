import os
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# Optional: only import psycopg2 if DATABASE_URL exists
DATABASE_URL = os.environ.get("DATABASE_URL", "")

if DATABASE_URL:
    import psycopg2
    from psycopg2.extras import RealDictCursor

# ------------------------------
# Config & Colors
# ------------------------------
st.set_page_config(page_title="AgriDash", page_icon="🌾", layout="wide", initial_sidebar_state="expanded")

GREEN        = "#2d6a4f"
LIGHT_GREEN  = "#95d5b2"
GOLD         = "#f4a261"
TERRACOTTA   = "#e76f51"
STEEL_BLUE   = "#457b9d"
OLIVE        = "#606c38"
COLORS       = [GREEN, GOLD, TERRACOTTA, STEEL_BLUE, OLIVE, LIGHT_GREEN, "#6d4c41", "#a8dadc"]

# ------------------------------
# Database Functions
# ------------------------------
def get_conn():
    if not DATABASE_URL:
        return None
    try:
        return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
    except Exception as e:
        st.error(f"⚠️ Database connection failed: {e}")
        return None

def load_crops():
    if DATABASE_URL:
        try:
            conn = get_conn()
            if conn is None:
                raise Exception("No database connection.")
            with conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT * FROM crops ORDER BY created_at DESC")
                    rows = cur.fetchall()
            df = pd.DataFrame([dict(r) for r in rows])
            for col in ["price_per_unit", "production_volume"]:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors="coerce")
            return df
        except Exception as e:
            st.error(f"Error loading crops: {e}")
            return pd.DataFrame()
    else:
        # Dummy data if DATABASE_URL not set
        data = [
            {"id":1,"name":"Wheat","category":"Grain","price_per_unit":2200,"unit":"kg",
             "production_volume":1000,"production_unit":"ton","region":"North","season":"Rabi",
             "year":2025,"notes":"Yield: 3 t/ha"},
            {"id":2,"name":"Rice","category":"Grain","price_per_unit":3000,"unit":"kg",
             "production_volume":1500,"production_unit":"ton","region":"East","season":"Kharif",
             "year":2025,"notes":"Yield: 4 t/ha"},
            {"id":3,"name":"Sugarcane","category":"Sugar","price_per_unit":1800,"unit":"kg",
             "production_volume":500,"production_unit":"ton","region":"South","season":"All-year",
             "year":2025,"notes":"Yield: 6 t/ha"},
        ]
        return pd.DataFrame(data)

def load_stats(df):
    if df.empty:
        return {"total":0,"avg_price":0,"total_prod":0,"top_price":"N/A","top_prod":"N/A"}
    return {
        "total": len(df),
        "avg_price": df["price_per_unit"].mean() if "price_per_unit" in df else 0,
        "total_prod": df["production_volume"].sum() if "production_volume" in df else 0,
        "top_price": df["name"].iloc[df["price_per_unit"].idxmax()] if "price_per_unit" in df else "N/A",
        "top_prod": df["name"].iloc[df["production_volume"].idxmax()] if "production_volume" in df else "N/A",
    }

# ------------------------------
# Session State
# ------------------------------
if "page" not in st.session_state: st.session_state.page="Dashboard"

# ------------------------------
# Sidebar Navigation
# ------------------------------
with st.sidebar:
    st.markdown("## 🌾 AgriDash")
    st.markdown("*Agricultural Management System*")
    st.markdown("---")
    nav_items = {"Dashboard":"📊","Crops":"🌱","Analytics":"📈","Settings":"⚙️"}
    for label, icon in nav_items.items():
        active = st.session_state.page == label
        if st.button(f"{icon} {label}", key=f"nav_{label}", use_container_width=True, type="primary" if active else "secondary"):
            st.session_state.page = label
    st.markdown("---")
    now = datetime.now()
    month = now.month
    season = "Winter"
    if 3<=month<=5: season="Spring"
    elif 6<=month<=8: season="Summer"
    elif 9<=month<=11: season="Autumn"
    st.caption(f"📅 {season} Season {now.year}")
    st.caption("👤 Vansh Rohilla — Farm Manager")

# ------------------------------
# Load Data
# ------------------------------
df_all = load_crops()
stats  = load_stats(df_all)
page   = st.session_state.page

# ------------------------------
# Dashboard
# ------------------------------
if page=="Dashboard":
    st.title("📊 Agricultural Dashboard")
    st.markdown("Overview of crop prices, production volumes, and category trends.")
    st.markdown("---")
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("🌾 Total Crops", stats["total"])
    c2.metric("💰 Avg Price / Unit", f"{stats['avg_price']:,.2f}")
    c3.metric("🏭 Total Production", f"{stats['total_prod']:,.0f}")
    c4.metric("🏆 Top by Price", stats["top_price"])
    st.markdown("---")
    if not df_all.empty:
        col_left,col_right = st.columns([2,1])
        with col_left:
            st.subheader("Production Volume — Top Crops")
            if "name" in df_all and "production_volume" in df_all:
                prod_df = df_all.groupby("name")["production_volume"].sum().sort_values(ascending=False).head(8).reset_index()
                fig_bar = px.bar(prod_df, x="name", y="production_volume", color_discrete_sequence=[GREEN], template="plotly_white")
                st.plotly_chart(fig_bar, use_container_width=True)
        with col_right:
            st.subheader("Category Distribution")
            if "category" in df_all:
                cat_df = df_all.groupby("category").size().reset_index(name="Count")
                fig_pie = px.pie(cat_df, values="Count", names="category", color_discrete_sequence=COLORS, hole=0.45)
                st.plotly_chart(fig_pie, use_container_width=True)

# ------------------------------
# Crops Page
# ------------------------------
elif page=="Crops":
    st.title("🌱 Crop Management")
    st.markdown("Add or view crop records.")
    st.markdown("---")
    st.dataframe(df_all, use_container_width=True)

# ------------------------------
# Analytics Page
# ------------------------------
elif page=="Analytics":
    st.title("📈 Analytics")
    st.markdown("Production and price trends.")
    st.markdown("---")
    if not df_all.empty:
        st.subheader("Price per Unit Trend")
        fig = px.line(df_all.sort_values("year"), x="name", y="price_per_unit", color="name", markers=True, template="plotly_white")
        st.plotly_chart(fig, use_container_width=True)

# ------------------------------
# Settings Page
# ------------------------------
elif page=="Settings":
    st.title("⚙️ Settings")
    st.markdown("Manage your preferences.")
    st.checkbox("Price alerts (when price changes >10%)", value=True)
