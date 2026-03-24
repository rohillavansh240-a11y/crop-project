import os
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

st.set_page_config(
    page_title="AgriDash",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded",
)

GREEN        = "#2d6a4f"
LIGHT_GREEN  = "#95d5b2"
GOLD         = "#f4a261"
TERRACOTTA   = "#e76f51"
STEEL_BLUE   = "#457b9d"
OLIVE        = "#606c38"
COLORS       = [GREEN, GOLD, TERRACOTTA, STEEL_BLUE, OLIVE, LIGHT_GREEN, "#6d4c41", "#a8dadc"]

DATABASE_URL = os.environ.get("DATABASE_URL", "")

def get_conn():
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)

def load_crops():
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM crops ORDER BY created_at DESC")
            rows = cur.fetchall()
    df = pd.DataFrame([dict(r) for r in rows])
    if not df.empty:
        for col in ["price_per_unit", "production_volume"]:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df

def load_stats(df):
    if df.empty:
        return {"total": 0, "avg_price": 0, "total_prod": 0, "top_price": "N/A", "top_prod": "N/A"}
    return {
        "total": len(df),
        "avg_price": df["price_per_unit"].mean(),
        "total_prod": df["production_volume"].sum(),
        "top_price": df.loc[df["price_per_unit"].idxmax(), "name"],
        "top_prod": df.loc[df["production_volume"].idxmax(), "name"],
    }

