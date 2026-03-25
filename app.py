import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3
from datetime import datetime
import os

# ---------------- 1. CONFIG & STYLING ----------------
st.set_page_config(page_title="AgriDash | Smart Farming", page_icon="🌾", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f8fafc; }
    .metric-card {
        padding: 20px;
        border-radius: 15px;
        background: linear-gradient(135deg, #1e293b, #334155);
        color: white;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    .stButton>button { width: 100%; border-radius: 8px; }
    </style>
    """, unsafe_allow_html=True)

# ---------------- 2. FIXED DATABASE ENGINE ----------------
DB_FILE = "agri_data.db"

def get_connection():
    # check_same_thread=False is important for Streamlit
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    return conn

def init_db():
    conn = get_connection()
    try:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS crops (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT, category TEXT, price REAL, 
                    volume REAL, region TEXT, year INTEGER)''')
        
        # Check if empty to insert seed data
        c.execute("SELECT COUNT(*) FROM crops")
        if c.fetchone()[0] == 0:
            data = [('Wheat', 'Grain', 2200, 110, 'North', 2023),
                    ('Rice', 'Grain', 2100, 130, 'East', 2023),
                    ('Cotton', 'Fiber', 6000, 60, 'West', 2023)]
            c.executemany("INSERT INTO crops (name, category, price, volume, region, year) VALUES (?,?,?,?,?,?)", data)
        conn.commit()
    except Exception as e:
        st.error(f"Database Error: {e}")
    finally:
        conn.close()

# Run initialization once
init_db()

def get_data():
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM crops", conn)
    conn.close()
    return df

# ---------------- 3. SIDEBAR NAVIGATION & FILTERS ----------------
with st.sidebar:
    st.title("🌾 AgriDash")
    st.write("---")
    
    menu = st.radio("Main Menu", ["📊 Dashboard", "🌱 Crop Management", "📈 Analytics", "⚙️ Settings"])
    
    st.write("---")
    st.subheader("🔍 Global Filters")
    
    raw_df = get_data()
    # Handle empty case
    if not raw_df.empty:
        f_region = st.selectbox("Region", ["All"] + sorted(list(raw_df["region"].unique())))
        f_cat = st.selectbox("Category", ["All"] + sorted(list(raw_df["category"].unique())))
        
        filtered_df = raw_df.copy()
        if f_region != "All": filtered_df = filtered_df[filtered_df["region"] == f_region]
        if f_cat != "All": filtered_df = filtered_df[filtered_df["category"] == f_cat]
    else:
        filtered_df = raw_df

# ---------------- 4. PAGES ----------------

# --- DASHBOARD PAGE ---
if menu == "📊 Dashboard":
    st.title("📊 Strategic Overview")
    
    if filtered_df.empty:
        st.info("No data available. Add crops in Management tab.")
    else:
        total_crops = len(filtered_df)
        avg_price = filtered_df["price"].mean()
        total_vol = filtered_df["volume"].sum()

        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"<div class='metric-card'><h3>{total_crops}</h3><p>Total Varieties</p></div>", unsafe_allow_html=True)
        with col2:
            st.markdown(f"<div class='metric-card'><h3>₹ {avg_price:,.2f}</h3><p>Average Market Price</p></div>", unsafe_allow_html=True)
        with col3:
            st.markdown(f"<div class='metric-card'><h3>{total_vol} Lakh MT</h3><p>Total Production</p></div>", unsafe_allow_html=True)

        st.write("---")
        v1, v2 = st.columns(2)
        with v1:
            fig1 = px.bar(filtered_df, x="name", y="volume", color="name", title="Production by Variety", template="plotly_white")
            st.plotly_chart(fig1, use_container_width=True)
        with v2:
            fig2 = px.pie(filtered_df, values="volume", names="category", hole=0.4, title="Category Distribution")
            st.plotly_chart(fig2, use_container_width=True)

# --- CROP MANAGEMENT PAGE ---
elif menu == "🌱 Crop Management":
    st.title("🌱 Crop Administration")
    tab1, tab2 = st.tabs(["📋 View & Add", "✏️ Edit & Delete"])
    
    with tab1:
        with st.expander("➕ Add New Crop Entry", expanded=False):
            with st.form("add_form"):
                ac1, ac2 = st.columns(2)
                name = ac1.text_input("Crop Name")
                cat = ac1.selectbox("Category", ["Grain", "Fiber", "Vegetable", "Fruit", "Other"])
                prc = ac2.number_input("Price", min_value=0.0)
                vlm = ac2.number_input("Volume", min_value=0.0)
                reg = st.text_input("Region")
                yr = st.number_input("Year", value=2024)
                
                if st.form_submit_button("Submit Record"):
                    if name and reg:
                        conn = get_connection()
                        conn.execute("INSERT INTO crops (name, category, price, volume, region, year) VALUES (?,?,?,?,?,?)", 
                                     (name, cat, prc, vlm, reg, yr))
                        conn.commit()
                        conn.close()
                        st.success("Added!")
                        st.rerun()

        st.subheader("Active Inventory")
        st.dataframe(filtered_df, use_container_width=True, hide_index=True)

    with tab2:
        if raw_df.empty:
            st.info("No records to edit.")
        else:
            options = {f"{r['id']} - {r['name']}": r['id'] for _, r in raw_df.iterrows()}
            select_id = st.selectbox("Select Crop", options.keys())
            curr_id = options[select_id]
            row = raw_df[raw_df["id"] == curr_id].iloc[0]
            
            with st.form("edit_form"):
                ec1, ec2 = st.columns(2)
                enat = ec1.text_input("Edit Name", row["name"])
                ecat = ec1.selectbox("Edit Category", ["Grain", "Fiber", "Vegetable", "Fruit", "Other"])
                eprc = ec2.number_input("Edit Price", value=float(row["price"]))
                evol = ec2.number_input("Edit Volume", value=float(row["volume"]))
                
                if st.form_submit_button("Update Changes"):
                    conn = get_connection()
                    conn.execute("UPDATE crops SET name=?, category=?, price=?, volume=? WHERE id=?", 
                                 (enat, ecat, eprc, evol, curr_id))
                    conn.commit()
                    conn.close()
                    st.success("Updated!")
                    st.rerun()
            
            if st.button("🗑️ Delete Permanently"):
                conn = get_connection()
                conn.execute("DELETE FROM crops WHERE id=?", (curr_id,))
                conn.commit()
                conn.close()
                st.warning("Deleted.")
                st.rerun()

# --- ANALYTICS PAGE ---
elif menu == "📈 Analytics":
    st.title("📈 Advanced Analytics")
    if not filtered_df.empty:
        fig_scat = px.scatter(filtered_df, x="price", y="volume", size="volume", color="category", 
                              hover_name="name", template="plotly_dark")
        st.plotly_chart(fig_scat, use_container_width=True)
    else:
        st.info("Add data to see analytics.")

# --- SETTINGS PAGE ---
elif menu == "⚙️ Settings":
    st.title("⚙️ System Settings")
    colA, colB = st.columns(2)
    with colA:
        st.subheader("👤 Profile")
        st.text_input("Name", "Vansh Rohilla")
        st.button("Update Profile")
    with colB:
        st.subheader("📤 Backup")
        csv = raw_df.to_csv(index=False).encode('utf-8')
        st.download_button("Download CSV", data=csv, file_name="agri_backup.csv")
    
    st.divider()
    if st.button("🔴 RESET DATABASE"):
        if os.path.exists(DB_FILE):
            os.remove(DB_FILE)
            st.success("Database wiped. Refreshing...")
            st.rerun()
