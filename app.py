import io
import math
import os
import bcrypt
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from database import (
    ensure_database_schema, query_df, execute, load_sales, log_activity, database_health,
)
from ml_model import train_evaluate, fit_full, next_month_forecast, FEATURES
from ui import setup, hero, kpi, section

st.set_page_config(
    page_title='Kramat Motor BI',
    page_icon='📊',
    layout='wide',
    initial_sidebar_state='expanded',
)
setup()

ROLE_LABEL = {'admin': 'Admin', 'manajemen': 'Manajemen'}
PAGE_GROUPS = {
    'Utama': ['Dashboard', 'Analisis Penjualan'],
    'Prediksi & Persediaan': ['Prediksi Random Forest', 'Perencanaan Persediaan'],
    'Data': ['Produk', 'Data Penjualan'],
}

if 'user' not in st.session_state:
    st.session_state.user = None
if 'db_ready' not in st.session_state:
    st.session_state.db_ready = False
if 'login_message' not in st.session_state:
    st.session_state.login_message = None


def money(x):
    return f"Rp {float(x):,.0f}".replace(',', '.')


def number(x):
    return f"{float(x):,.0f}".replace(',', '.')


def percent(x):
    return f"{float(x):.1f}%"


def parse_period(value):
    from model.random_forest import parse_indonesian_period
    return parse_indonesian_period(value)


def password_valid(password):
    return (
        len(password) >= 8
        and any(c.isupper() for c in password)
        and any(c.islower() for c in password)
        and any(c.isdigit() for c in password)
    )


def check_login(username, password):
    row = query_df(
        'SELECT id_user, username, password_hash, nama, email, role FROM tb_user WHERE username=%s AND status="aktif"',
        (username,),
    )
    if row.empty:
        return None
    try:
        valid = bcrypt.checkpw(password.encode(), row.iloc[0]['password_hash'].encode())
    except Exception:
        valid = False
    return row.iloc[0].to_dict() if valid else None


