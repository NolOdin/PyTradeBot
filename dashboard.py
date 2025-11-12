# dashboard.py
import streamlit as st
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt

st.title("ETH/USDT Bot Dashboard")

conn = sqlite3.connect('trades.db')
df = pd.read_sql("SELECT * FROM trades ORDER BY timestamp", conn)

st.write("### Последние сделки", df.tail(10))

fig, ax = plt.subplots()
ax.plot(df['timestamp'], df['price'], marker='o')
ax.set_title("Цена сделок")
st.pyplot(fig)

if st.button("Обновить"):
    st.experimental_rerun()
