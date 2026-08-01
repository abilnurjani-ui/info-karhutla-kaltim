import json
import os
import firebase_admin
from firebase_admin import credentials, firestore

# 1. Inisialisasi Firebase menggunakan Secret dari GitHub
firebase_secret = os.environ.get("FIREBASE_SERVICE_ACCOUNT")

if firebase_secret:
    try:
        # Load string JSON dari Environment Variable
        cred_dict = json.loads(firebase_secret)
        cred = credentials.Certificate(cred_dict)
        
        # Cek agar tidak inisialisasi ganda
        if not firebase_admin._apps:
            firebase_admin.initialize_app(cred)
            
        db = firestore.client()
        print("⚡ Berhasil terhubung ke Firebase Firestore!")
        
        # 2. Simpan data hari ini ke Firestore (Koleksi: 'history', Dokumen: 'YYYY-MM-DD')
        # Asumsi 'today_date' berformat '2026-08-01' dan 'today_data' adalah dictionary data
        doc_ref = db.collection('history').document(today_date)
        doc_ref.set(today_data, merge=True)
        print(f"✅ Data tanggal {today_date} berhasil dikirim ke Firebase!")
        
    except Exception as e:
        print(f"❌ Gagal mengirim data ke Firebase: {e}")
else:
    print("⚠️ Warning: Secret FIREBASE_SERVICE_ACCOUNT tidak ditemukan!")
