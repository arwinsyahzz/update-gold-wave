"""
CONFIG.PY - Konfigurasi Aplikasi Gold Tracker PRO
Ubah setting di sini untuk kustomisasi aplikasi
"""

# ==========================================
# DATABASE SETTINGS
# ==========================================
DB_HARGA = "riwayat_emas.db"  # Database harga emas
DB_ALERTS = "price_alerts.db"  # Database price alerts

# ==========================================
# HARGA EMAS SETTINGS
# ==========================================
HARGA_SOURCE_URL = "https://www.hargaemas.com/"
HARGA_REGEX_PATTERN = r'2\.9[0-9]{2}\.[0-9]{3}'  # Pattern untuk regex scraping

# ==========================================
# STREAMLIT SETTINGS
# ==========================================
PAGE_TITLE = "💰 Arwinzz Gold Wave - Dashboard Emas 24 Jam"
PAGE_ICON = "🏆"
PAGE_LAYOUT = "wide"

# Cache settings (dalam detik)
CACHE_TTL_DATA = 300  # Cache data 5 menit
CACHE_TTL_NEWS = 600  # Cache berita 10 menit

# Default refresh interval
DEFAULT_REFRESH_INTERVAL = 60  # dalam detik

# ==========================================
# OPERATIONAL SCHEDULE
# ==========================================
HARI_TUTUP = [5, 6]  # 5=Sabtu, 6=Minggu (ISO weekday)
JAM_BUKA = 0  # Jam 00:00 (midnight)
JAM_BUKA_MENIT = 0  # Menit 00

TIMEZONE = "Asia/Jakarta"

# Pesan status
PESAN_OPERASIONAL = "Website OPERASIONAL"
PESAN_TUTUP = "Website TUTUP - Hari Libur. Buka lagi Senin jam 00:00 WIB"

# ==========================================
# PRICE ALERT SETTINGS
# ==========================================
MIN_HARGA_ALERT = 100000  # Harga minimum Rp
MAX_HARGA_ALERT = 10000000  # Harga maksimum Rp
STEP_HARGA_ALERT = 1000  # Step increment harga

# ==========================================
# UI/STYLING
# ==========================================
WARNA_UTAMA = "#FFD700"  # Emas/Gold
WARNA_POSITIF = "#00d084"  # Hijau
WARNA_NEGATIF = "#ff6b6b"  # Merah
WARNA_NETRAL = "#4a90e2"  # Biru

FONT_HEADER = "'Orbitron', monospace"
FONT_BODY = "'Roboto', sans-serif"

# ==========================================
# CHART SETTINGS
# ==========================================

CHART_HEIGHT = 100
CHART_LIMIT_DATA = 100 # Ambil 100 data terakhir

# ==========================================
# BERITA SETTINGS
# ==========================================
BERITA_LIMIT = 20  # Tampilkan 20 berita per page

KATEGORI_DEFAULT = [
    "Suku Bunga",
    "Geopolitik",
    "Ekonomi",
    "Pasar",
    "Nilai Tukar"
]

DAMPAK_OPTIONS = ["Positif", "Negatif", "Netral"]

# ==========================================
# API SETTINGS (untuk future expansion)
# ==========================================
ENABLE_API = False  # Enable/disable REST API
API_PORT = 8000

# ==========================================
# LOGGING
# ==========================================
ENABLE_LOGGING = True
LOG_FILE = "gold_tracker.log"
LOG_LEVEL = "INFO"

# ==========================================
# SECURITY
# ==========================================
REQUIRE_PASSWORD = False  # Buka dengan password
PASSWORD_HASH = None  # Hash password jika diperlukan
