# 🏠 IniKos — Prediksi Harga Sewa Kos Madiun

Aplikasi web berbasis **Django** dan **Machine Learning** untuk memprediksi estimasi harga sewa bulanan rumah kos di wilayah **Madiun** berdasarkan spesifikasi fasilitas, luas kamar, dan lokasi.

---

## ✨ Fitur Utama

* **Kalkulator Prediksi Harga Kos:** Estimasi otomatis harga sewa bulanan menggunakan model regresi Scikit-learn (`LinearRegression` & `DecisionTreeRegressor`) yang dilatih dari dataset lokal (`kos_madiun.csv`).
* **Visualisasi & Grafik Analisis:** Tampilan grafik perbandingan harga kos dan faktor fasilitas yang memengaruhi tarif sewa.
* **AI Cost Explanation:** Penjelasan otomatis terkait kewajaran harga prediksi menggunakan integrasi API **Gemini** / **Groq** (dengan *fallback* lokal).
* **Riwayat Prediksi:** Penyimpanan otomatis hasil kalkulasi pengguna ke dalam database SQLite melalui model `RiwayatPrediksi`.
* **Antarmuka Modern:** Desain responsif bertema *Powder Blue Elegant*.

---

## 📂 Struktur Proyek

```text
IniKos/
├── hitungkos_project/     # Konfigurasi utama proyek Django (settings, urls, wsgi)
├── prediksi/              # Aplikasi utama (views, models, forms, logika prediksi & AI)
├── static/images/         # Aset gambar statis
├── templates/             # File antarmuka HTML
├── db.sqlite3             # Database lokal SQLite
├── kos_madiun.csv         # Dataset harga dan fasilitas kos di Madiun
├── manage.py              # CLI manajemen proyek Django
├── model_kos.joblib       # Model Machine Learning terlatih
└── train_model.py         # Script pelatihan & evaluasi model ML
```

---

## 🛠️ Teknologi yang Digunakan

* **Backend:** Python, Django
* **Machine Learning:** Scikit-learn, Pandas, Joblib
* **AI Integration:** Google Gemini API / Groq API
* **Frontend:** HTML5, CSS3, JavaScript
* **Database:** SQLite3

---

## 🚀 Cara Menjalankan Proyek

### 1. Clone Repository
```bash
git clone [https://github.com/gavinadhif/IniKos.git](https://github.com/gavinadhif/IniKos.git)
cd IniKos
```

### 2. Buat & Aktifkan Virtual Environment
* **Windows:**
  ```bash
  python -m venv venv
  venv\Scripts\activate
  ```
* **Mac / Linux:**
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```

### 3. Install Dependensi
```bash
pip install django scikit-learn pandas joblib python-dotenv google-genai groq
```

### 4. Konfigurasi Environment Variable (Opsional untuk Fitur AI)
Buat file `.env` di folder root (sejajar dengan `manage.py`), lalu isi API key Anda:
```env
GEMINI_API_KEY=masukkan_api_key_gemini_anda
GROQ_API_KEY=masukkan_api_key_groq_anda
```

### 5. Latih Ulang Model (Opsional)
Model sudah tersedia pada `model_kos.joblib`. Jika ingin melatih ulang dari `kos_madiun.csv`:
```bash
python train_model.py
```

### 6. Migrasi Database & Jalankan Server
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```

Buka browser dan akses **`http://127.0.0.1:8000/`**.

---

## 👨‍💻 Pengembang

* **Naufal Gavin Nadhif Annafi** (`253307050`) — [@gavinadhif](https://github.com/gavinadhif)
