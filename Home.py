import streamlit as st

st.set_page_config(page_title="Selamat Datang - Statistik Bekasi", page_icon="👋", layout="wide")

import db_config

    
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

# --- KONTEN HALAMAN UTAMA (WELCOME PAGE) ---
st.title("👋 Selamat Datang di Portal Statistik Kota Bekasi")
st.markdown("---")
# (Sisa kode welcome page Anda tetap sama seperti sebelumnya)
col1, col2 = st.columns([1, 2])
with col1:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/c/c1/Coat_of_arms_of_Bekasi.svg/882px-Coat_of_arms_of_Bekasi.svg.png", width=200)
with col2:
    st.header("Analisis dan Prediksi Data Terintegrasi")
    st.markdown("""
    Aplikasi ini dirancang untuk membantu dalam visualisasi, analisis, dan prediksi data statistik di lingkungan Pemerintah Kota Bekasi.
    """)
st.info("Pilih halaman dari menu navigasi di atas sidebar.")