import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3
from datetime import datetime

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

# ---------------- 2. LOCAL DATABASE ENGINE ----------------
def init_db():
    conn = sqlite3.connect('agri_data.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS crops (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT, category TEXT, price REAL, 
                volume REAL, region TEXT, year INTEGER)''')
    # Initial data agar table khali ho
    c.execute("SELECT COUNT(*) FROM crops")
    if c.fetchone()[0] == 0:
        data = [('Wheat', 'Grain', 2200, 110, 'North', 2023),
                ('Rice', 'Grain', 2100, 130, 'East', 2023),
                ('Cotton', 'Fiber', 6000, 60, 'West', 2023)]
        c.executemany("INSERT INTO crops (name, category, price, volume, region, year) VALUES (?,?,?,?,?,?)", data)
    conn.commit()
    conn.close()

init_db()

def get_data():
    conn = sqlite3.connect('agri_data.db')
    df = pd.read_sql_query("SELECT * FROM crops", conn)
    conn.close()
    return df

# ---------------- 3. SIDEBAR NAVIGATION & FILTERS ----------------
with st.sidebar:
    st.title("🌾 AgriDash")
    st.write("---")
    
    # Navigation
    menu = st.radio("Main Menu", ["📊 Dashboard", "🌱 Crop Management", "📈 Analytics", "⚙️ Settings"])
    
    st.write("---")
    st.subheader("🔍 Global Filters")
    
    # Filters moved to Sidebar
    raw_df = get_data()
    f_region = st.selectbox("Region", ["All"] + list(raw_df["region"].unique()))
    f_cat = st.selectbox("Category", ["All"] + list(raw_df["category"].unique()))
    
    filtered_df = raw_df.copy()
    if f_region != "All": filtered_df = filtered_df[filtered_df["region"] == f_region]
    if f_cat != "All": filtered_df = filtered_df[filtered_df["category"] == f_cat]

# ---------------- 4. PAGES ----------------

# --- DASHBOARD PAGE ---
if "📊 Dashboard" in menu:
    st.title("📊 Strategic Overview")
    
    # Big Metrics
    total_crops = len(filtered_df)
    avg_price = filtered_df["price"].mean() if not filtered_df.empty else 0
    total_vol = filtered_df["volume"].sum() if not filtered_df.empty else 0

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"<div class='metric-card'><h3>{total_crops}</h3><p>Total Varieties</p></div>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<div class='metric-card'><h3>₹ {avg_price:,.2f}</h3><p>Average Market Price</p></div>", unsafe_allow_html=True)
    with col3:
        st.markdown(f"<div class='metric-card'><h3>{total_vol} Lakh MT</h3><p>Total Production</p></div>", unsafe_allow_html=True)

    st.write("---")
    
    # Visuals
    v1, v2 = st.columns(2)
    with v1:
        fig1 = px.bar(filtered_df, x="name", y="volume", color="name", title="Production by Variety", template="plotly_white")
        st.plotly_chart(fig1, use_container_width=True)
    with v2:
        fig2 = px.pie(filtered_df, values="volume", names="category", hole=0.4, title="Category Distribution")
        st.plotly_chart(fig2, use_container_width=True)

# --- CROP MANAGEMENT PAGE ---
elif "🌱 Crop Management" in menu:
    st.title("🌱 Crop Administration")
    
    tab1, tab2 = st.tabs(["📋 View & Add", "✏️ Edit & Delete"])
    
    with tab1:
        # Add New Crop
        with st.expander("➕ Add New Crop Entry", expanded=False):
            with st.form("add_form"):
                ac1, ac2 = st.columns(2)
                name = ac1.text_input("Crop Name")
                cat = ac1.selectbox("Category", ["Grain", "Fiber", "Vegetable", "Fruit", "Other"])
                prc = ac2.number_input("Price (per quintal)", min_value=0.0)
                vlm = ac2.number_input("Production Volume", min_value=0.0)
                reg = st.text_input("Region (e.g. North, South)")
                yr = st.number_input("Year", value=2024)
                
                if st.form_submit_button("Submit Record"):
                    conn = sqlite3.connect('agri_data.db')
                    conn.execute("INSERT INTO crops (name, category, price, volume, region, year) VALUES (?,?,?,?,?,?)", 
                                 (name, cat, prc, vlm, reg, yr))
                    conn.commit()
                    conn.close()
                    st.success("Record Added!")
                    st.rerun()
        
        st.subheader("Active Inventory")
        st.dataframe(filtered_df, use_container_width=True, hide_index=True)

    with tab2:
        if filtered_df.empty:
            st.info("No data to edit.")
        else:
            # Edit Section
            options = {f"{r['id']} - {r['name']}": r['id'] for _, r in filtered_df.iterrows()}
            select_id = st.selectbox("Select Crop to Modify", options.keys())
            curr_id = options[select_id]
            row = filtered_df[filtered_df["id"] == curr_id].iloc[0]
            
            with st.form("edit_form"):
                ec1, ec2 = st.columns(2)
                enat = ec1.text_input("Edit Name", row["name"])
                ecat = ec1.selectbox("Edit Category", ["Grain", "Fiber", "Vegetable", "Fruit", "Other"], index=0)
                eprc = ec2.number_input("Edit Price", value=float(row["price"]))
                evol = ec2.number_input("Edit Volume", value=float(row["volume"]))
                
                if st.form_submit_button("Update Changes"):
                    conn = sqlite3.connect('agri_data.db')
                    conn.execute("UPDATE crops SET name=?, category=?, price=?, volume=? WHERE id=?", 
                                 (enat, ecat, eprc, evol, curr_id))
                    conn.commit()
                    conn.close()
                    st.success("Updated!")
                    st.rerun()
            
            st.write("---")
            if st.button("🗑️ Delete This Record Permanently", type="secondary"):
                conn = sqlite3.connect('agri_data.db')
                conn.execute("DELETE FROM crops WHERE id=?", (curr_id,))
                conn.commit()
                conn.close()
                st.error("Deleted.")
                st.rerun()

# --- ANALYTICS PAGE ---
elif "📈 Analytics" in menu:
    st.title("📈 Advanced Analytics")
    
    st.subheader("Price vs Production Analysis")
    fig_scat = px.scatter(filtered_df, x="price", y="volume", size="volume", color="category", 
                          hover_name="name", log_x=True, size_max=60, template="plotly_dark")
    st.plotly_chart(fig_scat, use_container_width=True)
    
    st.subheader("Yearly Trend Analysis")
    fig_trend = px.line(filtered_df.sort_values("year"), x="year", y="price", color="name", markers=True)
    st.plotly_chart(fig_trend, use_container_width=True)

# --- SETTINGS PAGE ---
elif "⚙️ Settings" in menu:
    st.title("⚙️ System Settings")
    
    s_col1, s_col2 = st.columns(2)
    
    with s_col1:
        st.subheader("👤 User Profile")
        st.text_input("Full Name", value="Vansh Rohilla")
        st.text_input("Organization", value="AgriCorp India")
        st.selectbox("Access Level", ["Administrator", "Farm Manager", "Analyst"])
        if st.button("Save Profile"):
            st.toast("Profile Updated!")

    with s_col2:
        st.subheader("📤 Data Management")
        csv = raw_df.to_csv(index=False).encode('utf-8')
        st.download_button(label="Download Full Backup (CSV)", data=csv, 
                           file_name=f"agridash_backup_{datetime.now().strftime('%Y%m%d')}.csv", 
                           mime='text/csv')
        
        st.write("---")
        st.subheader("🛠️ Utility")
        if st.button("Clear All Local Data", type="primary"):
            st.warning("Are you sure? This will wipe the database.")
            # Logical check for safety would go here
            
    st.write("---")
    st.info("App Status: Running Perfectly on Local Engine 🚀")
