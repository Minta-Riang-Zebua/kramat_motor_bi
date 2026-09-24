# Kramat Motor BI — Skripsi Teknik Informatika

**Judul:** Rancang Bangun Dashboard Business Intelligence untuk Prediksi Penjualan Aksesoris Mobil Berbasis Machine Learning Random Forest di PT Kramat Motor

## 1. Teknologi
- Python + Streamlit
- MySQL / phpMyAdmin
- Pandas + NumPy
- Plotly
- Scikit-learn Random Forest Regression
- bcrypt untuk hashing password
- python-dotenv untuk konfigurasi koneksi

## 2. Struktur project
```text
kramat_motor_bi/
├── app.py
├── database.py
├── ml_model.py                 # compatibility wrapper
├── ui.py
├── requirements.txt
├── .env.example
├── data_penjualan.csv
├── model/
│   ├── __init__.py
│   └── random_forest.py        # inti model Random Forest
├── sql/
│   └── schema_and_seed.sql
├── assets/
│   └── README.md
├── ERD.md
├── CHAPTER_IV_OUTLINE.md
└── README.md
```

## 3. Database
Lima tabel utama:
- `tb_user` — akun dan hak akses Admin/Manajemen
- `tb_produk` — master produk
- `tb_penjualan` — data penjualan bulanan
- `tb_prediksi` — hasil prediksi Random Forest
- `tb_log_aktivitas` — audit aktivitas pengguna

Aplikasi mencoba membuat database/tabel otomatis ketika MySQL dapat diakses. File `sql/schema_and_seed.sql` tetap disediakan agar database dapat di-import melalui phpMyAdmin.

## 4. Hak akses
### Admin
- Dashboard
- Analisis penjualan
- Prediksi Random Forest
- Perencanaan persediaan
- Produk
- Data penjualan
- Manajemen pengguna
- Aktivitas pengguna
- Profil dan perubahan password

### Manajemen
- Dashboard
- Analisis penjualan
- Prediksi Random Forest
- Perencanaan persediaan
- Produk
- Data penjualan
- Profil dan perubahan password

## 5. Login dan reset password
Akun awal:
- Admin: `admin` / `Admin@12345`
- Manajemen: `manager` / `Manager@12345`

Password disimpan dalam bentuk hash bcrypt.

Pada halaman login tersedia **Lupa Password**. Pengguna dapat melakukan reset mandiri dengan mencocokkan username dan email terdaftar, kemudian membuat password baru. Fitur ini disediakan untuk kebutuhan aplikasi lokal/skripsi; untuk deployment produksi, verifikasi email/OTP sebaiknya ditambahkan.

## 6. Model Random Forest
Fitur:
- Harga
- Stok
- Bulan
- Tahun
- Lag 1
- Lag 2
- Lag 3

Target:
- `Terjual`

Pembagian evaluasi berdasarkan waktu:
- Training: Januari–Desember 2025
- Testing: Januari–Juni 2026

Metrik:
- MAE
- RMSE
- R²

Lag dibuat per produk. Tiga periode awal setiap produk tidak memiliki Lag 3 lengkap sehingga tidak digunakan sebagai observasi training/testing, tetapi data asli tetap tersimpan.

## 7. Tujuan informasi prediksi
Prediksi digunakan sebagai **informasi pendukung perencanaan persediaan**. Halaman Perencanaan Persediaan membandingkan prediksi penjualan bulan berikutnya dengan stok terakhir untuk memberi indikasi produk yang perlu mendapat perhatian. Sistem tidak menetapkan jumlah pembelian atau reorder point secara otomatis.

## 8. Instalasi
1. Pastikan MySQL/XAMPP aktif.
2. Salin `.env.example` menjadi `.env` dan sesuaikan koneksi MySQL.
3. Install dependency:
   ```bash
   pip install -r requirements.txt
   ```
4. Jalankan:
   ```bash
   streamlit run app.py
   ```
5. Buka alamat yang diberikan Streamlit, biasanya `http://localhost:8501`.
6. Jika database belum ada, aplikasi akan mencoba membuat database dan tabel secara otomatis. Alternatifnya, import `sql/schema_and_seed.sql` melalui phpMyAdmin.

## 9. BAB IV — Analisis dan Perancangan
Project diselaraskan dengan pedoman:

**4.1 Analisis Sistem**
- 4.1.1 Analisis Masalah
- 4.1.2 Analisis Kebutuhan Sistem
  - 4.1.2.1 Analisis Data (Masukan dan Keluaran)
  - 4.1.2.2 Analisis Proses
  - 4.1.2.3 Analisis Pengguna
  - 4.1.2.4 Analisis Hardware
  - 4.1.2.5 Analisis Software
  - 4.1.2.6 Analisis Konfigurasi Sistem

**4.2 Perancangan Sistem (Perangkat Lunak)**
- 4.2.1 Use Case Diagram
- 4.2.2 Activity Diagram
- 4.2.3 Sequence Diagram
- 4.2.4 Class Diagram
- 4.2.5 Desain Database
- 4.2.6 Desain Antarmuka

Bagian Multimedia, Sistem Kendali, dan Jaringan tidak menjadi fokus karena penelitian ini merupakan aplikasi perangkat lunak Business Intelligence berbasis web.
