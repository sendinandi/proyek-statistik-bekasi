import streamlit as st
import pandas as pd
import bcrypt
from sqlalchemy import text
from mysql.connector import Error

# Jangan buat conn di sini
# conn = st.connection("mysql_db", type="sql") ❌

# --- Fungsi Autentikasi (Tetap Sama) ---
def verify_user(username, password):
    conn = st.connection("mysql_db", type="sql")  # ✅ Panggil hanya saat dipakai
    try:
        query = f"SELECT password, nama_lengkap FROM users WHERE username = '{username}'"
        user_data = conn.query(query, ttl=0)
        if not user_data.empty:
            stored_hash = user_data["password"][0].encode('utf-8')
            if bcrypt.checkpw(password.encode('utf-8'), stored_hash):
                return {"username": username, "nama_lengkap": user_data["nama_lengkap"][0]}
        return None
    except Exception:
        return None

# --- Fungsi Baru untuk Mengelola Metadata Dataset ---
@st.cache_data(ttl=300)
def get_all_datasets_metadata():
    conn = st.connection("mysql_db", type="sql")  # ✅ Panggil di sini juga
    return conn.query("SELECT * FROM uploaded_datasets ORDER BY kategori, nama_dataset_tampilan", ttl=300)

# --- Fungsi Insert Metadata ---
def insert_dataset_metadata(nama_dataset_tampilan, kategori, tahun_mulai, tahun_akhir, nama_file_asli, path_file):
    conn = st.connection("mysql_db", type="sql")  # ✅ Di sini juga
    try:
        with conn.session as s:
            query = text("""
                INSERT INTO uploaded_datasets (nama_dataset_tampilan, kategori, tahun_mulai, tahun_akhir, nama_file_asli, path_file)
                VALUES (:nama_dataset_tampilan, :kategori, :tahun_mulai, :tahun_akhir, :nama_file_asli, :path_file)
            """)
            s.execute(query, {
                "nama_dataset_tampilan": nama_dataset_tampilan,
                "kategori": kategori,
                "tahun_mulai": tahun_mulai,
                "tahun_akhir": tahun_akhir,
                "nama_file_asli": nama_file_asli,
                "path_file": path_file
            })
            s.commit()
            return "✅ Sukses: Metadata dataset berhasil disimpan ke database."
    except Exception as ex:
        return f"❌ Terjadi kesalahan saat menyimpan metadata: {ex}"
