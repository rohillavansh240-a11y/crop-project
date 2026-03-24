import os
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

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
# CSV File
# ------------------------------
DATA_FILE = "crops.csv"

# ------------------------------
# Database Functions (CSV based)
# ------------------------------
def load_crops():
    try:
        df = pd.read_csv(DATA_FILE)
        for col in ["price_per_unit","production_volume"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")
        return df
    except FileNotFoundError:
        # Agar CSV nahi hai to empty DataFrame return karo
        return pd.DataFrame(columns=["id","name","category","price_per_unit","unit","production_volume",
                                     "production_unit","region","season","year","notes"])

def load_stats(df):
    if df.empty:
        return {"total": 0, "avg_price": 0, "total_prod": 0, "top_price": "N/A", "top_prod": "N/A"}
    
    stats = {
        "total": len(df),
        "avg_price": df["price_per_unit"].mean() if "price_per_unit" in df else 0,
        "total_prod": df["production_volume"].sum() if "production_volume" in df else 0,
        "top_price": df["name"].iloc[df["price_per_unit"].idxmax()] if "price_per_unit" in df and not df["price_per_unit"].isna().all() else "N/A",
        "top_prod": df["name"].iloc[df["production_volume"].idxmax()] if "production_volume" in df and not df["production_volume"].isna().all() else "N/A",
    }
    return stats

def insert_crop(data):
    df = load_crops()
    next_id = df["id"].max()+1 if not df.empty else 1
    data_row = {
        "id": next_id,
        "name": data["name"],
        "category": data["category"],
        "price_per_unit": data["price"],
        "unit": data["unit"],
        "production_volume": data["production"],
        "production_unit": data["prod_unit"],
        "region": data["region"],
        "season": data["season"],
        "year": data["year"],
        "notes": data.get("notes","")
    }
    df = pd.concat([df, pd.DataFrame([data_row])], ignore_index=True)
    df.to_csv(DATA_FILE, index=False)

def update_crop(crop_id, data):
    df = load_crops()
    if df.empty: return
    df.loc[df["id"]==crop_id, ["name","category","price_per_unit","unit","production_volume","production_unit","region","season","year","notes"]] = [
        data["name"], data["category"], data["price"], data["unit"], data["production"], data["prod_unit"], data["region"], data["season"], data["year"], data.get("notes","")
    ]
    df.to_csv(DATA_FILE, index=False)

def delete_crop(crop_id):
    df = load_crops()
    if df.empty: return
    df = df[df["id"] != crop_id]
    df.to_csv(DATA_FILE, index=False)

# ------------------------------
# Session State
# ------------------------------
if "page" not in st.session_state: st.session_state.page = "Dashboard"
if "edit_crop_id" not in st.session_state: st.session_state.edit_crop_id = None
if "confirm_delete_id" not in st.session_state: st.session_state.confirm_delete_id = None

# ------------------------------
# Sidebar Navigation
# ------------------------------
with st.sidebar:
    st.markdown(f"## 🌾 AgriDash")
    st.markdown("*Agricultural Management System*")
    st.markdown("---")
    nav_items = {"Dashboard":"📊","Crops":"🌱","Analytics":"📈","Settings":"⚙️"}
    for label, icon in nav_items.items():
        active = st.session_state.page == label
        if st.button(f"{icon}  {label}", key=f"nav_{label}", use_container_width=True, type="primary" if active else "secondary"):
            st.session_state.page = label
            st.session_state.edit_crop_id = None
            st.session_state.confirm_delete_id = None
            st.experimental_rerun()
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
# Dashboard Page
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
    if df_all.empty:
        st.info("No crop data found. Add some crops in the Crops section.")
    else:
        col_left,col_right=st.columns([2,1])
        with col_left:
            st.subheader("Production Volume — Top Crops")
            if "name" in df_all and "production_volume" in df_all:
                prod_df=df_all.groupby("name")["production_volume"].sum().sort_values(ascending=False).head(8).reset_index()
                fig_bar=px.bar(prod_df,x="name",y="production_volume",color_discrete_sequence=[GREEN],template="plotly_white")
                fig_bar.update_layout(showlegend=False,margin=dict(t=10,b=10))
                st.plotly_chart(fig_bar,use_container_width=True)
        with col_right:
            st.subheader("Category Distribution")
            if "category" in df_all:
                cat_df=df_all.groupby("category").size().reset_index(name="Count")
                fig_pie=px.pie(cat_df,values="Count",names="category",color_discrete_sequence=COLORS,hole=0.45)
                fig_pie.update_layout(margin=dict(t=10,b=10))
                st.plotly_chart(fig_pie,use_container_width=True)

# ------------------------------
# Crops Page (Add/Edit/Delete)
# ------------------------------
elif page=="Crops":
    st.markdown("Add, edit, or remove crop records.")
    st.markdown("---")
    with st.expander("➕ Add New Crop",expanded=False):
        with st.form("add_crop_form",clear_on_submit=True):
            fc1,fc2,fc3=st.columns(3)
            with fc1:
                f_name=st.text_input("Crop Name *")
                f_category=st.selectbox("Category *", ["Grain","Legume","Fiber","Sugar","Vegetable","Fruit","Beverage","Root Crop","Other"])
                f_region=st.text_input("Region *")
            with fc2:
                f_price=st.number_input("Price per Unit *",min_value=0.0,step=0.01)
                f_unit=st.text_input("Price Unit *",value="kg")
                f_season=st.selectbox("Season *", ["Kharif","Rabi","Zaid","Summer","Winter","All-year","Rainy","Other"])
            with fc3:
                f_prod=st.number_input("Production Volume *",min_value=0.0,step=1.0)
                f_prod_unit=st.text_input("Production Unit *",value="ton")
                f_year=st.number_input("Year *",min_value=2000,max_value=2100,value=datetime.now().year)
            f_notes=st.text_area("Notes",height=80)
            submitted=st.form_submit_button("Add Crop",type="primary",use_container_width=True)
            if submitted:
                if not f_name or not f_region or not f_unit or not f_prod_unit:
                    st.error("Please fill in all required fields.")
                else:
                    insert_crop({"name":f_name,"category":f_category,"price":f_price,"unit":f_unit,
                                 "production":f_prod,"prod_unit":f_prod_unit,"region":f_region,
                                 "season":f_season,"year":int(f_year),"notes":f_notes})
                    st.success(f"✅ '{f_name}' added successfully!")
                    st.experimental_rerun()

# ------------------------------
# Analytics Page
# ------------------------------
elif page=="Analytics":
    st.title("📈 Analytics")
    st.markdown("Deep-dive into production and price trends.")
    st.markdown("---")
    if df_all.empty:
        st.info("No data to analyze yet.")
    else:
        st.subheader("Price vs Production Scatter")
        scatter_fig = px.scatter(df_all, x="price_per_unit", y="production_volume",
                                 color="category", size="production_volume",
                                 hover_name="name", template="plotly_white",
                                 color_discrete_sequence=COLORS,
                                 labels={"price_per_unit":"Price per Unit","production_volume":"Production","category":"Category"})
        scatter_fig.update_layout(margin=dict(t=10,b=10))
        st.plotly_chart(scatter_fig,use_container_width=True)

# ------------------------------
# Settings Page
# ------------------------------
elif page=="Settings":
    st.title("⚙️ Settings")
    st.markdown("Manage your profile and preferences.")
    st.markdown("---")
    st.checkbox("Price alerts (when price changes > 10%)", value=True)
