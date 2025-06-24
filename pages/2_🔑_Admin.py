# pages/2_🔑_Admin.py (PERBAIKAN UI HILANGKAN TAHUN)

import streamlit as st
import pandas as pd
import numpy as np
import db_config
import os
import time
from sklearn.ensemble import IsolationForest
import plotly.graph_objects as go

st.sidebar.title("Navigasi & Akses")
if st.session_state.get("logged_in", False):
    nama_user = st.session_state.get('nama_lengkap', 'Admin')
    st.sidebar.success(f"Login sebagai: {nama_user}")
    if st.sidebar.button("Logout", key="global_logout"):
        # Hapus semua session state terkait login
        for key in list(st.session_state.keys()):
            if key in ["logged_in", "nama_lengkap", "username"]:
                del st.session_state[key]
        st.rerun()
else:
    # Form login jika belum login
    with st.sidebar.form("global_login_form"):
        # ... (kode form login tetap sama) ...
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.form_submit_button("Login"):
            user_info = db_config.verify_user(username, password)
            if user_info:
                st.session_state["logged_in"] = True
                st.session_state["nama_lengkap"] = user_info["nama_lengkap"]
                st.session_state["username"] = user_info["username"]
                st.rerun()
            else:
                st.sidebar.error("😕 Username/password salah.")
                
# Keamanan: Pengecekan login
if not st.session_state.get("logged_in", False):
    st.error("🔒 Anda harus login untuk mengakses halaman ini.")
    st.stop()

st.title("🔑 Panel Admin: Upload Dataset Baru")

# Inisialisasi session_state
if 'admin_upload_data' not in st.session_state:
    st.session_state.admin_upload_data = {
        "df": None,
        "params": {},
        "original_filename": None,
        "is_processed": False
    }

# Membuat Tabs
tab1, tab2, tab3 = st.tabs([
    "**1. Upload & Metadata**", 
    "**2. Preview & Grafik**", 
    "**3. Deteksi Anomali & Simpan**"
])


# --- TAB 1: UPLOAD & METADATA ---
with tab1:
    st.header("Langkah 1: Isi Detail dan Upload File")
    
    # --- Input diletakkan di luar form ---
    display_name = st.text_input("Masukkan Judul Dataset (Nama Tampilan):", placeholder="Contoh: Jumlah Kunjungan Posyandu")
    kategori_list = ["Kesehatan", "Pemerintahan", "Pendidikan", "Ekonomi", "Sosial", "Lainnya"]
    selected_kategori = st.selectbox("Pilih Kategori:", kategori_list)
    
    is_multiyear = st.checkbox("File ini berisi data untuk beberapa tahun (memiliki kolom 'Tahun')")
    
    selected_year = None
    # Logika kondisional untuk menampilkan input tahun
    if not is_multiyear:
        selected_year = st.number_input("Pilih Tahun Data (untuk data bulanan):", min_value=2010, max_value=2050, value=2025)
    
    uploaded_file = st.file_uploader("Upload file CSV Anda di sini:", type=['csv'])

    # --- Form hanya untuk tombol submit ---
    with st.form("process_form"):
        submitted = st.form_submit_button("Proses File")
        if submitted:
            if uploaded_file is not None and display_name:
                with st.spinner("Memproses file..."):
                    try:
                        df = pd.read_csv(uploaded_file)
                        st.session_state.admin_upload_data = {
                            "df": df,
                            "params": {
                                "nama_dataset_tampilan": display_name,
                                "kategori": selected_kategori,
                                "is_multiyear": is_multiyear,
                                "selected_year": selected_year
                            },
                            "original_filename": uploaded_file.name,
                            "is_processed": True
                        }
                        st.success("File berhasil diproses! Silakan pindah ke tab berikutnya untuk validasi.")
                    except Exception as e:
                        st.error(f"Gagal memproses file: {e}")
                        st.session_state.admin_upload_data["is_processed"] = False
            else:
                st.warning("Mohon isi Judul Dataset dan upload file sebelum memproses.")


