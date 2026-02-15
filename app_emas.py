import streamlit as st
import sqlite3
import pandas as pd
import requests
import re
from datetime import datetime, timedelta
try:
    import plotly.graph_objects as go
    PLOTLY_AVAILABLE = True
except:
    PLOTLY_AVAILABLE = False

from news_berita import BeritaEmas
from price_alert import PriceAlert
from operasi_schedule import OperasiSchedule

# ============================================
# KONFIGURASI STREAMLIT
# ============================================
st.set_page_config(
    page_title="💰 arwin gold Wave - Dashboard Emas 24 Jam",
    page_icon="🏆",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS CUSTOM UNTUK EFEK FUTURISTIK
def inject_custom_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Roboto:wght@400;700&display=swap');
    
    * {
        font-family: 'Roboto', sans-serif;
    }
    
    h1, h2, h3 {
        font-family: 'Orbitron', monospace;
        text-shadow: 0 0 20px rgba(255, 215, 0, 0.5);
        color: #FFD700;
    }
    
    .metric-box {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        border: 2px solid #FFD700;
        border-radius: 15px;
        padding: 20px;
        box-shadow: 0 0 30px rgba(255, 215, 0, 0.3),
                    inset 0 0 20px rgba(255, 215, 0, 0.1);
        color: white;
        font-weight: bold;
    }
    
    .status-online {
        background: linear-gradient(135deg, #00d084 0%, #00a86b 100%);
        color: white;
        padding: 10px 15px;
        border-radius: 50px;
        display: inline-block;
        animation: pulse 2s infinite;
    }
    
    .status-offline {
        background: linear-gradient(135deg, #ff6b6b 0%, #ee5a6f 100%);
        color: white;
        padding: 10px 15px;
        border-radius: 50px;
        display: inline-block;
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.7; }
    }
    
    .chart-container {
        background: rgba(30, 30, 50, 0.8);
        border: 1px solid rgba(255, 215, 0, 0.3);
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 0 20px rgba(255, 215, 0, 0.2);
    }
    
    .news-card {
        background: linear-gradient(135deg, #0f3460 0%, #16213e 100%);
        border-left: 5px solid #FFD700;
        padding: 15px;
        margin: 10px 0;
        border-radius: 8px;
        color: white;
        box-shadow: 0 0 15px rgba(255, 215, 0, 0.2);
        transition: all 0.3s ease;
    }
    
    .news-card:hover {
        transform: translateX(5px);
        box-shadow: 0 0 25px rgba(255, 215, 0, 0.4);
    }
    
    .alert-badge {
        display: inline-block;
        padding: 5px 12px;
        border-radius: 20px;
        font-size: 0.8em;
        font-weight: bold;
        margin-right: 8px;
        text-transform: uppercase;
    }
    
    .badge-positif {
        background: #00d084;
        color: white;
    }
    
    .badge-negatif {
        background: #ff6b6b;
        color: white;
    }
    
    .badge-netral {
        background: #4a90e2;
        color: white;
    }
    
    .price-up {
        color: #00d084;
        font-weight: bold;
    }
    
    .price-down {
        color: #ff6b6b;
        font-weight: bold;
    }
    
    div[data-testid="stMetricValue"] {
        font-size: 2em !important;
    }
    
    .futuristic-header {
        background: linear-gradient(90deg, 
            rgba(255, 215, 0, 0.1) 0%,
            rgba(255, 215, 0, 0.3) 50%,
            rgba(255, 215, 0, 0.1) 100%);
        border-top: 3px solid #FFD700;
        border-bottom: 3px solid #FFD700;
        padding: 20px;
        margin: 20px 0;
        border-radius: 10px;
        text-align: center;
    }
    
    .grid-container {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 15px;
    }
    </style>
    """, unsafe_allow_html=True)

inject_custom_css()

# ============================================
# INISIALISASI SESSION STATE
# ============================================
if 'refresh_count' not in st.session_state:
    st.session_state.refresh_count = 0

# ============================================
# LOAD MODUL HELPER
# ============================================
@st.cache_resource
def load_modules():
    berita = BeritaEmas()
    alerts = PriceAlert()
    schedule = OperasiSchedule()
    return berita, alerts, schedule

berita_emas, price_alerts, operasi_schedule = load_modules()

# ============================================
# FUNGSI AMBIL DATA
# ============================================
@st.cache_data(ttl=300)
def load_data():
    """Load data dari database"""
    try:
        conn = sqlite3.connect("riwayat_emas.db")
        df = pd.read_sql_query(
            "SELECT waktu, harga FROM harga_emas ORDER BY id DESC LIMIT 100",
            conn
        )
        conn.close()
        return df.iloc[::-1] if not df.empty else pd.DataFrame(columns=['waktu', 'harga'])
    except:
        return pd.DataFrame(columns=['waktu', 'harga'])

def get_live_price():
    """Ambil harga emas terbaru"""
    try:
        url = "https://www.hargaemas.com/"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=5)
        match = re.search(r'2\.9[0-9]{2}\.[0-9]{3}', response.text)
        return match.group(0) if match else "N/A"
    except:
        return "N/A"

def format_harga(harga):
    """Format harga ke Rp"""
    if isinstance(harga, str):
        return harga
    return f"Rp {int(harga):,}".replace(",", ".")

def create_interactive_chart(df):
    """Buat chart interaktif dengan Plotly atau Streamlit Line Chart"""
    if df.empty:
        st.warning("📊 Database kosong. Jalankan aplikasi desktop untuk mengisi data.")
        return None
    
    if PLOTLY_AVAILABLE:
        try:
            import plotly.graph_objects as go
            fig = go.Figure()
            
            # Line chart
            fig.add_trace(go.Scatter(
                x=df['waktu'],
                y=df['harga'],
                mode='lines+markers',
                name='Harga Emas',
                line=dict(color='#FFD700', width=3),
                marker=dict(size=6, color='#FFD700', 
                           line=dict(color='#FFA500', width=2)),
                fill='tozeroy',
                fillcolor='rgba(255, 215, 0, 0.1)',
                hovertemplate='<b>%{x}</b><br>Rp %{y:,}<extra></extra>'
            ))
            
            fig.update_layout(
                title='📈 Grafik Pergerakan Harga Emas 24 Jam',
                xaxis_title='Waktu',
                yaxis_title='Harga (Rp)',
                hovermode='x unified',
                template='plotly_dark',
                paper_bgcolor='rgba(26, 26, 46, 0.8)',
                plot_bgcolor='rgba(22, 33, 62, 0.5)',
                font=dict(family='Arial, sans-serif', size=12, color='#FFD700'),
                height=500,
                margin=dict(l=50, r=50, t=80, b=50)
            )
            
            return fig
        except:
            return None
    else:
        # Fallback ke chart bawaan Streamlit
        return "streamlit"
def create_interactive_chart(df):
    """Buat chart interaktif ala TradingView dengan navigasi rentang waktu"""
    if df.empty:
        st.warning("📊 Database kosong. Jalankan aplikasi desktop untuk mengisi data.")
        return None
    
    # Pastikan kolom waktu adalah format datetime
    df['waktu'] = pd.to_datetime(df['waktu'])
    df = df.sort_values('waktu')

    fig = go.Figure()
    
    # Menambahkan Garis Utama (Line Chart)
    fig.add_trace(go.Scatter(
        x=df['waktu'],
        y=df['harga'],
        mode='lines',
        name='Harga Emas',
        line=dict(color='#FFD700', width=2),
        fill='tozeroy',
        fillcolor='rgba(255, 215, 0, 0.15)',
        hovertemplate='<b>Waktu:</b> %{x}<br><b>Harga:</b> Rp %{y:,.0f}<extra></extra>'
    ))
    
    # Konfigurasi Layout agar Mirip Trading Chart
    fig.update_layout(
        template='plotly_dark',
        hovermode='x unified',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=10, r=10, t=40, b=10),
        height=500,
        xaxis=dict(
            showgrid=True,
            gridcolor='rgba(255, 255, 255, 0.1)',
            # FITUR RANGESELECTOR: Tombol navigasi waktu
            rangeselector=dict(
                buttons=list([
                    dict(count=1, label="1 Jam", step="hour", stepmode="backward"),
                    dict(count=1, label="1 Hari", step="day", stepmode="backward"),
                    dict(count=7, label="1 Minggu", step="day", stepmode="backward"),
                    dict(count=1, label="1 Bulan", step="month", stepmode="backward"),
                    dict(count=1, label="1 Tahun", step="year", stepmode="backward"),
                    dict(step="all", label="Semua")
                ]),
                bgcolor="#16213e",
                activecolor="#FFD700",
                font=dict(color="white", size=11)
            ),
            rangeslider=dict(visible=False), # Slider di bawah (opsional)
            type='date'
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='rgba(255, 255, 255, 0.1)',
            side='right', # Harga biasanya di kanan pada chart trading
            tickformat=",.0f"
        )
    )
    
    return fig

# ============================================
# HEADER UTAMA
# ============================================
st.markdown(
    """
    <div class="futuristic-header">
        <h1>🏆 Arwinzz Gold Wave💰</h1>
        <p style="font-size: 1.2em; color: #FFD700;">Dashboard Monitoring Harga Emas Realtime 24 Jam</p>
    </div>
    """,
    unsafe_allow_html=True
)

# ============================================
# CEK STATUS OPERASIONAL
# ============================================
is_operasi, pesan_operasi = operasi_schedule.is_operasional()
status_html = f"""
<div style="text-align: center; margin: 20px 0;">
    <span class="{'status-online' if is_operasi else 'status-offline'}">
        {'🟢 OPERASIONAL' if is_operasi else '🔴 TUTUP'} - {pesan_operasi}
    </span>
</div>
"""
st.markdown(status_html, unsafe_allow_html=True)

if not is_operasi:
    st.error("""
    ⏰ Sistem Maintenance Rutin
    - Website ditutup pada hari Sabtu & Minggu
    - Dibuka kembali Senin jam 00:00 WIB
    - Terima kasih atas pengertian Anda!
    """)

# ============================================
# TAB NAVIGASI
# ============================================
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Dashboard",
    "📰 Berita & Analisis",
    "🔔 Price Alert",
    "📥 Download",
    "⚙️ Pengaturan"
])

# ============================================
# TAB 1: DASHBOARD UTAMA
# ============================================
with tab1:
    st.markdown("###  Dashboard Utama")
    
    # Load data
    df_history = load_data()
    live_price_str = get_live_price()
    
    # Convert to numeric
    try:
        live_price = float(live_price_str.replace(".", "")) if live_price_str != "N/A" else None
    except:
        live_price = None
    
    # Kalkulasi perubahan harga
    price_change = None
    price_change_pct = None
    if not df_history.empty and live_price:
        previous_price = df_history['harga'].iloc[0]
        price_change = live_price - previous_price
        price_change_pct = (price_change / previous_price * 100) if previous_price != 0 else 0
    
    # Metrik Utama
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-box">
            <h3> Harga Saat Ini</h3>
            <p style="font-size: 1.5em; color: #FFD700;">{format_harga(live_price_str)}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        if not df_history.empty:
            last_price = df_history['harga'].iloc[-1]
            st.markdown(f"""
            <div class="metric-box">
                <h3>📈 Terakhir Dicatat</h3>
                <p style="font-size: 1.5em; color: #FFD700;">{format_harga(last_price)}</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="metric-box">
                <h3>📈 Terakhir Dicatat</h3>
                <p style="font-size: 1.5em; color: #FFD700;">-</p>
            </div>
            """, unsafe_allow_html=True)
    
    with col3:
        if price_change is not None:
            color = "color: #00d084;" if price_change >= 0 else "color: #ff6b6b;"
            sign = "+" if price_change >= 0 else ""
            st.markdown(f"""
            <div class="metric-box">
                <h3>📊 Perubahan</h3>
                <p style="font-size: 1.5em; {color}">{sign}{int(price_change)}</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="metric-box">
                <h3>📊 Perubahan</h3>
                <p style="font-size: 1.5em; color: #FFD700;">-</p>
            </div>
            """, unsafe_allow_html=True)
    
    with col4:
        if price_change_pct is not None:
            color = "color: #00d084;" if price_change_pct >= 0 else "color: #ff6b6b;"
            sign = "+" if price_change_pct >= 0 else ""
            st.markdown(f"""
            <div class="metric-box">
                <h3>📈 Perubahan %</h3>
                <p style="font-size: 1.5em; {color}">{sign}{price_change_pct:.2f}%</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="metric-box">
                <h3>📈 Perubahan %</h3>
                <p style="font-size: 1.5em; color: #FFD700;">-</p>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Grafik Utama
    st.markdown("### 📈 Grafik Pergerakan Harga")
    fig = create_interactive_chart(df_history)
    if fig:
        if fig == "streamlit":
            # Gunakan chart bawaan Streamlit (fallback)
            st.line_chart(data=df_history, x='waktu', y='harga', use_container_width=True)
        else:
            # Gunakan Plotly chart
            st.plotly_chart(fig, use_container_width=True)
    
    # Statistik
    st.markdown("### 📊 Statistik Harga")
    if not df_history.empty:
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric("Harga Tertinggi", format_harga(df_history['harga'].max()))
        with col2:
            st.metric("Harga Terendah", format_harga(df_history['harga'].min()))
        with col3:
            st.metric("Harga Rata-rata", format_harga(df_history['harga'].mean()))
        with col4:
            st.metric("Total Entry", len(df_history))
        with col5:
            st.metric("Update Terakhir", df_history['waktu'].iloc[-1])
    
    # Data Tabel
    st.markdown("### 📋 Tabel Data Terakhir")
    if not df_history.empty:
        display_df = df_history.tail(20).copy()
        display_df['harga'] = display_df['harga'].apply(lambda x: format_harga(x))
        st.dataframe(display_df, use_container_width=True, height=400)

# ============================================
# TAB 2: BERITA & ANALISIS
# ============================================
with tab2:
    st.markdown("### 📰 Berita & Analisis Emas")
    
    # Filter kategori
    all_berita = berita_emas.get_berita_list()
    kategori_list = berita_emas.get_kategori_list()
    
    col1, col2, col3 = st.columns([2, 2, 2])
    with col1:
        kategori_filter = st.selectbox(
            "Filter Kategori",
            ["Semua Berita"] + kategori_list,
            key="kategori_filter"
        )
    
    with col2:
        if st.button("🔄 Refresh Berita"):
            st.cache_data.clear()
    
    # Tampilkan berita
    if kategori_filter == "Semua Berita":
        berita_display = all_berita
    else:
        berita_display = berita_emas.get_berita_by_kategori(kategori_filter)
    
    if berita_display:
        for idx, berita in enumerate(berita_display):
            badge_class = {
                "Positif": "badge-positif",
                "Negatif": "badge-negatif",
                "Netral": "badge-netral"
            }.get(berita['dampak'], "badge-netral")
            
            st.markdown(f"""
            <div class="news-card">
                <h4>{berita['judul']}</h4>
                <p>{berita['deskripsi']}</p>
                <div style="margin-top: 10px;">
                    <span class="alert-badge {badge_class}">{berita['dampak']}</span>
                    <span style="color: #999; font-size: 0.9em;">
                        📅 {berita['tanggal']} | 🏷️ {berita['kategori']}
                    </span>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Tidak ada berita untuk kategori ini.")
    
    # Form tambah berita
    st.markdown("---")
    st.markdown("### ➕ Tambah Berita Baru")
    
    col1, col2 = st.columns(2)
    with col1:
        judul_berita = st.text_input("Judul Berita")
        kategori_berita = st.selectbox(
            "Kategori",
            kategori_list + ["Kategori Baru..."],
            key="kategori_berita_baru"
        )
        if kategori_berita == "Kategori Baru...":
            kategori_berita = st.text_input("Kategori Baru")
    
    with col2:
        deskripsi_berita = st.text_area("Deskripsi Berita")
        dampak_berita = st.selectbox(
            "Dampak terhadap Harga Emas",
            ["Positif", "Negatif", "Netral"],
            key="dampak_berita"
        )
    
    if st.button("📤 Tambahkan Berita"):
        if judul_berita and deskripsi_berita and kategori_berita:
            berita_emas.add_berita(judul_berita, deskripsi_berita, kategori_berita, dampak_berita)
            st.success("✅ Berita berhasil ditambahkan!")
            st.rerun()
        else:
            st.error("⚠️ Mohon isi semua field terlebih dahulu!")

# ============================================
# TAB 3: PRICE ALERT
# ============================================
with tab3:
    st.markdown("### 🔔 Price Alert - Notifikasi Harga")
    st.write("Atur harga target untuk memberi tahu Anda kapan waktu yang tepat untuk beli atau jual emas!")
    
    col1, col2, col3 = st.columns([1, 2, 2])
    
    with col1:
        st.markdown("### ➕ Buat Alert Baru")
        nama_pengguna = st.text_input("Nama Anda", key="nama_alert")
        harga_beli = st.number_input("Harga Target BELI (Rp)", min_value=100000, step=1000, key="harga_beli")
        harga_jual = st.number_input("Harga Target JUAL (Rp)", min_value=100000, step=1000, key="harga_jual")
        
        if st.button("🔔 Buat Alert", use_container_width=True):
            if nama_pengguna:
                alert_id = price_alerts.tambah_alert(nama_pengguna, int(harga_beli), int(harga_jual))
                st.success(f"✅ Alert ID #{alert_id} berhasil dibuat!")
                st.rerun()
            else:
                st.error("⚠️ Mohon isi nama Anda!")
    
    with col2:
        st.markdown("### 📋 Alert Aktif Anda")
        # Untuk demo, tampilkan semua alert
        alerts = price_alerts.get_semua_alerts()
        
        if alerts:
            for alert in alerts:
                alert_id, nama, beli, jual, status, tgl_buat = alert[:6]
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #0f3460 0%, #16213e 100%);
                            border-left: 5px solid #FFD700; padding: 15px; margin: 10px 0;
                            border-radius: 8px; color: white;">
                    <strong>👤 {nama}</strong> (ID: #{alert_id})<br>
                    🛍️ BELI di: <span style="color: #00d084;">Rp {beli:,}</span><br>
                    💰 JUAL di: <span style="color: #ff6b6b;">Rp {jual:,}</span><br>
                    <small style="color: #999;">Dibuat: {tgl_buat}</small>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("Belum ada alert aktif. Buat alert baru untuk memulai!")
    
    with col3:
        st.markdown("### 📊 Status Alert Sekarang")
        live_price_str = get_live_price()
        try:
            live_price = float(live_price_str.replace(".", "")) if live_price_str != "N/A" else None
        except:
            live_price = None
        
        if live_price:
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
                        border: 2px solid #FFD700; padding: 15px; border-radius: 10px;
                        text-align: center; color: #FFD700;">
                <h3>💎 Harga Sekarang</h3>
                <p style="font-size: 2em; font-weight: bold;">{format_harga(live_price)}</p>
            </div>
            """, unsafe_allow_html=True)
            
            if alerts:
                st.markdown("#### ⚠️ Alert Terpicu")
                triggered = price_alerts.check_alert(live_price)
                if triggered:
                    for alert in triggered:
                        if alert['tipe'] == 'BELI':
                            st.success(f"🟢 {alert['pesan']}")
                        else:
                            st.warning(f"🔴 {alert['pesan']}")
                else:
                    st.info("Tidak ada alert yang terpicu.")

# ============================================
# TAB 4: DOWNLOAD
# ============================================
with tab4:
    st.markdown("### 📥 Download Data")
    
    df_history = load_data()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📊 Export ke CSV")
        if not df_history.empty:
            csv = df_history.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download CSV",
                data=csv,
                file_name=f'data_emas_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv',
                mime='text/csv',
                use_container_width=True
            )
        else:
            st.warning("Database kosong.")
    
    with col2:
        st.markdown("### 📋 Export ke Excel")
        if not df_history.empty:
            # Perlu install openpyxl untuk Excel
            try:
                excel_data = df_history.to_excel(
                    f'data_emas_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx',
                    index=False
                )
                st.success("✅ File Excel siap diunduh dari folder aplikasi!")
            except:
                st.info("Untuk export Excel, jalankan: pip install openpyxl")
        else:
            st.warning("Database kosong.")
    
    st.markdown("---")
    st.markdown("### 📈 Ringkasan Data")
    if not df_history.empty:
        st.dataframe(
            df_history.describe().T,
            use_container_width=True
        )

# ============================================
# TAB 5: PENGATURAN
# ============================================
with tab5:
    st.markdown("### ⚙️ Pengaturan Sistem")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🔄 Pengaturan Update Data")
        refresh_interval = st.slider("Interval Refresh (detik)", 30, 300, 60)
        st.info(f"Data akan di-refresh setiap {refresh_interval} detik")
        
        if st.button("🔄 Refresh Data Sekarang", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
    
    with col2:
        st.markdown("#### 📆 Status Operasional")
        status_info = operasi_schedule.get_status_operasi()
        st.info(f"""
        **Status:** {status_info['pesan']}
        **Waktu:** {status_info['waktu_sekarang']}
        **Hari:** {status_info['hari']}
        **Jam:** {status_info['jam']}
        """)
    
    st.markdown("---")
    st.markdown("#### 📊 Informasi Sistem")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Database File", "riwayat_emas.db")
    with col2:
        st.metric("Alert Database", "price_alerts.db")
    with col3:
        st.metric("Versi App", "2.0 Pro")
    
    st.markdown("---")
    st.markdown("#### 💡 Tips & Panduan")
    st.info("""
    **📱 Akses dari Mobile:**
    - Pastikan laptop dan HP terhubung ke WiFi yang sama
    - Buka di browser: http://[IP-LAPTOP]:8501
    
    **📊 Menggunakan Alert:**
    - Set harga BELI lebih rendah dari harga sekarang
    - Set harga JUAL lebih tinggi dari harga sekarang
    - Alert akan notif ketika harga mencapai target
    
    **🔄 Update Otomatis:**
    - Gunakan aplikasi desktop (emas.py) untuk auto-update harga
    - Website akan menampilkan data real-time
    
    **📅 Jadwal Operasional:**
    - Senin-Jumat: Website OPERASIONAL 24 jam
    - Sabtu-Minggu: Website TUTUP untuk maintenance
    """)

# ============================================
# FOOTER
# ============================================
st.markdown("---")
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("**Developed by:** Gold Tracker Team")
with col2:
    st.markdown("**Last Update:** 2026-02-08")
with col3:
    st.markdown("**Version:** 2.0 Pro Edition")


