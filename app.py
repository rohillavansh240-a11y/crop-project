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

# CSV fallback
CSV_FILE = "crop_data.csv"

# Database URL (optional)
DATABASE_URL = os.environ.get("DATABASE_URL", "")

# -------------------
# Data access functions
# -------------------
if DATABASE_URL:
    import psycopg2
    from psycopg2.extras import RealDictCursor

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

else:
    # CSV fallback
    def load_crops():
        try:
            df = pd.read_csv(CSV_FILE)
        except FileNotFoundError:
            df = pd.DataFrame(columns=[
                "id","name","category","price_per_unit","unit","production_volume",
                "production_unit","region","season","year","notes"
            ])
        return df

    def save_crops(df):
        df.to_csv(CSV_FILE, index=False)

    def insert_crop(data):
        df = load_crops()
        data["id"] = df["id"].max() + 1 if not df.empty else 1
        df = pd.concat([df, pd.DataFrame([data])], ignore_index=True)
        save_crops(df)

    def update_crop(crop_id, data):
        df = load_crops()
        idx = df.index[df["id"] == crop_id][0]
        for key in data:
            df.at[idx, key] = data[key]
        save_crops(df)

    def delete_crop(crop_id):
        df = load_crops()
        df = df[df["id"] != crop_id]
        save_crops(df)

# -------------------
# Stats function (common)
# -------------------
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

# -------------------
# Rest of your app remains the same
# -------------------
# (sidebar, dashboard, crops, analytics, settings)