def login_page():
    # Auto-initialize the local MySQL schema so the first run does not fail with
    # "table tb_user doesn't exist" after a fresh XAMPP/phpMyAdmin setup.
    if not st.session_state.db_ready:
        try:
            ok, msg = ensure_database_schema()
            st.session_state.db_ready = ok
            if ok:
                st.session_state.login_message = msg
        except Exception as exc:
            st.session_state.login_message = str(exc)

    st.markdown('<div class="login-shell"><div class="login-card">', unsafe_allow_html=True)
    st.markdown('<div class="login-brand"><div class="mark">PT KRAMAT MOTOR</div><h1>Business Intelligence</h1><p>Dashboard Analisis & Prediksi Penjualan</p></div>', unsafe_allow_html=True)

    if st.session_state.db_ready:
        st.success('Database siap digunakan.', icon='✅')
    else:
        st.error('Database belum siap. Pastikan MySQL/XAMPP aktif.', icon='⚠️')
        st.caption('Jika database baru dibuat, klik tombol di bawah untuk membuat tabel dan data awal.')
        if st.button('Inisialisasi Database', use_container_width=True):
            try:
                ok, msg = ensure_database_schema()
                st.session_state.db_ready = ok
                st.session_state.login_message = msg
                st.rerun()
            except Exception as exc:
                st.error(f'Inisialisasi gagal: {exc}')

    tab_login, tab_reset = st.tabs(['Masuk', 'Lupa Password'])
    with tab_login:
        with st.form('login_form'):
            username = st.text_input('Username', placeholder='Masukkan username')
            password = st.text_input('Password', type='password', placeholder='Masukkan password')
            submitted = st.form_submit_button('Masuk ke Dashboard', use_container_width=True, type='primary')
        if submitted:
            if not st.session_state.db_ready:
                st.error('Database belum siap. Inisialisasi database terlebih dahulu.')
            elif not username.strip() or not password:
                st.warning('Username dan password wajib diisi.')
            else:
                try:
                    user = check_login(username.strip(), password)
                    if user:
                        st.session_state.user = user
                        log_activity(user['id_user'], 'Login ke sistem')
                        st.rerun()
                    else:
                        st.error('Username atau password tidak sesuai / akun tidak aktif.')
                except Exception as exc:
                    st.error(f'Koneksi database gagal: {exc}')
        with st.expander('Akun demo untuk pengujian'):
            st.caption('Admin: admin / Admin@12345')
            st.caption('Manajemen: manager / Manager@12345')
            st.caption('Ganti password setelah berhasil masuk.')

    with tab_reset:
        st.caption('Reset mandiri menggunakan username dan email yang terdaftar pada akun.')
        with st.form('forgot_password_form'):
            username = st.text_input('Username akun', key='reset_username')
            email = st.text_input('Email terdaftar', key='reset_email')
            new_password = st.text_input('Password baru', type='password', key='reset_new')
            confirm = st.text_input('Konfirmasi password baru', type='password', key='reset_confirm')
            reset = st.form_submit_button('Reset Password', use_container_width=True)
        if reset:
            if not username.strip() or not email.strip() or not new_password or not confirm:
                st.warning('Semua field wajib diisi.')
            elif new_password != confirm:
                st.error('Konfirmasi password tidak sama.')
            elif not password_valid(new_password):
                st.error('Password minimal 8 karakter dan harus mengandung huruf besar, huruf kecil, serta angka.')
            else:
                try:
                    rows = query_df('SELECT id_user FROM tb_user WHERE username=%s AND LOWER(email)=LOWER(%s) AND status="aktif"', (username.strip(), email.strip()))
                    if rows.empty:
                        st.error('Username dan email tidak cocok dengan akun aktif.')
                    else:
                        uid = int(rows.iloc[0]['id_user'])
                        hashed = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt()).decode()
                        execute('UPDATE tb_user SET password_hash=%s, updated_at=CURRENT_TIMESTAMP WHERE id_user=%s', (hashed, uid))
                        log_activity(uid, 'Reset password mandiri melalui halaman login')
                        st.success('Password berhasil direset. Silakan masuk menggunakan password baru.')
                except Exception as exc:
                    st.error(f'Gagal mereset password: {exc}')

    st.markdown('</div><div class="footer">PT Kramat Motor • Teknik Informatika • Business Intelligence & Machine Learning</div></div>', unsafe_allow_html=True)


if st.session_state.user is None:
    login_page()
    st.stop()

user = st.session_state.user


def sidebar():
    st.sidebar.markdown('<div class="brand"><div class="brand-mark">PT Kramat Motor</div><h1>Business Intelligence</h1><p>Analisis Penjualan & Prediksi</p></div>', unsafe_allow_html=True)
    st.sidebar.markdown(
        f'<div class="user-card"><div class="name">{user["nama"]}</div><div class="role">Role: {ROLE_LABEL.get(user["role"], user["role"])}</div></div>',
        unsafe_allow_html=True,
    )
    allowed = []
    for group, pages in PAGE_GROUPS.items():
        with st.sidebar.expander(group, expanded=True):
            for item in pages:
                allowed.append(item)
    if user['role'] == 'admin':
        with st.sidebar.expander('Administrasi', expanded=True):
            allowed += ['Manajemen Pengguna', 'Aktivitas Pengguna']
    with st.sidebar.expander('Akun', expanded=True):
        allowed.append('Profil')
    page = st.sidebar.radio('Halaman', allowed, label_visibility='collapsed')
    st.sidebar.divider()
    if st.sidebar.button('Keluar', use_container_width=True):
        log_activity(user['id_user'], 'Logout dari sistem')
        st.session_state.user = None
        st.rerun()
    return page


page = sidebar()

try:
    df = load_sales()
