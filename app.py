import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# ---------------- CONFIG ----------------
st.set_page_config(page_title="AgriDash", layout="wide")

# ---------------- SESSION STATE ----------------
if "confirm_delete_id" not in st.session_state:
    st.session_state.confirm_delete_id = None

# ---------------- DATA ----------------
@st.cache_data
def load_data():
    return pd.DataFrame([
        {"id":1,"name":"Wheat","category":"Grain","price_per_unit":2200,"unit":"quintal",
         "production_volume":110,"production_unit":"lakh MT","region":"North","season":"Rabi","year":2023,"notes":"Yield: 3.5 t/ha"},
        {"id":2,"name":"Rice","category":"Grain","price_per_unit":2100,"unit":"quintal",
         "production_volume":130,"production_unit":"lakh MT","region":"East","season":"Kharif","year":2023,"notes":"Yield: 4.2 t/ha"},
        {"id":3,"name":"Cotton","category":"Fiber","price_per_unit":6000,"unit":"quintal",
         "production_volume":60,"production_unit":"lakh MT","region":"West","season":"Kharif","year":2023,"notes":"Yield: 2.1 t/ha"},
    ])

df_all = load_data().copy()

# ---------------- FUNCTIONS ----------------
def update_crop(cid, data):
    for k, v in data.items():
        df_all.loc[df_all["id"] == cid, k] = v

def delete_crop(cid):
    global df_all
    df_all = df_all[df_all["id"] != cid]

# ---------------- SIDEBAR ----------------
page = st.sidebar.radio("Navigation", ["Dashboard","Edit","Analytics","Settings"])

# ================= DASHBOARD =================
if page == "Dashboard":
    st.title("🌾 AgriDash Dashboard")

    st.markdown("""
    <style>
    .card {
        padding: 18px;
        border-radius: 14px;
        background: linear-gradient(135deg, #1e293b, #0f172a);
        color: white;
        text-align: center;
        box-shadow: 0 6px 20px rgba(0,0,0,0.25);
    }
    </style>
    """, unsafe_allow_html=True)

    # FILTERS
    f1,f2,f3 = st.columns(3)
    with f1:
        region = st.selectbox("Region", ["All"]+sorted(df_all["region"].unique()))
    with f2:
        category = st.selectbox("Category", ["All"]+sorted(df_all["category"].unique()))
    with f3:
        year = st.selectbox("Year", ["All"]+sorted(df_all["year"].unique()))

    filtered = df_all.copy()
    if region!="All": filtered = filtered[filtered["region"]==region]
    if category!="All": filtered = filtered[filtered["category"]==category]
    if year!="All": filtered = filtered[filtered["year"]==year]

    # METRICS
    total = len(filtered)
    avg_price = round(filtered["price_per_unit"].mean(),2) if not filtered.empty else 0
    total_prod = filtered["production_volume"].sum() if not filtered.empty else 0

    m1,m2,m3 = st.columns(3)
    m1.markdown(f"<div class='card'><h2>{total}</h2><p>Total Crops</p></div>",unsafe_allow_html=True)
    m2.markdown(f"<div class='card'><h2>₹ {avg_price}</h2><p>Avg Price</p></div>",unsafe_allow_html=True)
    m3.markdown(f"<div class='card'><h2>{total_prod}</h2><p>Total Production</p></div>",unsafe_allow_html=True)

    st.markdown("---")

    # CHARTS
    c1,c2 = st.columns(2)
    with c1:
        fig1 = px.bar(filtered,x="name",y="production_volume",color="region",title="Production by Crop")
        st.plotly_chart(fig1,use_container_width=True)
    with c2:
        fig2 = px.line(filtered.sort_values("year"),x="year",y="price_per_unit",color="name",markers=True,title="Price Trend")
        st.plotly_chart(fig2,use_container_width=True)

    # TABLE
    st.subheader("📋 Crop Data")
    st.dataframe(filtered,use_container_width=True)

# ================= EDIT =================
elif page == "Edit":
    st.title("✏️ Edit / Delete Crop")

    options = {f"{r['id']} — {r['name']}":r["id"] for _,r in df_all.iterrows()}
    selected = st.selectbox("Select Crop", list(options.keys()))
    cid = options[selected]

    row = df_all[df_all["id"]==cid].iloc[0]

    c1,c2 = st.columns(2)

    # EDIT
    with c1:
        with st.form("edit"):
            name = st.text_input("Name",row["name"])
            category = st.selectbox("Category",["Grain","Fiber","Vegetable","Fruit","Other"],
                                    index=["Grain","Fiber","Vegetable","Fruit","Other"].index(row["category"]) if row["category"] in ["Grain","Fiber","Vegetable","Fruit","Other"] else 0)
            price = st.number_input("Price",value=float(row["price_per_unit"]))
            production = st.number_input("Production",value=float(row["production_volume"]))
            year = st.number_input("Year",value=int(row["year"]))

            if st.form_submit_button("💾 Save"):
                update_crop(cid,{
                    "name":name,
                    "category":category,
                    "price_per_unit":price,
                    "production_volume":production,
                    "year":int(year)
                })
                st.success("✅ Updated Successfully")
                st.rerun()

    # DELETE
    with c2:
        st.warning("Delete Crop Permanently")

        if st.button("🗑️ Delete"):
            st.session_state.confirm_delete_id = cid

        if st.session_state.confirm_delete_id == cid:
            st.error("Are you sure?")
            c11,c22 = st.columns(2)

            with c11:
                if st.button("Yes Delete"):
                    delete_crop(cid)
                    st.session_state.confirm_delete_id = None
                    st.success("Deleted")
                    st.rerun()

            with c22:
                if st.button("Cancel"):
                    st.session_state.confirm_delete_id = None
                    st.rerun()

# ================= ANALYTICS =================
elif page == "Analytics":
    st.title("📈 Analytics")

    fig1 = px.line(df_all,x="year",y="price_per_unit",color="name",markers=True)
    st.plotly_chart(fig1,use_container_width=True)

    fig2 = px.scatter(df_all,x="price_per_unit",y="production_volume",
                      color="category",size="production_volume")
    st.plotly_chart(fig2,use_container_width=True)

# ================= SETTINGS =================
elif page == "Settings":
    st.title("⚙️ Settings")

    st.subheader("Export Data")

    csv = df_all.to_csv(index=False)

    st.download_button(
        label="📥 Download CSV",
        data=csv,
        file_name=f"agridash_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )

    st.success("✅ App Running Perfectly")
