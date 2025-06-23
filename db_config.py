import streamlit as st
import pandas as pd
import bcrypt
from sqlalchemy import text

def get_connection():
    return st.connection("mysql_db", type="sql")

# --- Fungsi Autentikasi (Tetap Sama) ---
def verify_user(username, password):
    conn = get_connection()
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

@st.cache_data(ttl=300)
def get_all_datasets_metadata():
    conn = get_connection()
    return conn.query("SELECT * FROM uploaded_datasets ORDER BY kategori, nama_dataset_tampilan", ttl=300)

def insert_dataset_metadata(nama_dataset_tampilan, kategori, tahun_mulai, tahun_akhir, nama_file_asli, path_file):
    conn = get_connection()
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
            return "✅ Metadata berhasil disimpan."
    except Exception as ex:
        return f"❌ Gagal menyimpan metadata: {ex}"
