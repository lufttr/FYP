import base64
import streamlit as st
import pandas as pd
import warnings

warnings.filterwarnings('ignore')

def set_bg_image(image_file):
    with open(image_file, "rb") as file:
        btn = base64.b64encode(file.read()).decode()

    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("data:image/png;base64,{btn}");
            background-size: cover;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

set_bg_image("Football_New2.png")

st.title("Football Player's Performance Analysis using Data Analytics Approach")
st.markdown("#### Streamlit Application developed by Aluf Adil (TP062240) from APD3F2305CS(DA)")

# Welcome Message
st.markdown("""
Hi! I'm Aluf, a student from Asia Pacific University doing a Bachelor of Science (Hons) in Computer Science with a Specialization in Data Analytics.

This Streamlit Application is my Final Year Project where I aim to analyze a football player's performance using various data analytics techniques. Data for this project was obtained on [Kaggle](https://www.kaggle.com/datasets/beridzeg45/top-league-footballer-stats-2000-2023-seasons/data) and was cleaned and modified to fit into the requirements necessary for this project.

The features in this application include being able to search for specific players or teams and comparing their statistics with each other. The appropriate visualizations are provided with these searches and comparisons. Users will be able to obtain a prediction for how many goals a player will score in the 2023/2024 season using the predictor function, which utilizes a Random Forest Regressor model to calculate the prediction.
""")
