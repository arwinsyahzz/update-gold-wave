import requests
from bs4 import BeautifulSoup
from datetime import datetime
import json

class BeritaEmas:
    def __init__(self):
        self.berita_manual = [
            {
                "judul": "Federal Reserve Kurangi Suku Bunga",
                "deskripsi": "Bank sentral AS mengurangi suku bunga sebesar 0.5%, kemungkinan mendorong permintaan emas",
                "kategori": "Suku Bunga",
                "tanggal": "2026-02-08",
                "dampak": "Positif"
            },
            {
                "judul": "Konflik Geopolitik Meningkat di Timur Tengah",
                "deskripsi": "Ketegangan geopolitik mendorong investor mencari safe haven, emas melonjak 2%",
                "kategori": "Geopolitik",
                "tanggal": "2026-02-07",
                "dampak": "Positif"
            },
            {
                "judul": "Inflasi Turun ke Level Terendah 2 Tahun",
                "deskripsi": "Data inflasi menunjukkan penurunan signifikan, mempengaruhi valuasi emas",
                "kategori": "Ekonomi",
                "tanggal": "2026-02-06",
                "dampak": "Netral"
            },
            {
                "judul": "China Tingkatkan Cadangan Emas",
                "deskripsi": "China menambah cadangan emas mereka sebesar 50 ton, strategi diversifikasi mata uang",
                "kategori": "Pasar",
                "tanggal": "2026-02-05",
                "dampak": "Positif"
            },
            {
                "judul": "Dolar Menguat Terhadap Mata Uang Lainnya",
                "deskripsi": "Penguatan dolar membuat harga emas tertekan di pasar internasional",
                "kategori": "Nilai Tukar",
                "tanggal": "2026-02-04",
                "dampak": "Negatif"
            }
        ]
    
    def get_berita_list(self):
        """Ambil daftar berita"""
        return self.berita_manual
    
    def get_berita_by_kategori(self, kategori):
        """Ambil berita berdasarkan kategori"""
        return [b for b in self.berita_manual if b['kategori'].lower() == kategori.lower()]
    
    def add_berita(self, judul, deskripsi, kategori, dampak):
        """Tambah berita baru"""
        berita_baru = {
            "judul": judul,
            "deskripsi": deskripsi,
            "kategori": kategori,
            "tanggal": datetime.now().strftime("%Y-%m-%d"),
            "dampak": dampak
        }
        self.berita_manual.insert(0, berita_baru)
        return berita_baru
    
    def get_kategori_list(self):
        """Ambil daftar kategori unik"""
        return list(set([b['kategori'] for b in self.berita_manual]))
