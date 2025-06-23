# pages/2_🔑_Admin.py (STRUKTUR FINAL DENGAN TABS YANG BENAR)

import streamlit as st
import pandas as pd
import numpy as np
import db_config
import os
import time
from sklearn.ensemble import IsolationForest
import plotly.graph_objects as go

# HANYA PENGECEKAN KEAMANAN DI SINI.
# Login/Logout sudah di-handle secara global oleh Home.py
if not st.session_state.get("logged_in", False):
    st.error("🔒 Anda harus login untuk mengakses halaman ini.")
    st.stop()

st.title("🔑 Panel Admin: Upload Dataset Baru")

# Inisialisasi session_state untuk menyimpan data sementara antar tab
if 'admin_upload_data' not in st.session_state:
    st.session_state.admin_upload_data = {
        "df": None,
        "params": {},
        "original_filename": None,
        "is_processed": False
    }

# Membuat Tabs
tab1, tab2, tab3 = st.tabs([
    "**1️⃣ Upload & Metadata**", 
    "**2️⃣ Preview & Grafik**", 
    "**3️⃣ Deteksi Anomali & Simpan**"
])


# --- SEMUA KODE UNTUK LANGKAH 1 ADA DI DALAM BLOK INI ---
with tab1:
    st.header("Langkah 1: Isi Detail dan Upload File")
    
    # Gunakan form untuk mengelompokkan input dan tombol proses
    with st.form("metadata_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        display_name = col1.text_input("Masukkan Judul Dataset (Nama Tampilan):", placeholder="Contoh: Jumlah Kunjungan Posyandu")
        kategori_list = ["Kesehatan", "Pemerintahan", "Pendidikan", "Ekonomi", "Sosial", "Lainnya"]
        selected_kategori = col2.selectbox("Pilih Kategori:", kategori_list)
        
        is_multiyear = st.checkbox("File ini berisi data untuk beberapa tahun (memiliki kolom 'Tahun')")
        selected_year = None
        if not is_multiyear:
            selected_year = st.number_input("Pilih Tahun Data (untuk data bulanan):", min_value=2010, max_value=2050, value=2025)
        
        uploaded_file = st.file_uploader("Upload file CSV Anda di sini:", type=['csv'])

        # Tombol submit untuk form
        submitted = st.form_submit_button("Proses File")
        if submitted:
            if uploaded_file is not None and display_name:
                with st.spinner("Memproses file..."):
                    try:
                        df = pd.read_csv(uploaded_file)
                        # Simpan semua ke session state
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
                        st.success("File berhasil diproses! Silakan pindah ke tab berikutnya.")
                    except Exception as e:
                        st.error(f"Gagal memproses file: {e}")
                        st.session_state.admin_upload_data["is_processed"] = False
            else:
                st.warning("Mohon isi Judul Dataset dan upload file sebelum memproses.")


# --- SEMUA KODE UNTUK LANGKAH 2 ADA DI DALAM BLOK INI ---
with tab2:
    st.header("Langkah 2: Preview Data dan Visualisasi")
    if st.session_state.admin_upload_data.get("is_processed"):
        df = st.session_state.admin_upload_data["df"]
        params = st.session_state.admin_upload_data["params"]
        
        st.info(f"Menampilkan data untuk **{params['nama_dataset_tampilan']}**")
        st.subheader("Preview Tabel Data")
        st.dataframe(df)
        
        st.subheader("Visualisasi Sederhana")
        if len(df.columns) > 1:
            # ... (Sisa kode visualisasi sama seperti sebelumnya) ...
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
        st.info("Silakan isi detail dan proses file di tab **1. Upload & Metadata** terlebih dahulu.")


# --- SEMUA KODE UNTUK LANGKAH 3 ADA DI DALAM BLOK INI ---
with tab3:
    st.header("Langkah 3: Deteksi Anomali dan Finalisasi")
    if st.session_state.admin_upload_data.get("is_processed"):
        df = st.session_state.admin_upload_data["df"]
        params = st.session_state.admin_upload_data["params"]
        
        st.subheader("Deteksi Anomali")
        # ... (Sisa kode deteksi anomali dan simpan sama seperti sebelumnya) ...
        numeric_cols_anomaly = df.select_dtypes(include=np.number).columns.tolist()
        if numeric_cols_anomaly:
            col_to_check = st.selectbox("Pilih kolom untuk diperiksa anomalinya:", numeric_cols_anomaly)
            if col_to_check:
                model = IsolationForest(contamination='auto', random_state=42)
                # Normalisasi nama kolom sebelum menambahkan 'is_anomaly'
                df.columns = df.columns.str.lower().str.replace(' ', '_')
                df['is_anomaly'] = model.fit_predict(df[[col_to_check.lower().replace(' ', '_')]])
                anomalies = df[df['is_anomaly'] == -1]
                if not anomalies.empty:
                    st.warning(f"⚠️ Ditemukan {len(anomalies)} potensi anomali!")
                    st.dataframe(anomalies)
                else:
                    st.success("✅ Tidak ada anomali yang terdeteksi.")

        st.markdown("---")
        st.subheader("Simpan ke Sistem")
        
        tahun_mulai, tahun_akhir = None, None
        try:
            df_original_case = st.session_state.admin_upload_data["df"]
            df_original_case.columns = df_original_case.columns.str.lower()
            if params['is_multiyear']:
                if 'tahun' in df_original_case.columns:
                    tahun_mulai = int(df_original_case['tahun'].min())
                    tahun_akhir = int(df_original_case['tahun'].max())
                else:
                    st.error("Checkbox rentang tahun dicentang, tetapi kolom 'Tahun'/'tahun' tidak ditemukan.")
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
                    
                    df_to_save = st.session_state.admin_upload_data["df"]
                    df_to_save.to_csv(file_path, index=False)
                    
                    result = db_config.insert_dataset_metadata(
                        nama_dataset_tampilan=params['nama_dataset_tampilan'], kategori=params['kategori'],
                        tahun_mulai=tahun_mulai, tahun_akhir=tahun_akhir,
                        nama_file_asli=st.session_state.admin_upload_data["original_filename"], path_file=file_path
                    )
                    
                    if "Sukses" in result:
                        st.success(result)
                        st.balloons()
                        st.cache_data.clear()
                        # Reset state
                        st.session_state.admin_upload_data = {"df": None, "params": {}, "original_filename": None, "is_processed": False}
                        st.rerun()
                    else:
                        st.error(result)
        except Exception as e:
            st.error(f"Terjadi kesalahan pada tahap finalisasi: {e}")
    else:
        st.info("Silakan isi detail dan proses file di tab **1. Upload & Metadata** terlebih dahulu.")