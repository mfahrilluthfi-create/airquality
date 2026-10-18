# Air Quality Data Analysis

## Deskripsi
Proyek analisis data akhir (Dicoding, kelas *Belajar Fundamental Analisis Data*) yang menganalisis kualitas udara dari **12 stasiun pemantau di Beijing**: perbandingan **antar stasiun**, **pola musiman dan tren tahunan**, serta **hubungan kondisi cuaca (angin, hujan, arah angin) dengan PM2.5**. Sebagai analisis lanjutan, hari-hari dikelompokkan ke dalam kategori kualitas udara (manual grouping/binning, tanpa machine learning). Hasilnya ditampilkan pada dashboard Streamlit interaktif.

Alur analisis: Business Questions → Data Wrangling (Gathering, Assessing, Cleaning) → EDA → Visualization & Explanatory Analysis → Analisis Lanjutan (binning) → Conclusion & Recommendation.

## Dataset
**Air Quality Dataset** (data kualitas udara per jam, 12 stasiun di Beijing, **1 Maret 2013 – 28 Februari 2017**). Terdiri dari 12 file CSV (`PRSA_Data_<Stasiun>_20130301-20170228.csv`) di folder `data/`, masing-masing 35.064 baris per jam.

| Kelompok | Kolom |
|---|---|
| Waktu | `year`, `month`, `day`, `hour` |
| Polutan | `PM2.5`, `PM10`, `SO2`, `NO2`, `CO`, `O3` |
| Cuaca | `TEMP`, `PRES`, `DEWP`, `RAIN`, `wd` (arah angin), `WSPM` (kecepatan angin, m/s) |
| Lokasi | `station` |

**Satuan analisis:** rata-rata PM2.5 **harian** per stasiun, hanya untuk hari dengan minimal 18 jam PM2.5 valid (17.164 hari-stasiun valid dari 17.532).

**Acuan di luar dataset:** batas harian 75 µg/m³ dan batas tahunan 35 µg/m³ PM2.5 (Standar Kualitas Udara Ambien China GB 3095-2012, Grade II), serta batas kategori kualitas udara harian dari skema HJ 633-2012.

## Business Questions
1. **Perbandingan Kualitas Udara Antar Stasiun:** Stasiun pemantau mana yang memiliki rata-rata PM2.5 harian tertinggi dan terendah di antara 12 stasiun selama 1 Maret 2013 – 28 Februari 2017, berapa selisihnya, dan berapa persen hari yang melampaui batas harian 75 µg/m³ di setiap stasiun?
2. **Pola Musiman dan Tren Tahunan PM2.5:** Bagaimana pola bulanan dan musiman rata-rata PM2.5 harian, bulan dan musim mana yang terburuk, dan bagaimana perubahan rata-rata antar periode tahunan (Maret–Februari)?
3. **Pengaruh Kondisi Cuaca (Angin, Hujan, Arah Angin) terhadap PM2.5:** Bagaimana hubungan kecepatan angin, hujan, dan arah angin dengan PM2.5 harian, dan berapa persen lebih rendah PM2.5 pada hari berangin (> 3 m/s) dibanding hari tenang (<= 1 m/s)?

## Insight Utama
- **BQ1:** rata-rata PM2.5 harian tertinggi pada **Dongsi** (85,94 µg/m³) dan terendah pada **Dingling** (65,75 µg/m³), selisih 20,20 µg/m³. Stasiun terbagi dua kelompok: 9 stasiun pada 79,1–85,9 µg/m³ dan 3 stasiun yang lebih bersih (Changping, Huairou, Dingling). Peringkat stasiun teratas tidak robust (berganti pada uji sensitivitas), dan seluruh stasiun melampaui batas tahunan 35 µg/m³.
- **BQ2:** bulan terburuk **Des** (104,5 µg/m³), terbaik **Agu** (53,4); Winter 94,6 vs Summer 64,6 µg/m³. Rata-rata antarperiode 85,9 → 81,3 → 73,0 → 78,1 µg/m³; kenaikan periode terakhir hampir seluruhnya dari musim dingin.
- **BQ3:** PM2.5 **76,0%** lebih rendah pada hari berangin (> 3 m/s) dibanding hari tenang (30,1 vs 125,7 µg/m³). Pengaruh hujan tidak konsisten antarmusim; seluruhnya adalah asosiasi.
- **Analisis lanjutan:** hanya 29,6% hari-stasiun berkategori Excellent dan 12,5% Heavily/Severely Polluted; proporsi hari berat mencapai 20,6% pada Winter dan 33,3% pada hari tenang.
- **Kualitas data:** waktu tidak tersedia sebagai kolom datetime; missing value dengan celah hingga 343 jam; PM2.5 > PM10 pada 5,18% baris; arah angin hilang; sebagian hari tidak lengkap. Seluruhnya ditangani pada notebook tanpa imputasi.