except Exception as exc:
    st.error('Data belum dapat dimuat dari MySQL.')
    st.code(str(exc))
    st.info('Pastikan MySQL/XAMPP aktif dan database kramat_motor_bi sudah dibuat. Gunakan tombol Inisialisasi Database pada halaman login jika diperlukan.')
    st.stop()

if df.empty:
    st.warning('Belum ada data penjualan pada database.')
    st.stop()

df['periode_date'] = pd.to_datetime(df['periode_date'], errors='coerce')
df['NilaiPenjualan'] = df['Harga'] * df['Terjual']


@st.cache_data(ttl=600, show_spinner=False)
def cached_model_bundle(data):
    return train_evaluate(data)


@st.cache_data(ttl=600, show_spinner=False)
def cached_forecast_bundle(data):
    model, _ = fit_full(data)
    forecast, target_date = next_month_forecast(data, model=model)
    return model, forecast, target_date


def get_model_bundle():
    return cached_model_bundle(df)


def get_forecast_bundle():
    return cached_forecast_bundle(df)


if page == 'Dashboard':
    hero('Dashboard Business Intelligence', 'Ringkasan kondisi penjualan, nilai transaksi, produk, dan informasi prediktif untuk mendukung perencanaan persediaan.')
    latest = df['periode_date'].max()
    previous = sorted(df['periode_date'].dropna().unique())[-2] if df['periode_date'].nunique() > 1 else latest
    latest_sales = df.loc[df['periode_date'].eq(latest), 'Terjual'].sum()
    previous_sales = df.loc[df['periode_date'].eq(previous), 'Terjual'].sum()
    growth = ((latest_sales - previous_sales) / previous_sales * 100) if previous_sales else 0

    c1,c2,c3,c4 = st.columns(4)
    with c1: kpi('Total Produk', number(df['Produk'].nunique()), 'Produk pada sumber data')
    with c2: kpi('Unit Terjual', number(df['Terjual'].sum()), 'Akumulasi seluruh periode')
    with c3: kpi('Nilai Penjualan', money(df['NilaiPenjualan'].sum()), 'Harga × unit terjual')
    with c4: kpi('Penjualan Periode Terakhir', number(latest_sales), latest.strftime('%B %Y'))

    section('Ringkasan Periode Terakhir', 'Perbandingan unit terjual pada periode terakhir terhadap periode sebelumnya.')
    a,b,c = st.columns(3)
    with a: kpi('Periode', latest.strftime('%B %Y'), 'Data aktual terakhir')
    with b: kpi('Pertumbuhan Unit', percent(growth), 'Dibanding periode sebelumnya')
    with c: kpi('Rata-rata Unit/Produk', number(df.loc[df['periode_date'].eq(latest), 'Terjual'].mean()), 'Pada periode terakhir')

    trend = df.groupby('periode_date', as_index=False).agg(Terjual=('Terjual','sum'), Nilai=('NilaiPenjualan','sum'))
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=trend['periode_date'], y=trend['Terjual'], mode='lines+markers', name='Unit Terjual', line=dict(width=3)))
    fig.update_layout(template='plotly_white', height=360, margin=dict(l=10,r=10,t=20,b=10), xaxis_title='', yaxis_title='Unit')
    section('Tren Penjualan', 'Pergerakan total unit terjual setiap bulan.')
    st.plotly_chart(fig, use_container_width=True, config={'displaylogo':False})

    a,b = st.columns(2)
    with a:
        top = df.groupby('Produk', as_index=False)['Terjual'].sum().sort_values('Terjual', ascending=False).head(10).sort_values('Terjual')
        fig = px.bar(top, x='Terjual', y='Produk', orientation='h', template='plotly_white', title='10 Produk dengan Penjualan Tertinggi', text='Terjual')
        fig.update_traces(textposition='outside')
        fig.update_layout(height=410, margin=dict(l=10,r=30,t=45,b=10), xaxis_title='Unit', yaxis_title='')
        st.plotly_chart(fig, use_container_width=True, config={'displaylogo':False})
    with b:
        cat = df.groupby('Kategori', as_index=False)['Terjual'].sum().sort_values('Terjual', ascending=False)
        fig = px.pie(cat, names='Kategori', values='Terjual', hole=.52, template='plotly_white', title='Distribusi Penjualan per Kategori')
        fig.update_layout(height=410, margin=dict(l=10,r=10,t=45,b=10), legend_title='Kategori')
        st.plotly_chart(fig, use_container_width=True, config={'displaylogo':False})

    try:
        _, forecast, target_date = get_forecast_bundle()
        total_pred = forecast['hasil_prediksi'].sum()
        st.markdown(f'<div class="insight"><b>Informasi prediktif:</b> model Random Forest mengestimasi sekitar <b>{number(total_pred)} unit</b> penjualan pada {target_date.strftime("%B %Y")}. Nilai ini digunakan sebagai informasi pendukung perencanaan persediaan, bukan keputusan pembelian otomatis.</div>', unsafe_allow_html=True)
    except Exception as exc:
        st.warning(f'Prediksi belum dapat dihitung: {exc}')

