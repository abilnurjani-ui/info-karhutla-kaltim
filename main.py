from datetime import datetime, timezone, timedelta
import json
from google.auth.credentials import AnonymousCredentials
from google.cloud import firestore

# ==========================================
# 1. PERSIAPAN DATA & TANGGAL (FIX ZONA WAKTU WITA)
# ==========================================
print("🔍 Memulai proses update data Karhutla...")

# Mengunci zona waktu ke WITA (UTC+8)
wita_tz = timezone(timedelta(hours=8))
now = datetime.now(wita_tz)

doc_id = now.strftime("%Y-%m-%d")
current_time = now.strftime("%Y-%m-%d %H:%M:%S WITA")

# Structure Data UTUH Sesuai Schema Dashboard Vercel & Colab
data_update = {
    "iso_date": doc_id,
    "last_updated": current_time,
    "ringkasan": (
        "Pemantauan harian menunjukkan fluktuasi tingkat kerawanan karhutla "
        "di wilayah Kalimantan Timur berdasarkan indeks FDRS dan potensi hotspot."
    ),
    "rekomendasi": (
        "1. Tingkatkan patroli darat pada wilayah berstatus Sangat Rawan.\n"
        "2. Koordinasi lintas sektor BMKG, BPBD, dan Manggala Agni.\n"
        "3. Imbauan masyarakat untuk tidak melakukan pembukaan lahan dengan cara membakar."
    ),
    "tabel_wilayah": [
        {
            "kabupaten": "Paser",
            "lat": -1.88,
            "lng": 115.93,
            "ffmc": 85.2,
            "dmc": 32.1,
            "dc": 210.5,
            "fwi": 12.4,
            "hotspot": 3,
            "status": "Sangat Rawan"
        },
        {
            "kabupaten": "Kutai Barat",
            "lat": -0.23,
            "lng": 115.66,
            "ffmc": 81.0,
            "dmc": 25.4,
            "dc": 180.2,
            "fwi": 8.1,
            "hotspot": 1,
            "status": "Waspada"
        },
        {
            "kabupaten": "Kutai Kartanegara",
            "lat": -0.44,
            "lng": 116.98,
            "ffmc": 88.5,
            "dmc": 40.0,
            "dc": 250.0,
            "fwi": 18.2,
            "hotspot": 5,
            "status": "Sangat Rawan"
        },
        {
            "kabupaten": "Kutai Timur",
            "lat": 0.95,
            "lng": 117.58,
            "ffmc": 86.0,
            "dmc": 35.0,
            "dc": 220.0,
            "fwi": 15.0,
            "hotspot": 2,
            "status": "Sangat Rawan"
        },
        {
            "kabupaten": "Berau",
            "lat": 2.05,
            "lng": 117.35,
            "ffmc": 78.0,
            "dmc": 20.0,
            "dc": 150.0,
            "fwi": 5.5,
            "hotspot": 0,
            "status": "Aman"
        },
        {
            "kabupaten": "Penajam Paser Utara",
            "lat": -1.28,
            "lng": 116.66,
            "ffmc": 84.0,
            "dmc": 30.0,
            "dc": 195.0,
            "fwi": 10.2,
            "hotspot": 1,
            "status": "Waspada"
        },
        {
            "kabupaten": "Mahakam Ulu",
            "lat": 0.58,
            "lng": 114.53,
            "ffmc": 70.0,
            "dmc": 15.0,
            "dc": 110.0,
            "fwi": 2.1,
            "hotspot": 0,
            "status": "Aman"
        },
        {
            "kabupaten": "Balikpapan",
            "lat": -1.26,
            "lng": 116.83,
            "ffmc": 82.5,
            "dmc": 28.0,
            "dc": 185.0,
            "fwi": 9.0,
            "hotspot": 0,
            "status": "Waspada"
        },
        {
            "kabupaten": "Samarinda",
            "lat": -0.50,
            "lng": 117.15,
            "ffmc": 83.0,
            "dmc": 29.0,
            "dc": 190.0,
            "fwi": 9.5,
            "hotspot": 0,
            "status": "Waspada"
        },
        {
            "kabupaten": "Bontang",
            "lat": 0.13,
            "lng": 117.50,
            "ffmc": 79.0,
            "dmc": 22.0,
            "dc": 160.0,
            "fwi": 6.0,
            "hotspot": 0,
            "status": "Aman"
        }
    ]
}

# ==========================================
# 2. SIMPAN BACKUP LOKAL (data_karhutla.json)
# ==========================================
try:
    with open("data_karhutla.json", "w", encoding="utf-8") as f:
        json.dump(data_update, f, indent=4, ensure_ascii=False)
    print("💾 File data_karhutla.json lokal berhasil diperbarui!")
except Exception as e:
    print(f"⚠️ Gagal menyimpan file JSON lokal: {e}")

# ==========================================
# 3. KIRIM DATA UTUH KE FIREBASE FIRESTORE
# ==========================================
try:
    # Inisialisasi Firestore Client Anonim
    db = firestore.Client(
        project='karhutla-kaltim',
        credentials=AnonymousCredentials()
    )

    doc_ref = db.collection('history').document(doc_id)
    doc_ref.set(data_update)

    print(f"🚀 BERHASIL! Data lengkap tanggal {doc_id} sudah terkirim UTUH ke Firestore!")
    print("🔥 Dashboard Vercel siap menampilkan data live!")

except Exception as e:
    print(f"❌ Gagal mengirim data ke Firestore: {e}")
