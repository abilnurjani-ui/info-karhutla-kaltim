from datetime import datetime
import json
import os
import firebase_admin
from firebase_admin import credentials, firestore
import requests

# ==========================================
# 1. PERSIAPAN DATA & TANGGAL
# ==========================================
print("🔍 Memulai proses update data Karhutla...")

# Mengambil tanggal dan waktu saat ini
today_date = datetime.now().strftime("%Y-%m-%d")
current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S WITA")

# [SESUAIKAN] Data hasil scraping/pemantauan Anda
# Masukkan atau gabungkan dengan data scraping asli Anda di sini
today_data = {
    "last_updated": current_time,
    "date": today_date,
    "status": "Active Monitoring",
    "region": "Kalimantan Timur",
    # Tambahkan field/data hotspot Anda di sini jika ada
}

# ==========================================
# 2. SIMPAN KE FILE LOKAL (data_karhutla.json)
# ==========================================
try:
    with open("data_karhutla.json", "w", encoding="utf-8") as f:
        json.dump(today_data, f, indent=4, ensure_ascii=False)
    print("💾 File data_karhutla.json berhasil diperbarui secara lokal!")
except Exception as e:
    print(f"⚠️ Gagal menyimpan file JSON lokal: {e}")

# ==========================================
# 3. KIRIM DATA KE FIREBASE FIRESTORE
# ==========================================
firebase_secret = os.environ.get("FIREBASE_SERVICE_ACCOUNT")

if firebase_secret:
    try:
        # Load string JSON dari Environment Variable GitHub
        cred_dict = json.loads(firebase_secret)
        cred = credentials.Certificate(cred_dict)

        # Inisialisasi Firebase (jika belum)
        if not firebase_admin._apps:
            firebase_admin.initialize_app(cred)

        db = firestore.client()
        print("⚡ Berhasil terhubung ke Firebase Firestore!")

        # Simpan ke Firestore (Koleksi: 'history', Dokumen berdasarkan Tanggal)
        doc_ref = db.collection("history").document(today_date)
        doc_ref.set(today_data, merge=True)

        print(f"✅ Data tanggal {today_date} BERHASIL dikirim ke Firestore!")

    except Exception as e:
        print(f"❌ Gagal mengirim data ke Firebase: {e}")
else:
    print(
        "⚠️ Warning: Environment variable FIREBASE_SERVICE_ACCOUNT tidak"
        " ditemukan!"
    )
