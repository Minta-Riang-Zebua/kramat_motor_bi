import os
from pathlib import Path
import mysql.connector
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
SCHEMA_FILE = BASE_DIR / 'sql' / 'schema_and_seed.sql'


def _config(include_database=True):
    cfg = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': int(os.getenv('DB_PORT', '3306')),
        'user': os.getenv('DB_USER', 'root'),
        'password': os.getenv('DB_PASSWORD', ''),
    }
    if include_database:
        cfg['database'] = os.getenv('DB_NAME', 'kramat_motor_bi')
    return cfg


def get_connection():
    return mysql.connector.connect(**_config(True))


def get_server_connection():
    return mysql.connector.connect(**_config(False))


def query_df(sql, params=None):
    conn = get_connection()
    try:
        return pd.read_sql(sql, conn, params=params)
    finally:
        conn.close()


def execute(sql, params=None):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(sql, params or ())
        conn.commit()
        return cur.lastrowid
    finally:
        cur.close()
        conn.close()


def _run_schema_file(conn):
    sql_text = SCHEMA_FILE.read_text(encoding='utf-8')
    # The project SQL contains ordinary statements without procedures/functions,
    # so semicolon splitting is sufficient and keeps phpMyAdmin import compatible.
    statements = [s.strip() for s in sql_text.split(';') if s.strip()]
    cur = conn.cursor()
    try:
        for statement in statements:
            lines = [line for line in statement.splitlines() if not line.strip().startswith('--')]
            statement = '\n'.join(lines).strip()
            if statement:
                cur.execute(statement)
        conn.commit()
    finally:
        cur.close()


def ensure_database_schema():
    """Create the database/schema if the local MySQL server is reachable.

    Returns a status message. Existing installations are preserved; a missing
    email column from an older project version is migrated automatically.
    """
    conn = get_server_connection()
    cur = conn.cursor()
    try:
        db_name = os.getenv('DB_NAME', 'kramat_motor_bi')
        cur.execute(f"CREATE DATABASE IF NOT EXISTS `{db_name}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        cur.execute(f"USE `{db_name}`")
        cur.execute("SHOW TABLES LIKE 'tb_user'")
        has_user = cur.fetchone() is not None
        if not has_user:
            cur.close()
            _run_schema_file(conn)
            cur = conn.cursor()
        else:
            cur.execute("SHOW COLUMNS FROM tb_user LIKE 'email'")
            has_email = cur.fetchone() is not None
            if not has_email:
                cur.execute("ALTER TABLE tb_user ADD COLUMN email VARCHAR(150) NULL AFTER nama")
                cur.execute("UPDATE tb_user SET email=CONCAT(username,'@kramatmotor.local') WHERE email IS NULL OR email='' ")
                cur.execute("ALTER TABLE tb_user MODIFY email VARCHAR(150) NOT NULL")
                try:
                    cur.execute("ALTER TABLE tb_user ADD UNIQUE KEY uq_tb_user_email (email)")
                except mysql.connector.Error:
                    pass
                conn.commit()
            # Ensure demo accounts/data exist if the installation was partially imported.
            cur.execute("SELECT COUNT(*) FROM tb_user")
            user_count = cur.fetchone()[0]
            if user_count == 0:
                cur.close()
                _run_schema_file(conn)
                cur = conn.cursor()
        return True, 'Database dan struktur tabel siap digunakan.'
    finally:
        cur.close()
        conn.close()


def database_health():
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT COUNT(*) FROM tb_user")
        users = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM tb_produk")
        products = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM tb_penjualan")
        sales = cur.fetchone()[0]
        return {'users': users, 'products': products, 'sales': sales}
    finally:
        cur.close()
        conn.close()


def load_sales():
    return query_df('''
        SELECT p.id_penjualan, p.periode, p.periode_date, pr.id_produk,
               pr.nama_produk AS Produk, pr.kategori AS Kategori,
               p.harga AS Harga, p.stok AS Stok, p.terjual AS Terjual
        FROM tb_penjualan p
        JOIN tb_produk pr ON pr.id_produk = p.id_produk
        ORDER BY p.periode_date, pr.nama_produk
    ''')


def log_activity(user_id, activity):
    try:
        execute('INSERT INTO tb_log_aktivitas (id_user, aktivitas) VALUES (%s,%s)', (user_id, activity))
    except Exception:
        pass