def insert_crop(data):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """INSERT INTO crops (name, category, price_per_unit, unit,
                   production_volume, production_unit, region, season, year, notes)
                   VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                (data["name"], data["category"], data["price"], data["unit"],
                 data["production"], data["prod_unit"], data["region"],
                 data["season"], data["year"], data.get("notes", "")),
            )
        conn.commit()

def update_crop(crop_id, data):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """UPDATE crops SET name=%s, category=%s, price_per_unit=%s, unit=%s,
                   production_volume=%s, production_unit=%s, region=%s, season=%s,
                   year=%s, notes=%s, updated_at=NOW() WHERE id=%s""",
                (data["name"], data["category"], data["price"], data["unit"],
                 data["production"], data["prod_unit"], data["region"],
                 data["season"], data["year"], data.get("notes", ""), crop_id),
            )
        conn.commit()

def delete_crop(crop_id):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM crops WHERE id=%s", (crop_id,))
        conn.commit()

if "page" not in st.session_state:
    st.session_state.page = "Dashboard"
if "edit_crop_id" not in st.session_state:
    st.session_state.edit_crop_id = None
if "confirm_delete_id" not in st.session_state:
    st.session_state.confirm_delete_id = None

with st.sidebar:
    st.markdown(f"## 🌾 AgriDash")
    st.markdown("*Agricultural Management System*")
    st.markdown("---")

    nav_items = {
        "Dashboard": "📊",
        "Crops": "🌱",
        "Analytics": "📈",
        "Settings": "⚙️",
    }
    for label, icon in nav_items.items():
        active = st.session_state.page == label
        if st.button(
            f"{icon}  {label}",
            key=f"nav_{label}",
            use_container_width=True,
            type="primary" if active else "secondary",
        ):
            st.session_state.page = label
            st.session_state.edit_crop_id = None
            st.session_state.confirm_delete_id = None
            st.rerun()

    st.markdown("---")
    now = datetime.now()
    month = now.month
    if 3 <= month <= 5:
        season = "Spring"
    elif 6 <= month <= 8:
        season = "Summer"
    elif 9 <= month <= 11:
        season = "Autumn"
    else:
        season = "Winter"
    st.caption(f"📅 {season} Season {now.year}")
    st.caption("👤 Vansh Rohilla — Farm Manager")

df_all = load_crops()
stats  = load_stats(df_all)
page   = st.session_state.page

if page == "Dashboard":
    st.title("📊 Agricultural Dashboard")
    st.markdown("Overview of crop prices, production volumes, and category trends.")
    st.markdown("---")

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("🌾 Total Crops", stats["total"])
    with c2:
        st.metric("💰 Avg Price / Unit", f"{stats['avg_price']:,.2f}")
    with c3:
        st.metric("🏭 Total Production", f"{stats['total_prod']:,.0f}")
    with c4:
        st.metric("🏆 Top by Price", stats["top_price"])

    st.markdown("---")

    if df_all.empty:
        st.info("No crop data found. Add some crops in the Crops section.")
    else:
        col_left, col_right = st.columns([2, 1])

        with col_left:
            st.subheader("Production Volume — Top Crops")
            prod_df = (
                df_all.groupby("name")["production_volume"]
                .sum()
                .sort_values(ascending=False)
                .head(8)
                .reset_index()
            )
            prod_df.columns = ["Crop", "Production"]
            fig_bar = px.bar(
                prod_df, x="Crop", y="Production",
                color_discrete_sequence=[GREEN],
                template="plotly_white",
            )
            fig_bar.update_traces(marker_line_color="white", marker_line_width=1)
            fig_bar.update_layout(showlegend=False, margin=dict(t=10, b=10))
            st.plotly_chart(fig_bar, use_container_width=True)

        with col_right:
            st.subheader("Category Distribution")
            cat_df = df_all.groupby("category").size().reset_index(name="Count")
            fig_pie = px.pie(
                cat_df, values="Count", names="category",
                color_discrete_sequence=COLORS,
                hole=0.45,
            )
            fig_pie.update_layout(margin=dict(t=10, b=10), showlegend=True)
            st.plotly_chart(fig_pie, use_container_width=True)

        st.subheader("Price per Unit — Trend Across Crops")
        price_df = (
            df_all.sort_values(["year", "name"])
            .head(12)[["name", "price_per_unit"]]
            .reset_index(drop=True)
        )
        fig_line = px.line(
            price_df, x="name", y="price_per_unit",
            markers=True, template="plotly_white",
            color_discrete_sequence=[GOLD],
            labels={"name": "Crop", "price_per_unit": "Price"},
        )
        fig_line.update_traces(line_width=3, marker_size=8)
        fig_line.update_layout(margin=dict(t=10, b=10))
        st.plotly_chart(fig_line, use_container_width=True)


elif page == "Crops":
    st.title("🌱 Crop Management")
    st.markdown("Add, edit, or remove crop records.")
    st.markdown("---")

    with st.expander("➕ Add New Crop", expanded=False):
        with st.form("add_crop_form", clear_on_submit=True):
            fc1, fc2, fc3 = st.columns(3)
            with fc1:
                f_name     = st.text_input("Crop Name *")
                f_category = st.selectbox("Category *", ["Grain", "Legume", "Fiber", "Sugar", "Vegetable", "Fruit", "Beverage", "Root Crop", "Other"])
                f_region   = st.text_input("Region *")
            with fc2:
                f_price    = st.number_input("Price per Unit *", min_value=0.0, step=0.01)
                f_unit     = st.text_input("Price Unit *", value="kg")
                f_season   = st.selectbox("Season *", ["Kharif", "Rabi", "Zaid", "Summer", "Winter", "All-year", "Rainy", "Other"])
            with fc3:
                f_prod     = st.number_input("Production Volume *", min_value=0.0, step=1.0)
                f_prod_unit= st.text_input("Production Unit *", value="ton")
                f_year     = st.number_input("Year *", min_value=2000, max_value=2100, value=datetime.now().year, step=1)
            f_notes = st.text_area("Notes", height=80)
            submitted = st.form_submit_button("Add Crop", type="primary", use_container_width=True)
            if submitted:
                if not f_name or not f_region or not f_unit or not f_prod_unit:
                    st.error("Please fill in all required fields.")
                else:
                    insert_crop({
                        "name": f_name, "category": f_category, "price": f_price,
                        "unit": f_unit, "production": f_prod, "prod_unit": f_prod_unit,
                        "region": f_region, "season": f_season, "year": int(f_year),
                        "notes": f_notes,
                    })
                    st.success(f"✅ '{f_name}' added successfully!")
                    st.rerun()

    df_all = load_crops()

    if df_all.empty:
        st.info("No crops yet. Add one above!")
    else:
        search = st.text_input("🔍 Search crops by name or category", "")
        filtered = df_all.copy()
        if search:
            filtered = filtered[
                filtered["name"].str.contains(search, case=False, na=False) |
                filtered["category"].str.contains(search, case=False, na=False)
            ]

        display_cols = ["id", "name", "category", "price_per_unit", "unit", "production_volume", "production_unit", "region", "season", "year", "notes"]
        available_cols = [c for c in display_cols if c in filtered.columns]
        st.dataframe(
            filtered[available_cols].rename(columns={
                "id": "ID", "name": "Name", "category": "Category",
                "price_per_unit": "Price", "unit": "Price Unit",
                "production_volume": "Production", "production_unit": "Prod. Unit",
                "region": "Region", "season": "Season", "year": "Year", "notes": "Notes",
            }),
            use_container_width=True,
            height=350,
            hide_index=True,
        )

        st.markdown("---")
        st.subheader("Edit / Delete a Crop")
        crop_options = {f"{row['id']} — {row['name']}": row["id"] for _, row in df_all.iterrows()}
        selected_label = st.selectbox("Select crop to edit/delete", list(crop_options.keys()))
        selected_id = crop_options[selected_label]
        row = df_all[df_all["id"] == selected_id].iloc[0]

        ed1, ed2 = st.columns(2)

        with ed1:
            with st.form("edit_crop_form"):
                st.markdown(f"**Editing: {row['name']}**")
                ec1, ec2, ec3 = st.columns(3)
                with ec1:
                    e_name     = st.text_input("Name", value=row["name"])
                    e_category = st.selectbox("Category", ["Grain","Legume","Fiber","Sugar","Vegetable","Fruit","Beverage","Root Crop","Other"],
                                              index=["Grain","Legume","Fiber","Sugar","Vegetable","Fruit","Beverage","Root Crop","Other"].index(row["category"]) if row["category"] in ["Grain","Legume","Fiber","Sugar","Vegetable","Fruit","Beverage","Root Crop","Other"] else 0)
                    e_region   = st.text_input("Region", value=row.get("region", ""))
                with ec2:
                    e_price    = st.number_input("Price", value=float(row["price_per_unit"]), step=0.01)
                    e_unit     = st.text_input("Price Unit", value=row.get("unit", "kg"))
                    seasons    = ["Kharif","Rabi","Zaid","Summer","Winter","All-year","Rainy","Other"]
                    e_season   = st.selectbox("Season", seasons,
                                             index=seasons.index(row["season"]) if row["season"] in seasons else 0)
                with ec3:
                    e_prod     = st.number_input("Production", value=float(row["production_volume"]), step=1.0)
                    e_prod_unit= st.text_input("Prod. Unit", value=row.get("production_unit", "ton"))
                    e_year     = st.number_input("Year", min_value=2000, max_value=2100, value=int(row["year"]), step=1)
                e_notes    = st.text_area("Notes", value=row.get("notes", "") or "", height=60)
                save = st.form_submit_button("💾 Save Changes", type="primary", use_container_width=True)
                if save:
                    update_crop(selected_id, {
                        "name": e_name, "category": e_category, "price": e_price,
                        "unit": e_unit, "production": e_prod, "prod_unit": e_prod_unit,
                        "region": e_region, "season": e_season, "year": int(e_year),
                        "notes": e_notes,
                    })
                    st.success("✅ Crop updated!")
                    st.rerun()

        with ed2:
            st.markdown(f"**Delete: {row['name']}**")
            st.warning(f"This will permanently remove **{row['name']}** from the database.")
            if st.button("🗑️ Delete this Crop", type="secondary", use_container_width=True):
                st.session_state.confirm_delete_id = selected_id

            if st.session_state.confirm_delete_id == selected_id:
                st.error(f"Are you sure you want to delete **{row['name']}**?")
                cc1, cc2 = st.columns(2)
                with cc1:
                    if st.button("Yes, Delete", type="primary", use_container_width=True):
                        delete_crop(selected_id)
                        st.session_state.confirm_delete_id = None
                        st.success("Crop deleted.")
                        st.rerun()
                with cc2:
                    if st.button("Cancel", use_container_width=True):
                        st.session_state.confirm_delete_id = None
                        st.rerun()


elif page == "Analytics":
    st.title("📈 Analytics")
    st.markdown("Deep-dive into India MSP trends, yield patterns, and regional production.")
    st.markdown("---")

    india_df = df_all[df_all["production_unit"] == "lakh MT"].copy()
    global_df = df_all[df_all["production_unit"] == "ton"].copy()

    if not india_df.empty:
        st.subheader("India MSP Price Trend (₹/quintal)")
        msp_fig = px.line(
            india_df.sort_values("year"),
            x="year", y="price_per_unit", color="name",
            markers=True, template="plotly_white",
            color_discrete_sequence=[GREEN, GOLD, TERRACOTTA],
            labels={"year": "Year", "price_per_unit": "MSP (₹/quintal)", "name": "Crop"},
        )
        msp_fig.update_traces(line_width=3, marker_size=9)
        msp_fig.update_layout(margin=dict(t=10, b=10))
        st.plotly_chart(msp_fig, use_container_width=True)

        st.subheader("India Production Trend (lakh MT)")
        prod_fig = px.area(
            india_df.sort_values("year"),
            x="year", y="production_volume", color="name",
            template="plotly_white",
            color_discrete_sequence=[GREEN, GOLD],
            labels={"year": "Year", "production_volume": "Production (lakh MT)", "name": "Crop"},
        )
        prod_fig.update_layout(margin=dict(t=10, b=10))
        st.plotly_chart(prod_fig, use_container_width=True)

        notes_df = india_df[india_df["notes"].str.startswith("Yield:", na=False)].copy()
        if not notes_df.empty:
            notes_df["yield_tha"] = notes_df["notes"].str.extract(r"([\d.]+) t/ha").astype(float)
            st.subheader("Yield per Hectare Trend (t/ha)")
            yield_fig = px.line(
                notes_df.sort_values("year"),
                x="year", y="yield_tha", color="name",
                markers=True, template="plotly_white",
                color_discrete_sequence=[STEEL_BLUE, OLIVE],
                labels={"year": "Year", "yield_tha": "Yield (t/ha)", "name": "Crop"},
            )
            yield_fig.update_traces(line_width=3, marker_size=9)
            yield_fig.update_layout(margin=dict(t=10, b=10))
            st.plotly_chart(yield_fig, use_container_width=True)
    else:
        st.info("No India MSP data available yet.")

    if not global_df.empty:
        st.markdown("---")
        st.subheader("Regional Production Breakdown")
        region_df = global_df.groupby("region")["production_volume"].sum().sort_values(ascending=False).reset_index()
        reg_fig = px.bar(
            region_df, x="region", y="production_volume",
            template="plotly_white", color_discrete_sequence=[STEEL_BLUE],
            labels={"region": "Region", "production_volume": "Total Production (ton)"},
        )
        reg_fig.update_layout(margin=dict(t=10, b=10))
        st.plotly_chart(reg_fig, use_container_width=True)

        st.subheader("Price vs Production Scatter")
        scatter_fig = px.scatter(
            global_df, x="price_per_unit", y="production_volume",
            color="category", size="production_volume",
            hover_name="name", template="plotly_white",
            color_discrete_sequence=COLORS,
            labels={"price_per_unit": "Price ($/kg)", "production_volume": "Production (ton)", "category": "Category"},
        )
        scatter_fig.update_layout(margin=dict(t=10, b=10))
        st.plotly_chart(scatter_fig, use_container_width=True)


elif page == "Settings":
    st.title("⚙️ Settings")
    st.markdown("Manage your profile and application preferences.")
    st.markdown("---")

    tab1, tab2, tab3 = st.tabs(["👤 Profile", "🔔 Notifications", "📤 Export Data"])

    with tab1:
        st.subheader("Profile Information")
        with st.form("profile_form"):
            p1, p2 = st.columns(2)
            with p1:
                st.text_input("Full Name", value="Vansh Rohilla")
                st.text_input("Email", value="vansh@agridash.com")
            with p2:
                st.text_input("Role", value="Farm Manager")
                st.selectbox("Region", ["North Region", "South Region", "East Region", "West Region", "Central Region"])
            if st.form_submit_button("Save Profile", type="primary"):
                st.success("✅ Profile saved!")

    with tab2:
        st.subheader("Notification Preferences")
        st.toggle("Price alerts (when price changes > 10%)", value=True)
        st.toggle("Weekly production summary", value=True)
        st.toggle("New crop record notifications", value=False)
        st.toggle("Seasonal reminders", value=True)
        if st.button("Save Notification Settings", type="primary"):
            st.success("✅ Notification preferences saved!")

    with tab3:
        st.subheader("Export Data")
        st.markdown("Download all crop data as a CSV file.")
        if not df_all.empty:
            csv = df_all.to_csv(index=False)
            st.download_button(
                label="📥 Download CSV",
                data=csv,
                file_name=f"agridash_crops_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                type="primary",
            )
        else:
            st.info("No data to export yet.")

        st.markdown("---")
        st.subheader("Database Summary")
        sc1, sc2, sc3 = st.columns(3)
        with sc1:
            st.metric("Total Records", stats["total"])
        with sc2:
            cats = df_all["category"].nunique() if not df_all.empty else 0
            st.metric("Categories", cats)
        with sc3:
            regions = df_all["region"].nunique() if not df_all.empty else 0
            st.metric("Regions", regions)
