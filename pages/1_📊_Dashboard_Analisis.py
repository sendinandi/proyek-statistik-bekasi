# pages/1_📊_Dashboard_Analisis.py (PERBAIKAN FINAL UNTUK SEMUA JENIS DATA)

import streamlit as st
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
import plotly.graph_objects as go
import db_config
import os

st.title("📊 Dashboard Analisis & Prediksi Data Statistik")
st.info("Pilih Kategori dan Dataset untuk menampilkan data.")
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
                
# --- Filter ---
metadata_df = db_config.get_all_datasets_metadata()
if metadata_df.empty:
    st.warning("Belum ada data tersedia. Silakan upload data melalui halaman Admin.")
    st.stop()

col1, col2 = st.columns(2)
kategori_list = sorted(metadata_df['kategori'].unique())
selected_kategori = col1.selectbox("1. Pilih Kategori", kategori_list)
filtered_datasets = metadata_df[metadata_df['kategori'] == selected_kategori]
dataset_list = filtered_datasets['nama_dataset_tampilan'].tolist()

if not dataset_list:
    st.warning(f"Tidak ada dataset untuk kategori '{selected_kategori}'.")
    st.stop()
selected_dataset_display_name = col2.selectbox("2. Pilih Dataset", dataset_list)

# --- Ambil dan Tampilkan Data ---
if selected_dataset_display_name:
    selected_row = metadata_df[metadata_df['nama_dataset_tampilan'] == selected_dataset_display_name]
    if not selected_row.empty:
        file_path = selected_row['path_file'].iloc[0]
        
        st.header(f"Analisis: {selected_dataset_display_name}")
        start_year = selected_row['tahun_mulai'].iloc[0]
        end_year = selected_row['tahun_akhir'].iloc[0]
        year_display = str(start_year) if start_year == end_year else f"{start_year} - {end_year}"
        st.markdown(f"**Tahun Data:** `{year_display}` | **Nama File Asli:** `{selected_row['nama_file_asli'].iloc[0]}`")

        if os.path.exists(file_path):
            try:
                df = pd.read_csv(file_path)
                st.subheader("Data dari File")
                
                # Logika pengurutan bulan teks
                # Letakkan blok ini setelah baris df = pd.read_csv(file_path)

                if df.columns.to_list():
                    # Ambil kolom pertama sebagai kandidat kolom waktu
                    time_col_candidate = df.columns[0]
    
                    # 1. Definisikan "kamus" untuk bulan dan hari
                    month_map = {
                        'januari': 1, 'februari': 2, 'maret': 3, 'april': 4, 'mei': 5, 'juni': 6, 
                        'juli': 7, 'agustus': 8, 'september': 9, 'oktober': 10, 'november': 11, 'desember': 12
                    }
                    day_map = {
                        'senin': 1, 'selasa': 2, 'rabu': 3, 'kamis': 4, 'jumat': 5, 'sabtu': 6, 'minggu': 7
                    }
    
                    # Ambil data kolom pertama dan ubah ke huruf kecil untuk pengecekan
                    column_data_lower = df[time_col_candidate].astype(str).str.lower()
    
                    # 2. Cek jika kolom berisi nama bulan
                    if column_data_lower.isin(month_map.keys()).all():
                        # Buat kunci urutan berdasarkan nomor bulan, lalu urutkan
                        df['sort_key'] = column_data_lower.map(month_map)
                        df = df.sort_values(by='sort_key').drop(columns=['sort_key'])
                    # 3. Jika bukan bulan, cek jika kolom berisi nama hari
                    elif column_data_lower.isin(day_map.keys()).all():
                        # Buat kunci urutan berdasarkan nomor hari, lalu urutkan
                        df['sort_key'] = column_data_lower.map(day_map)
                        df = df.sort_values(by='sort_key').drop(columns=['sort_key'])
                    # 4. Jika bukan keduanya, cek jika kolomnya adalah angka (seperti Tahun)
                    elif pd.api.types.is_numeric_dtype(df[time_col_candidate]):
                        # Langsung urutkan berdasarkan nilai angka tersebut
                        df = df.sort_values(by=time_col_candidate)
                        st.dataframe(df)

                tab1, tab2 = st.tabs(["🖼️ Visualisasi Umum", "📈 Analisis Prediksi"])

                with tab1:
                    # Kode visualisasi umum sudah benar
                    st.header("Visualisasi Data")
                    if len(df.columns) > 1:
                        all_cols_vis = df.columns.tolist()
                        numeric_cols_vis = df.select_dtypes(include=np.number).columns.tolist()
                        if numeric_cols_vis:
                            col_vis1, col_vis2 = st.columns(2)
                            x_col_vis = col_vis1.selectbox("Pilih Kolom untuk Sumbu X:", all_cols_vis, key="vis_x")
                            y_col_vis = col_vis2.selectbox("Pilih Kolom untuk Sumbu Y:", numeric_cols_vis, key="vis_y")
                            if x_col_vis and y_col_vis:
                                fig_vis = go.Figure(data=go.Scatter(x=df[x_col_vis], y=df[y_col_vis], mode='lines+markers'))
                                fig_vis.update_layout(title=f'Grafik {y_col_vis} berdasarkan {x_col_vis}', xaxis_title=x_col_vis, yaxis_title=y_col_vis)
                                st.plotly_chart(fig_vis, use_container_width=True)

                with tab2:
                    st.header("Prediksi Tren Data (Regresi Linear)")
                    all_cols_pred = df.columns.tolist()
                    numeric_cols_pred = df.select_dtypes(include=np.number).columns.tolist()

                    if len(numeric_cols_pred) < 1:
                        st.warning("Prediksi memerlukan setidaknya satu kolom numerik.")
                    else:
                        col_pred1, col_pred2 = st.columns(2)
                        time_col = col_pred1.selectbox("1. Pilih kolom Waktu (X):", all_cols_pred, key="pred_x")
                        target_col = col_pred2.selectbox("2. Pilih kolom Nilai (Y):", numeric_cols_pred, key="pred_y")

                        if time_col and target_col and time_col != target_col:
                            df_pred = df[[time_col, target_col]].dropna().reset_index(drop=True)

                            if len(df_pred) < 3:
                                st.warning("Data terlalu sedikit untuk menghasilkan prediksi yang andal.")
                            else:
                                # Model regresi berdasarkan indeks
                                X = pd.DataFrame(df_pred.index, columns=['time_feature'])
                                y = df_pred[target_col]
                                model = LinearRegression().fit(X, y)

                                st.subheader("3. Buat Prediksi")
                                periods = st.slider("Pilih jumlah periode ke depan:", 1, 12, 6)
                                last_index = X['time_feature'].max()
                                future_indices = [last_index + i + 1 for i in range(periods)]
                                future_X = pd.DataFrame(future_indices, columns=['time_feature'])
                                predictions = model.predict(future_X)

                                # --- Penyesuaian label waktu untuk prediksi ---
                                future_labels = []
                                if pd.api.types.is_numeric_dtype(df_pred[time_col]):
                                    try:
                                        last_time = int(df_pred[time_col].iloc[-1])
                                        future_labels = [str(last_time + i + 1) for i in range(periods)]
                                    except:
                                        future_labels = [f"Prediksi {i+1}" for i in range(periods)]
                                else:
                                    future_labels = [f"Prediksi {i+1}" for i in range(periods)]

                                # Tampilkan tabel prediksi
                                pred_df = pd.DataFrame({
                                    'Periode': future_labels,
                                    'Prediksi Nilai': np.round(predictions, 2)
                                })
                                st.table(pred_df)

                                # --- Grafik Gabungan ---
                                st.subheader("4. Grafik Prediksi vs Historis")

                                x_axis_labels = list(df_pred[time_col].astype(str)) + future_labels
                                y_hist = list(y) + [None] * periods
                                y_pred = [None] * len(y) + list(predictions)

                                fig_pred = go.Figure()
                                fig_pred.add_trace(go.Scatter(
                                    x=x_axis_labels,
                                    y=y_hist,
                                    mode='lines+markers',
                                    name='Data Historis'
                                ))
                                fig_pred.add_trace(go.Scatter(
                                    x=x_axis_labels,
                                    y=y_pred,
                                    mode='lines+markers',
                                    name='Data Prediksi',
                                    line=dict(dash='dash'),
                                    marker=dict(color='lightblue')
                                ))

                                fig_pred.update_layout(
                                    title=f'Prediksi {target_col} berdasarkan {time_col}',
                                    xaxis_title='Periode',
                                    yaxis_title=target_col
                                )
                                st.plotly_chart(fig_pred, use_container_width=True)


            except Exception as e:
                st.error(f"Gagal memproses data: {e}")
        else:
            st.error(f"File tidak ditemukan: {file_path}.")