import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

data = pd.read_csv("crop_data.csv")

crop = st.selectbox("Select Crop", data['Crop'].unique())
year = st.number_input("Enter Year", 2000, 2035)

if st.button("Predict"):
    st.success("Prediction shown")

# 👇 Graph code नीचे
if st.button("Show Graph"):
    filtered_data = data[data['Crop'] == crop]

    fig, ax = plt.subplots()
    ax.plot(filtered_data['Year'], filtered_data['Price'], marker='o')
    ax.set_xlabel("Year")
    ax.set_ylabel("Price")
    ax.set_title("Price Trend")

    st.pyplot(fig)