# --- TAB 2: PREVIEW & GRAFIK ---
with tab2:
    st.header("Langkah 2: Preview Data dan Visualisasi")
    if st.session_state.admin_upload_data.get("is_processed"):
        df = st.session_state.admin_upload_data["df"]
        params = st.session_state.admin_upload_data["params"]
        
        st.subheader("Preview Tabel Data")
        st.dataframe(df)
        
        st.subheader("Visualisasi Sederhana")
        if len(df.columns) > 1:
            all_cols = df.columns.tolist()
            numeric_cols = df.select_dtypes(include=np.number).columns.tolist()
            if numeric_cols:
                col_vis1, col_vis2 = st.columns(2)
                x_col = col_vis1.selectbox("Pilih Kolom Sumbu X:", all_cols, key="vis_x_admin")
                y_col = col_vis2.selectbox("Pilih Kolom Sumbu Y:", numeric_cols, key="vis_y_admin")
                if x_col and y_col:
                    fig = go.Figure(data=go.Scatter(x=df[x_col], y=df[y_col], mode='lines+markers'))
                    fig.update_layout(title=f"Grafik {y_col} vs {x_col}", xaxis_title=x_col, yaxis_title=y_col)
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Tidak ada kolom numerik untuk divisualisasikan.")
    else:
        st.info("Silakan isi detail dan proses file di tab **1. Upload & Metadata** terlebih dahulu.")


# --- TAB 3: DETEKSI ANOMALI & SIMPAN ---
with tab3:
    st.header("Langkah 3: Deteksi Anomali dan Finalisasi")
    if st.session_state.admin_upload_data.get("is_processed"):
        df = st.session_state.admin_upload_data["df"]
        params = st.session_state.admin_upload_data["params"]
        
        st.subheader("Deteksi Anomali")
        numeric_cols_anomaly = df.select_dtypes(include=np.number).columns.tolist()
        if numeric_cols_anomaly:
            col_to_check = st.selectbox("Pilih kolom untuk diperiksa anomalinya:", numeric_cols_anomaly)
            if col_to_check:
                model = IsolationForest(contamination='auto', random_state=42)
                df['is_anomaly'] = model.fit_predict(df[[col_to_check]])
                anomalies = df[df['is_anomaly'] == -1]
                if not anomalies.empty:
                    st.warning(f"⚠️ **Ditemukan {len(anomalies)} potensi anomali pada kolom '{col_to_check}'!**")
                    st.dataframe(anomalies)
                else:
                    st.success("✅ Tidak ada anomali yang terdeteksi.")
        else:
            st.info("Tidak ada kolom numerik untuk dideteksi anomalinya.")

        st.markdown("---")
        st.subheader("Simpan ke Sistem")
        
        # Logika untuk menentukan rentang tahun dipindahkan ke sini, saat akan disimpan
        tahun_mulai, tahun_akhir = None, None
        try:
            df_original_case = st.session_state.admin_upload_data["df"]
            cols_lower = [c.lower() for c in df_original_case.columns]
            if params['is_multiyear']:
                if 'tahun' in cols_lower:
                    idx_tahun = cols_lower.index('tahun')
                    tahun_colname = df_original_case.columns[idx_tahun]
                    tahun_mulai = int(df_original_case[tahun_colname].min())
                    tahun_akhir = int(df_original_case[tahun_colname].max())
                else:
                    st.error("Checkbox rentang tahun dicentang, tetapi kolom 'Tahun' tidak ditemukan (dalam bentuk huruf besar/kecil).")
                    st.stop()
            else:
                tahun_mulai = params['selected_year']
                tahun_akhir = params['selected_year']
            
            if st.button(f"Simpan Dataset '{params['nama_dataset_tampilan']}'"):
                with st.spinner("Menyimpan..."):
                    timestamp = int(time.time())
                    unique_filename = f"{tahun_mulai}_{tahun_akhir}_{params['kategori'].lower().replace(' ', '')}_{timestamp}.csv"
                    upload_dir = "csv_uploads"
                    if not os.path.exists(upload_dir):
                        os.makedirs(upload_dir)
                    file_path = os.path.join(upload_dir, unique_filename)
                    df_to_save = df.drop(columns=['is_anomaly'], errors='ignore')
                    df_to_save.to_csv(file_path, index=False)
                    
                    result = db_config.insert_dataset_metadata(
                        nama_dataset_tampilan=params['nama_dataset_tampilan'], kategori=params['kategori'],
                        tahun_mulai=tahun_mulai, tahun_akhir=tahun_akhir,
                        nama_file_asli=st.session_state.admin_upload_data["original_filename"], path_file=file_path
                    )
                    
                    if result and "sukses" in result.lower():
                        st.success(result)
                        st.balloons()
                        st.cache_data.clear()
                        st.session_state.admin_upload_data = {"df": None, "params": {}, "original_filename": None, "is_processed": False}
                        st.rerun()
                    else:
                        st.error(result)

        except Exception as e:
            st.error(f"Terjadi kesalahan pada tahap finalisasi: {e}")
    else:
        st.info("Silakan isi detail dan proses file di tab **1. Upload & Metadata** terlebih dahulu.")