elif page == 'Analisis Penjualan':
    hero('Analisis Penjualan', 'Eksplorasi data historis berdasarkan periode, kategori, produk, volume, dan nilai penjualan.')
    c1,c2,c3 = st.columns(3)
    categories = sorted(df['Kategori'].dropna().unique())
    products = sorted(df['Produk'].dropna().unique())
    with c1: cats = st.multiselect('Kategori', categories, default=categories)
    with c2: prods = st.multiselect('Produk', products, default=products)
    with c3: metric = st.selectbox('Indikator tren', ['Unit Terjual','Nilai Penjualan'])
    f = df[df['Kategori'].isin(cats) & df['Produk'].isin(prods)].copy()
    if f.empty:
        st.warning('Tidak ada data untuk kombinasi filter tersebut.')
        st.stop()
    trend = f.groupby('periode_date', as_index=False).agg(Terjual=('Terjual','sum'), Nilai=('NilaiPenjualan','sum'))
    y = 'Terjual' if metric == 'Unit Terjual' else 'Nilai'
    title_y = 'Unit' if y == 'Terjual' else 'Rupiah'
    fig = px.area(trend, x='periode_date', y=y, template='plotly_white', title=f'Tren {metric}')
    fig.update_layout(height=380, margin=dict(l=10,r=10,t=45,b=10), xaxis_title='', yaxis_title=title_y)
    st.plotly_chart(fig, use_container_width=True, config={'displaylogo':False})

    a,b = st.columns(2)
    with a:
        prod = f.groupby('Produk', as_index=False).agg(Terjual=('Terjual','sum'), Nilai=('NilaiPenjualan','sum')).sort_values('Terjual', ascending=False).head(12).sort_values('Terjual')
        fig = px.bar(prod, x='Terjual', y='Produk', orientation='h', template='plotly_white', title='Performa Produk Berdasarkan Unit')
        fig.update_layout(height=430, margin=dict(l=10,r=25,t=45,b=10), xaxis_title='Unit', yaxis_title='')
        st.plotly_chart(fig, use_container_width=True, config={'displaylogo':False})
    with b:
        cat = f.groupby('Kategori', as_index=False).agg(Terjual=('Terjual','sum'), Nilai=('NilaiPenjualan','sum')).sort_values('Terjual', ascending=False)
        fig = px.bar(cat, x='Kategori', y='Terjual', template='plotly_white', title='Penjualan per Kategori', text='Terjual')
        fig.update_layout(height=430, margin=dict(l=10,r=10,t=45,b=10), xaxis_title='', yaxis_title='Unit')
        st.plotly_chart(fig, use_container_width=True, config={'displaylogo':False})

    section('Ringkasan Analisis', 'Tabel agregasi membantu menghubungkan visualisasi dengan data sumber.')
    summary = f.groupby(['Produk','Kategori'], as_index=False).agg(Total_Terjual=('Terjual','sum'), Total_Nilai=('NilaiPenjualan','sum'), Rata2_Stok=('Stok','mean'), Harga_Rata2=('Harga','mean')).sort_values('Total_Terjual', ascending=False)
    st.dataframe(summary.style.format({'Total_Nilai':'Rp {:,.0f}','Rata2_Stok':'{:,.1f}','Harga_Rata2':'Rp {:,.0f}'}), use_container_width=True, hide_index=True)