## Struktur Project
```
submission/
├── dashboard/
│   ├── main_data.csv      # data bersih harian per stasiun (hasil notebook)
│   └── dashboard.py       # aplikasi Streamlit
├── data/
│   └── PRSA_Data_*.csv    # 12 file stasiun
├── notebook.ipynb         # proses analisis data lengkap
├── README.md
├── requirements.txt
└── url.txt                # URL dashboard yang sudah di-deploy
```

## Persyaratan
- Python 3.10 atau lebih baru (diuji pada Python 3.12 dengan pandas 2.3 dan pandas 3.0)
- pip (package manager Python)
- Library (lihat `requirements.txt`): NumPy, Pandas, Matplotlib, Seaborn (notebook), Streamlit, Plotly (dashboard)

## Setup Environment
Disarankan memakai virtual environment agar library proyek ini tidak bercampur dengan proyek lain.

1. Buka terminal (Command Prompt/PowerShell di Windows, Terminal di macOS/Linux) lalu masuk ke folder proyek:
   ```
   cd submission
   ```
2. Buat virtual environment:
   ```
   python -m venv .venv
   ```
3. Aktifkan virtual environment:
   - Windows:
     ```
     .venv\Scripts\activate
     ```
   - macOS/Linux:
     ```
     source .venv/bin/activate
     ```
   Jika berhasil, tulisan `(.venv)` muncul di awal baris terminal.

## Instalasi Dependency
Dengan virtual environment aktif dan berada di folder `submission/`:
```
pip install -r requirements.txt
```

## Menjalankan Dashboard
Masuk ke folder dashboard lalu jalankan Streamlit:
```
cd dashboard
streamlit run dashboard.py
```
Browser akan terbuka otomatis. Jika tidak, buka alamat yang tampil di terminal (biasanya `http://localhost:8501`). Untuk menghentikan dashboard, tekan `Ctrl+C`.

Alternatif dari folder `submission/` (tanpa `cd dashboard`):
```
streamlit run dashboard/dashboard.py
```

## Menjalankan Notebook (opsional)
Jalankan dari folder `submission/` agar folder `data/` terbaca:
```
pip install jupyter
jupyter notebook notebook.ipynb
```
Lalu pilih *Restart & Run All*. Di Google Colab, unggah ke-12 file CSV ke folder `data/` (atau ke direktori yang sama dengan notebook) sebelum menjalankan sel.

## Dashboard Online
URL deployment tercantum di `url.txt` (https://airquality-6ppvmmka7sauxau7garvd8.streamlit.app/).

## Fitur Dashboard
**Visualisasi untuk tiga Business Questions**
- **BQ1 (tab "BQ1: Antar Stasiun"):** grafik batang rata-rata PM2.5 harian per stasiun dan persentase hari di atas batas PM2.5.
- **BQ2 (tab "BQ2: Musim & Tren"):** rata-rata PM2.5 menurut bulan (berwarna per musim) dan menurut periode tahunan Maret–Februari.
- **BQ3 (tab "BQ3: Cuaca"):** PM2.5 menurut kecepatan angin, hari hujan vs tanpa hujan per musim, dan arah angin dominan harian.

**Visualisasi pendukung:** tab "Kategori Kualitas Udara" menampilkan distribusi kategori (Excellent sampai Severely Polluted) keseluruhan dan per musim (hasil analisis lanjutan).

**Fitur interaktif (sidebar)**
- **Periode tanggal** (pemilih rentang tanggal)
- **Stasiun** (pilihan ganda)
- **Musim** (pilihan ganda)
- **Batas PM2.5 harian** (slider 35–150 µg/m³; nilai awal 75 sesuai notebook)

Perubahan filter langsung memperbarui KPI (jumlah hari-stasiun, rata-rata PM2.5, persentase hari di atas batas, persentase hari Heavily/Severely Polluted), seluruh grafik, dan teks insight. Jika kombinasi filter tidak menghasilkan data, dashboard menampilkan peringatan tanpa error.

**Catatan metodologi dashboard:** `main_data.csv` berisi satu baris per stasiun per hari valid (rata-rata PM2.5 harian dengan minimal 18 jam data). Tanpa filter, seluruh angka pada dashboard identik dengan notebook.

## Author
M Fahril Luthfi — Sistem Informasi, Universitas Islam Negeri Sultan Syarif Kasim Riau
