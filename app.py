import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression

# Page settings
st.set_page_config(page_title="Crop Dashboard", layout="wide")

# Title
st.title("🌾 Crop Price & Production Dashboard")

# Load data
data = pd.read_csv("crop_data.csv")

# Sidebar
st.sidebar.header("Select Options")
crop = st.sidebar.selectbox("🌱 Select Crop", data['Crop'].unique())
year = st.sidebar.number_input("📅 Enter Year", 2000, 2035)

# -------- SETTINGS OPTIONS --------
st.sidebar.subheader("🔧 Display Settings")

show_graph = st.sidebar.checkbox("Show Graph", True)
show_data = st.sidebar.checkbox("Show Raw Data", False)

theme = st.sidebar.selectbox("Theme", ["Light", "Dark"])
graph_style = st.sidebar.selectbox("Graph Style", ["Default", "ggplot", "seaborn"])

# Apply graph style
if graph_style == "ggplot":
    plt.style.use("ggplot")
elif graph_style == "seaborn":
    plt.style.use("seaborn")
else:
    plt.style.use("default")

# Filter data
filtered_data = data[data['Crop'] == crop]

# Model
X = filtered_data[['Year']]
y_price = filtered_data['Price']
y_production = filtered_data['Production']

price_model = LinearRegression()
production_model = LinearRegression()

price_model.fit(X, y_price)
production_model.fit(X, y_production)

# Prediction
if st.sidebar.button("🚀 Predict"):
    price = price_model.predict([[year]])
    production = production_model.predict([[year]])

    col1, col2 = st.columns(2)

    col1.metric("💰 Price", f"{price[0]:.2f}")
    col2.metric("🌾 Production", f"{production[0]:.2f}")

# Graph
st.subheader("📊 Crop Data Graph")

fig, ax = plt.subplots()
ax.plot(filtered_data['Year'], filtered_data['Price'], label="Price")
ax.plot(filtered_data['Year'], filtered_data['Production'], label="Production")

ax.set_xlabel("Year")
ax.set_ylabel("Value")
ax.legend()

st.pyplot(fig)