elif page == 'Prediksi Random Forest':
    hero('Prediksi Penjualan — Random Forest', 'Prediksi penjualan bulan berikutnya menggunakan Harga, Stok, waktu, dan Lag 1–3 per produk.')
    with st.spinner('Menyiapkan model Random Forest dan evaluasi time-based split...'):
        model, feature_df, train, test, metrics = get_model_bundle()
        full_model, forecast, target_date = get_forecast_bundle()

    c1,c2,c3,c4 = st.columns(4)
    with c1: kpi('MAE', f'{metrics["MAE"]:.2f}', 'Rata-rata kesalahan absolut')
    with c2: kpi('RMSE', f'{metrics["RMSE"]:.2f}', 'Akar rata-rata kuadrat error')
    with c3: kpi('R²', f'{metrics["R2"]:.4f}', 'Koefisien determinasi')
    with c4: kpi('Prediksi Total', number(forecast['hasil_prediksi'].sum()), target_date.strftime('%B %Y'))

    st.markdown('<div class="insight"><b>Rancangan evaluasi:</b> data Januari–Desember 2025 digunakan sebagai training dan Januari–Juni 2026 sebagai testing. Pembagian berdasarkan waktu digunakan agar urutan historis tidak tercampur.</div>', unsafe_allow_html=True)

    section('Actual vs Prediction', 'Perbandingan hasil aktual dan prediksi pada data testing.')
    t = test.groupby('periode_date', as_index=False).agg(Actual=('Terjual','sum'), Prediction=('prediksi','sum'))
    long = t.melt('periode_date', var_name='Jenis', value_name='Unit')
    fig = px.line(long, x='periode_date', y='Unit', color='Jenis', markers=True, template='plotly_white')
    fig.update_layout(height=370, margin=dict(l=10,r=10,t=15,b=10), xaxis_title='', yaxis_title='Unit')
    st.plotly_chart(fig, use_container_width=True, config={'displaylogo':False})

    section(f'Prediksi Bulan Berikutnya — {target_date.strftime("%B %Y")}', 'Lag 1 = penjualan bulan terakhir, Lag 2 = dua bulan sebelumnya, Lag 3 = tiga bulan sebelumnya.')
    show = forecast[['Produk','Kategori','Harga','Stok','lag_1','lag_2','lag_3','hasil_prediksi']].copy()
    show.columns = ['Produk','Kategori','Harga','Stok','Lag 1','Lag 2','Lag 3','Prediksi Unit']
    st.dataframe(show.style.format({'Harga':'Rp {:,.0f}','Stok':'{:,.0f}','Prediksi Unit':'{:,.0f}','Lag 1':'{:,.0f}','Lag 2':'{:,.0f}','Lag 3':'{:,.0f}'}), use_container_width=True, hide_index=True)

    section('Feature Importance', 'Kontribusi relatif fitur terhadap pembentukan prediksi pada model yang dilatih.')
    imp = pd.DataFrame({'Fitur':FEATURES, 'Importance':full_model.feature_importances_}).sort_values('Importance', ascending=True)
    fig = px.bar(imp, x='Importance', y='Fitur', orientation='h', template='plotly_white')
    fig.update_layout(height=330, margin=dict(l=10,r=20,t=10,b=10), xaxis_title='Importance', yaxis_title='')
    st.plotly_chart(fig, use_container_width=True, config={'displaylogo':False})

    if user['role'] == 'admin':
        if st.button('Simpan hasil prediksi ke database', type='primary'):
            for _, r in forecast.iterrows():
                pid = int(df.loc[df['Produk'].eq(r['Produk']), 'id_produk'].iloc[0])
                execute('''INSERT INTO tb_prediksi (id_produk, periode_prediksi, lag_1, lag_2, lag_3, harga, stok, hasil_prediksi)
                           VALUES (%s,%s,%s,%s,%s,%s,%s,%s)''',
                        (pid, target_date.strftime('%Y-%m-01'), float(r['lag_1']), float(r['lag_2']), float(r['lag_3']), float(r['Harga']), int(r['Stok']), float(r['hasil_prediksi'])))
            log_activity(user['id_user'], 'Menyimpan hasil prediksi Random Forest')
            st.success('Hasil prediksi berhasil disimpan ke database.')

