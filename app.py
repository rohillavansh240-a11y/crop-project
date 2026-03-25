import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Page Configuration - Browser tab name and layout
st.set_page_config(page_title="Crop Price & Production Dashboard", layout="wide")

# --- CUSTOM CSS (For that Dark Glassy UI Look) ---
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    [data-testid="stMetricValue"] { font-size: 28px; color: #00d4ff; }
    [data-testid="stSidebar"] { background-color: #161b22; }
    div.stButton > button { background-color: #00d4ff; color: white; border-radius: 5px; }
    .metric-card {
        background-color: #161b22;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #30363d;
    }
    </style>
    """, unsafe_allow_html=True)

# --- MOCK DATA (Crop Price & Production) ---
data = {
    'Month': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct'],
    'Price': [450, 480, 520, 510, 550, 600, 590, 620, 650, 700],
    'Production': [1200, 1150, 1300, 1250, 1400, 1350, 1500, 1450, 1600, 1550],
    'Region': ['North', 'East', 'South', 'West', 'North', 'East', 'South', 'West', 'North', 'East']
}
df = pd.DataFrame(data)

# --- SIDEBAR NAV ---
with st.sidebar:
    st.image("https://www.python.org/static/community_logos/python-logo-master-v3-TM.png", width=50)
    st.title("PYDASH")
    st.markdown("---")
    st.button("📊 Dashboard", use_container_width=True)
    st.button("📁 Projects", use_container_width=True)
    st.button("📑 Reports", use_container_width=True)
    st.button("⚙️ Settings", use_container_width=True)
    st.markdown("---")
    st.write("User: **Admin K.**")

# --- MAIN UI ---
st.header("Crop Production & Price Analytics")
st.subheader("Global Performance Overview")

# Top Metrics Row
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Revenue", "$1.2M", "+8.4%")
with col2:
    st.metric("Avg Crop Price", "$580", "+5.2%")
with col3:
    st.metric("New Harvests", "1,340", "+12.1%")
with col4:
    st.metric("Market Demand", "94%", "-0.5%")

st.markdown("---")

# Middle Row: Main Charts
left_col, right_col = st.columns([2, 1])

with left_col:
    st.write("### Monthly Price vs. Production")
    fig = go.Figure()
    # Line Chart for Price
    fig.add_trace(go.Scatter(x=df['Month'], y=df['Price'], name='Price ($)', 
                             line=dict(color='#00d4ff', width=4), mode='lines+markers'))
    # Area Chart for Production
    fig.add_trace(go.Scatter(x=df['Month'], y=df['Production'], name='Production (Tons)', 
                             fill='tozeroy', line=dict(color='rgba(0, 212, 255, 0.2)')))
    
    fig.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', 
                      plot_bgcolor='rgba(0,0,0,0)', height=400)
    st.plotly_chart(fig, use_container_width=True)

with right_col:
    st.write("### Top 5 Crops by Sales")
    crops = ['Wheat', 'Rice', 'Corn', 'Soy', 'Cotton']
    sales = [2500, 2100, 1800, 1500, 900]
    fig_bar = px.bar(x=sales, y=crops, orientation='h', color_discrete_sequence=['#00d4ff'])
    fig_bar.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', height=400)
    st.plotly_chart(fig_bar, use_container_width=True)

# Bottom Row
bottom_left, bottom_right = st.columns(2)

with bottom_left:
    st.write("### Distribution by Region")
    fig_pie = px.pie(df, values='Production', names='Region', hole=0.6,
                     color_discrete_sequence=px.colors.sequential.Cyan)
    fig_pie.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_pie, use_container_width=True)

with bottom_right:
    st.write("### Recent Activity Log")
    activity_data = {
        "Time": ["2 mins ago", "10 mins ago", "1 hour ago", "4 hours ago"],
        "Action": ["Price Updated", "New Export Order", "Stock Refilled", "Report Generated"],
        "Status": ["✅ Done", "✅ Done", "⚠️ Pending", "✅ Done"]
    }
    st.table(pd.DataFrame(activity_data))
