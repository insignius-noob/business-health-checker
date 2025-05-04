import streamlit as st
from datetime import datetime, timedelta
import pandas as pd
from sklearn.cluster import KMeans
import numpy as np
import requests

st.set_page_config(page_title='Business Health Checker')

st.title("💼 Business Health Checker")
st.markdown("### Helping Your Business Understand its Financial Health")
st.markdown("""
Welcome to your Business's Health Checker!  
This app helps you analyze your business performance using your financial data. 
""")
st.markdown("---")

st.image(r"C:\\University\\Semester 6\\Financial Programming\\Assignment 3\\BusinessHealthApp\\Finance_Home_Image.jpg", use_container_width=True)

st.sidebar.header("📂 Upload Business Data")
uploaded_file = st.sidebar.file_uploader('Upload a CSV file', type=['csv'])

st.sidebar.markdown("— or —")
use_sample = st.sidebar.button("📄 Load Sample Data Instead")

if "df" not in st.session_state:
    st.session_state.df = None

if uploaded_file is not None:
    st.session_state.df = pd.read_csv(uploaded_file)
elif use_sample:
    st.session_state.df = pd.read_csv("sample_data.csv")

df = st.session_state.df

if df is None:
    st.info("ℹ️ Please upload your business data in CSV format or use the sample file.")

if df is not None:
    required_cols = ["Business", "Revenue", "COGS", "Net_Profit", 
                     "Current_Assets", "Current_Liabilities", 
                     "Debt", "Equity", "Inventory"]

    missing_cols = [col for col in required_cols if col not in df.columns]

    if missing_cols:
        st.error("🚨 Your file is missing these required columns:")
        st.write(missing_cols)
        st.warning("Please upload a file with all the correct columns or use the sample file.")
    else:
        st.subheader("📄 Business Data")
        st.dataframe(df)

        st.markdown("---")
        st.subheader("📈 Calculated Financial Health Metrics")

        df["Gross_Profit_Margin"] = (df['Revenue'] - df['COGS']) / df['Revenue']
        df['Net_Profit_Margin'] = df['Net_Profit'] / df['Revenue']
        df['Current_Ratio'] = df['Current_Assets'] / df['Current_Liabilities']
        df['Debt_to_Equity'] = df['Debt'] / df['Equity']
        df['Inventory_Turnover'] = df['COGS'] / df['Inventory']

        metrics_df = df[["Business", "Gross_Profit_Margin", "Net_Profit_Margin", 
                         "Current_Ratio", "Debt_to_Equity", "Inventory_Turnover"]]
        st.dataframe(metrics_df.style.format({
            "Gross_Profit_Margin": "{:.2f}",
            "Net_Profit_Margin": "{:.2f}",
            "Current_Ratio": "{:.2f}",
            "Debt_to_Equity": "{:.2f}",
            "Inventory_Turnover": "{:.2f}"
        }))

        st.markdown("---")
        st.subheader("🤖 Risk Grouping")

        features = df[['Gross_Profit_Margin', 'Net_Profit_Margin', 
                       'Current_Ratio', 'Debt_to_Equity', 'Inventory_Turnover']]

        features = features.replace([np.inf, -np.inf], np.nan).dropna()

        kmeans = KMeans(n_clusters=3, random_state=42)
        df.loc[features.index, 'Risk_Clust'] = kmeans.fit_predict(features)


        label_map = {
            0: "🟢 Healthy",
            1: "🟡 Moderate Risk",
            2: "🔴 High Risk"
        }

        df['Risk_Label'] = df['Risk_Clust'].map(label_map)

        st.subheader("📊 Risk Assessment Results")
        st.dataframe(df[["Business", "Risk_Label"]])

        st.markdown("---")
st.subheader("📰 Latest Business News")

NEWS_API_KEY = "pub_84728c9d44c96cef7c6ae6780b9fc2a1c7923"  

url = f"https://newsdata.io/api/1/news?apikey={NEWS_API_KEY}&category=business&country=pk&language=en"

try:
    response = requests.get(url)
    news_data = response.json()

    if news_data.get("status") == "success" and news_data.get("results"):
        articles = news_data["results"][:5]  # show top 5 articles
        for article in articles:
            st.markdown(f"**{article['title']}**")
            st.caption(article.get("pubDate", ""))
            st.write(article.get("description", "No description available"))
            if article.get("link"):
                st.markdown(f"[Read more]({article['link']})")
            st.markdown("---")
    else:
        st.warning("⚠️ No news articles found.")
except Exception as e:
    st.error("🚨 Error fetching news from API.")
    st.exception(e)