elif page == 'Perencanaan Persediaan':
    hero('Perencanaan Persediaan', 'Menyandingkan stok terakhir dengan estimasi penjualan bulan berikutnya sebagai informasi pendukung keputusan restock.')
    with st.spinner('Menghitung estimasi kebutuhan persediaan...'):
        _, forecast, target_date = get_forecast_bundle()
    plan = forecast.copy()
    plan['Selisih Prediksi-Stok'] = plan['hasil_prediksi'] - plan['Stok']
    plan['Indikasi'] = np.where(plan['Selisih Prediksi-Stok'] > 0, 'Perlu perhatian', 'Stok relatif mencukupi')
    total_gap = plan.loc[plan['Selisih Prediksi-Stok'] > 0, 'Selisih Prediksi-Stok'].sum()
    c1,c2,c3 = st.columns(3)
    with c1: kpi('Periode Prediksi', target_date.strftime('%B %Y'), 'Berdasarkan histori terakhir')
    with c2: kpi('Produk Perlu Perhatian', number((plan['Indikasi']=='Perlu perhatian').sum()), 'Prediksi lebih tinggi dari stok tercatat')
    with c3: kpi('Selisih Positif', number(total_gap), 'Estimasi gap agregat')

    st.markdown('<div class="warn-box"><b>Catatan metodologis:</b> selisih di halaman ini merupakan indikator sederhana antara prediksi penjualan dan stok tercatat. Sistem tidak menetapkan jumlah pembelian atau reorder point secara otomatis.</div>', unsafe_allow_html=True)
    section('Indikasi Persediaan per Produk', 'Gunakan informasi ini sebagai bahan evaluasi kebutuhan stok bersama kebijakan persediaan perusahaan.')
    show = plan[['Produk','Kategori','Stok','lag_1','lag_2','lag_3','hasil_prediksi','Selisih Prediksi-Stok','Indikasi']].copy()
    show.columns = ['Produk','Kategori','Stok Terakhir','Lag 1','Lag 2','Lag 3','Prediksi Penjualan','Selisih','Indikasi']
    st.dataframe(show.style.format({'Stok Terakhir':'{:,.0f}','Lag 1':'{:,.0f}','Lag 2':'{:,.0f}','Lag 3':'{:,.0f}','Prediksi Penjualan':'{:,.0f}','Selisih':'{:,.0f}'}), use_container_width=True, hide_index=True)

    gap = plan.sort_values('Selisih Prediksi-Stok', ascending=False).head(10).sort_values('Selisih Prediksi-Stok')
    fig = px.bar(gap, x='Selisih Prediksi-Stok', y='Produk', orientation='h', template='plotly_white', title='Produk dengan Selisih Prediksi terhadap Stok Terbesar')
    fig.update_layout(height=400, margin=dict(l=10,r=25,t=45,b=10), xaxis_title='Prediksi - Stok', yaxis_title='')
    st.plotly_chart(fig, use_container_width=True, config={'displaylogo':False})

