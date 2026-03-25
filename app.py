import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

st.set_page_config(page_title="AgriDash", layout="wide")

# ---------------- SESSION STATE ----------------
if "confirm_delete_id" not in st.session_state:
    st.session_state.confirm_delete_id = None

# ---------------- SAMPLE DATA ----------------
def load_data():
    return pd.DataFrame([
        {
            "id": 1, "name": "Wheat", "category": "Grain",
            "price_per_unit": 2200, "unit": "quintal",
            "production_volume": 110, "production_unit": "lakh MT",
            "region": "North", "season": "Rabi", "year": 2023,
            "notes": "Yield: 3.5 t/ha"
        },
        {
            "id": 2, "name": "Rice", "category": "Grain",
            "price_per_unit": 2100, "unit": "quintal",
            "production_volume": 130, "production_unit": "lakh MT",
            "region": "East", "season": "Kharif", "year": 2023,
            "notes": "Yield: 4.2 t/ha"
        }
    ])

df_all = load_data()

# ---------------- FUNCTIONS ----------------
def update_crop(crop_id, new_data):
    global df_all
    for key, value in new_data.items():
        df_all.loc[df_all["id"] == crop_id, key] = value

def delete_crop(crop_id):
    global df_all
    df_all = df_all[df_all["id"] != crop_id]

# ---------------- UI ----------------
page = st.sidebar.radio("Navigation", ["Dashboard", "Edit", "Analytics", "Settings"])

# ---------------- DASHBOARD ----------------
if page == "Dashboard":
    st.title("🌾 Crop Dashboard")

    display_cols = [
        "id", "name", "category", "price_per_unit", "unit",
        "production_volume", "production_unit",
        "region", "season", "year", "notes"
    ]

    filtered = df_all.copy()

    cols = [c for c in display_cols if c in filtered.columns]

    st.dataframe(
        filtered[cols].rename(columns={
            "id": "ID",
            "name": "Name",
            "category": "Category",
            "price_per_unit": "Price",
            "unit": "Price Unit",
            "production_volume": "Production",
            "production_unit": "Prod. Unit",
            "region": "Region",
            "season": "Season",
            "year": "Year",
            "notes": "Notes",
        }),
        use_container_width=True,
        height=400,
        hide_index=True,
    )

# ---------------- EDIT PAGE ----------------
elif page == "Edit":
    st.title("✏️ Edit / Delete Crop")

    crop_options = {f"{row['id']} — {row['name']}": row["id"] for _, row in df_all.iterrows()}
    selected_label = st.selectbox("Select crop", list(crop_options.keys()))
    selected_id = crop_options[selected_label]

    row = df_all[df_all["id"] == selected_id].iloc[0]

    col1, col2 = st.columns(2)

    # -------- EDIT --------
    with col1:
        with st.form("edit_form"):
            st.subheader("Edit Crop")

            name = st.text_input("Name", value=row["name"])
            category = st.selectbox("Category", ["Grain","Vegetable","Fruit","Other"])
            price = st.number_input("Price", value=float(row["price_per_unit"]))
            unit = st.text_input("Unit", value=row["unit"])
            production = st.number_input("Production", value=float(row["production_volume"]))
            prod_unit = st.text_input("Production Unit", value=row["production_unit"])
            region = st.text_input("Region", value=row["region"])
            season = st.selectbox("Season", ["Kharif","Rabi","Zaid"])
            year = st.number_input("Year", value=int(row["year"]))
            notes = st.text_area("Notes", value=row["notes"])

            if st.form_submit_button("💾 Save"):
                update_crop(selected_id, {
                    "name": name,
                    "category": category,
                    "price_per_unit": price,
                    "unit": unit,
                    "production_volume": production,
                    "production_unit": prod_unit,
                    "region": region,
                    "season": season,
                    "year": int(year),
                    "notes": notes,
                })
                st.success("Updated successfully")
                st.rerun()

    # -------- DELETE --------
    with col2:
        st.subheader("Delete Crop")
        st.warning(f"Delete {row['name']} permanently")

        if st.button("🗑️ Delete"):
            st.session_state.confirm_delete_id = selected_id

        if st.session_state.confirm_delete_id == selected_id:
            st.error("Are you sure?")
            c1, c2 = st.columns(2)

            with c1:
                if st.button("Yes Delete"):
                    delete_crop(selected_id)
                    st.session_state.confirm_delete_id = None
                    st.success("Deleted")
                    st.rerun()

            with c2:
                if st.button("Cancel"):
                    st.session_state.confirm_delete_id = None
                    st.rerun()

# ---------------- ANALYTICS ----------------
elif page == "Analytics":
    st.title("📈 Analytics")

    fig = px.line(df_all, x="year", y="price_per_unit", color="name", markers=True)
    st.plotly_chart(fig, use_container_width=True)

    fig2 = px.bar(df_all, x="name", y="production_volume", color="region")
    st.plotly_chart(fig2, use_container_width=True)

# ---------------- SETTINGS ----------------
elif page == "Settings":
    st.title("⚙️ Settings")

    st.subheader("Export Data")

    csv = df_all.to_csv(index=False)

    st.download_button(
        label="📥 Download CSV",
        data=csv,
        file_name=f"crops_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )

    st.success("App running perfectly 🚀")
