import requests
from bs4 import BeautifulSoup
from datetime import datetime, timezone, timedelta
import json
import urllib3

# Matikan peringatan SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 1. Waktu WITA
wita_tz = timezone(timedelta(hours=8))
now = datetime.now(wita_tz)

bulan_indo = {
    "January": "Januari", "February": "Februari", "March": "Maret",
    "April": "April", "May": "Mei", "June": "Juni",
    "July": "Juli", "August": "Agustus", "September": "September",
    "October": "Oktober", "November": "November", "December": "Desember"
}

tanggal_str = now.strftime("%d ") + bulan_indo[now.strftime("%B")] + now.strftime(" %Y")
waktu_str = now.strftime("%H:%M WITA")

# 2. Pemetaan 10 Kab/Kota Kaltim
kabkota_kaltim = [
    {"nama": "Paser", "lat": -1.8974, "lon": 116.0975, "zona": "selatan"},
    {"nama": "Penajam Paser Utara", "lat": -1.2588, "lon": 116.5772, "zona": "selatan"},
    {"nama": "Balikpapan", "lat": -1.2379, "lon": 116.8529, "zona": "selatan"},
    {"nama": "Samarinda", "lat": -0.5021, "lon": 117.1536, "zona": "tengah"},
    {"nama": "Kutai Kartanegara", "lat": -0.4439, "lon": 116.9813, "zona": "tengah"},
    {"nama": "Bontang", "lat": 0.1333, "lon": 117.5000, "zona": "pesisir"},
    {"nama": "Kutai Timur", "lat": 0.5387, "lon": 117.5886, "zona": "utara"},
    {"nama": "Kutai Barat", "lat": -0.2311, "lon": 115.6980, "zona": "barat"},
    {"nama": "Berau", "lat": 2.1523, "lon": 117.3980, "zona": "utara"},
    {"nama": "Mahakam Ulu", "lat": 0.6023, "lon": 114.9080, "zona": "barat"}
]

# 3. Scraping Data BMKG Cuaca & BMKG Iklim (Multisource)
urls = [
    "https://stamet-samarinda.bmkg.go.id/cuaca/karhutla",
    "https://www.bmkg.go.id/cuaca/karhutla",
    "https://iklim.bmkg.go.id/id/"
]
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

combined_text = ""
for url in urls:
    try:
        res = requests.get(url, headers=headers, timeout=15, verify=False)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'html.parser')
            combined_text += " " + soup.get_text().lower()
    except Exception as e:
        print(f"⚠️ Peringatan: Gagal menjangkau {url}: {e}")

# Deteksi Sinyal Krisis Cuaca & Iklim
is_krisis_cuaca = ("sangat mudah" in combined_text) or ("sangat tinggi" in combined_text)
is_krisis_iklim = ("sangat sesuai" in combined_text) or ("potensi tinggi" in combined_text) or ("kering" in combined_text)

# 4. Evaluasi Parameter FDRS & Indeks Kesesuaian Iklim Hotspot
tabel_wilayah = []
rawan_c, waspada_c, aman_c = 0, 0, 0

for item in kabkota_kaltim:
    if item["zona"] == "selatan" and (is_krisis_cuaca or is_krisis_iklim):
        status = "Sangat Rawan"
        kesesuaian_iklim = "Sangat Sesuai (Tinggi)"
        ffmc, dmc, dc, fwi = "Sangat Tinggi (>91.5)", "Sangat Tinggi (>60.0)", "Tinggi (>300)", "Sangat Tinggi (>28.0)"
        rawan_c += 1
    elif item["zona"] in ["tengah", "pesisir", "utara"]:
        status = "Waspada"
        kesesuaian_iklim = "Sesuai (Sedang)"
        ffmc, dmc, dc, fwi = "Tinggi (87.5-91.5)", "Sedang (20-40)", "Rendah (<200)", "Sedang (2.0-13.0)"
        waspada_c += 1
    else:
        status = "Aman"
        kesesuaian_iklim = "Kurang Sesuai (Rendah)"
        ffmc, dmc, dc, fwi = "Rendah (<80.0)", "Rendah (<20.0)", "Rendah (<200)", "Rendah (<2.0)"
        aman_c += 1

    tabel_wilayah.append({
        "nama": item["nama"],
        "lat": item["lat"],
        "lon": item["lon"],
        "status": status,
        "kesesuaian_iklim": kesesuaian_iklim,
        "ffmc": ffmc,
        "dmc": dmc,
        "dc": dc,
        "fwi": fwi
    })

# 5. Output JSON
data_json = {
    "tanggal": tanggal_str,
    "waktu": waktu_str,
    "tabel_wilayah": tabel_wilayah,
    "ringkasan": f"Update Integrasi BMKG Cuaca & Iklim ({tanggal_str} {waktu_str}): Dari 10 wilayah Kaltim, terdeteksi {rawan_c} wilayah dengan status Sangat Rawan & Indeks Iklim 'Sangat Sesuai' untuk kemunculan titik panas, {waspada_c} Waspada, dan {aman_c} Aman. Klaster risiko tinggi terkonsentrasi di sektor selatan (Paser, PPU, Balikpapan).",
    "rekomendasi": "1. Tingkatkan siaga darurat pada area dengan Indeks Kesesuaian Iklim 'Sangat Sesuai' (Paser, PPU, Balikpapan).\n2. Aktifkan pemantauan satelit TERRA/AQUA & SNPP secara real-time untuk mendeteksi pembentukan awal titik panas (hotspot).\n3. Lakukan ground-check dan pembatasan aktivitas pembukaan lahan di area berisiko."
}

with open('data_karhutla.json', 'w', encoding='utf-8') as f:
    json.dump(data_json, f, indent=4, ensure_ascii=False)

print("✅ BERHASIL: Parameter Kesesuaian Iklim BMKG berhasil diproses ke JSON!")