elif page == 'Produk':
    hero('Master Produk', 'Informasi produk dan performa historis yang digunakan sebagai dasar analisis Business Intelligence.')
    p = df.groupby(['id_produk','Produk','Kategori'], as_index=False).agg(Total_Terjual=('Terjual','sum'), Rata2_Stok=('Stok','mean'), Harga_Terakhir=('Harga','last'))
    c1,c2,c3 = st.columns(3)
    with c1: kpi('Jumlah Produk', number(len(p)), 'Produk pada database')
    with c2: kpi('Kategori', number(p['Kategori'].nunique()), 'Kelompok produk')
    with c3: kpi('Rata-rata Penjualan', number(p['Total_Terjual'].mean()), 'Unit per produk selama histori')
    st.dataframe(p.style.format({'Total_Terjual':'{:,.0f}','Rata2_Stok':'{:,.1f}','Harga_Terakhir':'Rp {:,.0f}'}), use_container_width=True, hide_index=True)

elif page == 'Data Penjualan':
    hero('Data Penjualan', 'Data historis bulanan yang tersimpan pada MySQL dan menjadi sumber utama analisis serta pembentukan fitur machine learning.')
    c1,c2,c3 = st.columns(3)
    min_date, max_date = df['periode_date'].min(), df['periode_date'].max()
    with c1: start = st.date_input('Mulai periode', min_date.date(), min_value=min_date.date(), max_value=max_date.date())
    with c2: end = st.date_input('Sampai periode', max_date.date(), min_value=min_date.date(), max_value=max_date.date())
    with c3: cat = st.multiselect('Kategori', sorted(df['Kategori'].unique()), default=sorted(df['Kategori'].unique()))
    f = df[(df['periode_date'].dt.date >= start) & (df['periode_date'].dt.date <= end) & df['Kategori'].isin(cat)].copy()
    st.caption(f'{len(f):,} baris ditampilkan dari {len(df):,} baris data.')
    export = f[['periode','Produk','Kategori','Harga','Stok','Terjual']].copy()
    csv = export.to_csv(index=False).encode('utf-8-sig')
    st.download_button('Unduh data terfilter (CSV)', csv, 'data_penjualan_kramat_motor.csv', 'text/csv')
    st.dataframe(export.style.format({'Harga':'Rp {:,.0f}','Stok':'{:,.0f}','Terjual':'{:,.0f}'}), use_container_width=True, hide_index=True)

elif page == 'Manajemen Pengguna':
    hero('Manajemen Pengguna', 'Admin mengelola akun, status akses, dan reset password pengguna tanpa melihat password asli.')
    users = query_df('SELECT id_user, username, nama, email, role, status, created_at, updated_at FROM tb_user ORDER BY id_user')
    c1,c2,c3 = st.columns(3)
    with c1: kpi('Total Pengguna', number(len(users)), 'Akun terdaftar')
    with c2: kpi('Akun Aktif', number((users['status']=='aktif').sum()), 'Dapat login')
    with c3: kpi('Admin', number((users['role']=='admin').sum()), 'Pengguna dengan hak administrasi')
    st.dataframe(users,use_container_width=True,hide_index=True)

    section('Reset Password Pengguna', 'Gunakan bila pengguna meminta bantuan reset. Password baru tetap disimpan dalam bentuk hash.')
    choices = users['username'].tolist()
    with st.form('admin_reset_pw'):
        target = st.selectbox('Pilih username', choices)
        newpw = st.text_input('Password baru', type='password')
        conf = st.text_input('Konfirmasi password baru', type='password')
        reset = st.form_submit_button('Reset Password', type='primary')
    if reset:
        if not password_valid(newpw):
            st.error('Password minimal 8 karakter dan harus mengandung huruf besar, huruf kecil, serta angka.')
        elif newpw != conf:
            st.error('Konfirmasi password tidak sama.')
        else:
            uid = int(users.loc[users['username'].eq(target), 'id_user'].iloc[0])
            h = bcrypt.hashpw(newpw.encode(), bcrypt.gensalt()).decode()
            execute('UPDATE tb_user SET password_hash=%s, updated_at=CURRENT_TIMESTAMP WHERE id_user=%s', (h, uid))
            log_activity(user['id_user'], f'Reset password pengguna: {target}')
            st.success(f'Password {target} berhasil direset.')

