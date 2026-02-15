import streamlit as st
import sqlite3
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random
import os

st.set_page_config(page_title="Harga Emas", layout="wide")
st.title("📈 Grafik Harga Emas per Jam")

# =========================
# RESET DATABASE OTOMATIS (1 KALI)
# =========================
if not os.path.exists("emas.db"):
    conn = sqlite3.connect("emas.db")
else:
    conn = sqlite3.connect("emas.db")

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS harga_emas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    waktu TEXT,
    harga INTEGER
)
""")
conn.commit()

# =========================
# ISI DATA 24 JAM PASTI
# =========================
cursor.execute("SELECT COUNT(*) FROM harga_emas")
if cursor.fetchone()[0] < 2:
    now = datetime.now().replace(minute=0, second=0, microsecond=0)
    harga = 2700000

    for i in range(24):
        harga += random.randint(-20000, 30000)
        waktu = now - timedelta(hours=23 - i)

        cursor.execute(
            "INSERT INTO harga_emas (waktu, harga) VALUES (?, ?)",
            (waktu, harga)
        )
    conn.commit()

# =========================
# AMBIL DATA
# =========================
df = pd.read_sql(
    "SELECT waktu, harga FROM harga_emas ORDER BY waktu ASC",
    conn
)
df["waktu"] = pd.to_datetime(df["waktu"])

st.write("JUMLAH DATA:", len(df))

# =========================
# CHART GARIS KUNING
# =========================
fig = go.Figure()
fig.add_trace(go.Scatter(
    x=df["waktu"],
    y=df["harga"],
    mode="lines",   # GARIS
    line=dict(color="#FFD700", width=4),
    fill="tozeroy",
    fillcolor="rgba(255,215,0,0.35)"
))

fig.update_layout(
    showlegend=False,
    template="simple_white",
    xaxis=dict(showgrid=False, tickformat="%H:%M"),
    yaxis=dict(showgrid=False)
)

st.plotly_chart(fig, use_container_width=True)