# Pemetaan BAB IV dengan sistem

## 4.1 Analisis Sistem
### 4.1.1 Analisis Masalah
Masalah pengelolaan penjualan dan persediaan, kebutuhan informasi manajemen, serta kebutuhan estimasi penjualan bulan berikutnya.

### 4.1.2 Analisis Kebutuhan Sistem
#### 4.1.2.1 Analisis Data
Masukan: periode, produk, kategori, harga, stok, terjual. Keluaran: KPI, grafik, tabel analisis, hasil prediksi, metrik model, dan indikator pendukung persediaan.

#### 4.1.2.2 Analisis Proses
Login → pengambilan data MySQL → preprocessing → pembentukan Lag 1–3 → training/testing → Random Forest → evaluasi → prediksi → penyimpanan/visualisasi → informasi pendukung keputusan.

#### 4.1.2.3 Analisis Pengguna
Admin dan Manajemen.

#### 4.1.2.4 Analisis Hardware
Komputer/laptop pengembangan dan server lokal MySQL/XAMPP sesuai kebutuhan penelitian.

#### 4.1.2.5 Analisis Software
Python, Streamlit, MySQL, phpMyAdmin, Pandas, NumPy, Plotly, Scikit-learn, bcrypt, dan python-dotenv.

#### 4.1.2.6 Analisis Konfigurasi Sistem
Konfigurasi Python environment, koneksi MySQL melalui `.env`, dan konfigurasi aplikasi Streamlit.

## 4.2 Perancangan Sistem (Perangkat Lunak)
### 4.2.1 Use Case Diagram
Aktor: Admin dan Manajemen. Fitur: login, dashboard, analisis, prediksi, perencanaan persediaan, produk, data penjualan, profil, dan fungsi administrasi Admin.

### 4.2.2 Activity Diagram
Login, reset password, analisis penjualan, proses prediksi, penyimpanan prediksi, dan pengelolaan pengguna.

### 4.2.3 Sequence Diagram
Interaksi pengguna dengan Streamlit, modul database, dan modul Random Forest.

### 4.2.4 Class Diagram
Entitas utama: User, Produk, Penjualan, Prediksi, LogAktivitas; serta modul service untuk autentikasi, database, dan model.

### 4.2.5 Desain Database
Lima tabel: `tb_user`, `tb_produk`, `tb_penjualan`, `tb_prediksi`, `tb_log_aktivitas`.

### 4.2.6 Desain Antarmuka
Login, Dashboard, Analisis Penjualan, Prediksi Random Forest, Perencanaan Persediaan, Produk, Data Penjualan, Profil, Manajemen Pengguna, dan Aktivitas Pengguna.