elif page == 'Aktivitas Pengguna':
    hero('Aktivitas Pengguna', 'Audit trail untuk mencatat akses login, perubahan password, dan aktivitas penting pada sistem.')
    logs = query_df('''SELECT l.waktu, u.username, u.nama, u.role, l.aktivitas
                       FROM tb_log_aktivitas l JOIN tb_user u ON u.id_user=l.id_user
                       ORDER BY l.waktu DESC LIMIT 300''')
    c1,c2 = st.columns(2)
    with c1: kpi('Log Ditampilkan', number(len(logs)), 'Maksimal 300 aktivitas terbaru')
    with c2: kpi('Pengguna Tercatat', number(logs['username'].nunique() if not logs.empty else 0), 'Akun yang memiliki aktivitas')
    st.dataframe(logs,use_container_width=True,hide_index=True)

elif page == 'Profil':
    hero('Profil Pengguna', 'Kelola informasi akun, email, dan password untuk akses dashboard.')
    current = query_df('SELECT username, nama, email, role, status FROM tb_user WHERE id_user=%s', (user['id_user'],))
    if not current.empty:
        r = current.iloc[0]
        c1,c2,c3 = st.columns(3)
        with c1: kpi('Username', r['username'], 'Akun login')
        with c2: kpi('Role', ROLE_LABEL.get(r['role'], r['role']), 'Hak akses')
        with c3: kpi('Status', r['status'].title(), 'Status akun')
        section('Informasi Akun')
        with st.form('profile_form'):
            nama = st.text_input('Nama', value=r['nama'])
            email = st.text_input('Email', value=r['email'])
            save_profile = st.form_submit_button('Simpan Informasi', type='primary')
        if save_profile:
            try:
                execute('UPDATE tb_user SET nama=%s, email=%s, updated_at=CURRENT_TIMESTAMP WHERE id_user=%s', (nama.strip(), email.strip(), user['id_user']))
                st.session_state.user['nama'] = nama.strip()
                log_activity(user['id_user'], 'Memperbarui informasi profil')
                st.success('Informasi profil berhasil diperbarui.')
            except Exception as exc:
                st.error(f'Gagal memperbarui profil: {exc}')

        section('Ubah Password', 'Untuk perubahan password saat masih dapat login.')
        with st.form('change_pw'):
            old = st.text_input('Password saat ini', type='password')
            new = st.text_input('Password baru', type='password')
            confirm = st.text_input('Konfirmasi password baru', type='password')
            ok = st.form_submit_button('Simpan Password', type='primary')
        if ok:
            row = query_df('SELECT password_hash FROM tb_user WHERE id_user=%s', (user['id_user'],))
            valid = not row.empty and bcrypt.checkpw(old.encode(), row.iloc[0]['password_hash'].encode())
            if not valid:
                st.error('Password saat ini salah.')
            elif not password_valid(new):
                st.error('Password minimal 8 karakter dan harus mengandung huruf besar, huruf kecil, serta angka.')
            elif new != confirm:
                st.error('Konfirmasi password tidak sama.')
            else:
                h = bcrypt.hashpw(new.encode(), bcrypt.gensalt()).decode()
                execute('UPDATE tb_user SET password_hash=%s, updated_at=CURRENT_TIMESTAMP WHERE id_user=%s', (h, user['id_user']))
                log_activity(user['id_user'], 'Mengubah password sendiri')
                st.success('Password berhasil diubah.')
