# create_admin.py

import mysql.connector
from getpass import getpass
import bcrypt

# --- Kredensial Database (Sesuaikan jika perlu) ---
# NOTE: Script ini dijalankan lokal, jadi tidak masalah menaruh kredensial di sini.
# Atau, Anda bisa menggunakan cara yang lebih canggih untuk memuatnya.
DB_HOST = "localhost"
DB_USER = "root"  # Ganti dengan username DB Anda
DB_PASSWORD = "" # Ganti dengan password DB Anda
DB_NAME = "diskominfo_bekasi"

def create_admin_user():
    print("--- Membuat User Admin Baru ---")
    try:
        conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        cursor = conn.cursor()

        username = input("Masukkan Username Admin: ")
        nama_lengkap = input("Masukkan Nama Lengkap: ")
        password = getpass("Masukkan Password Admin: ")
        password_confirm = getpass("Konfirmasi Password Admin: ")

        if password != password_confirm:
            print("\n❌ Password tidak cocok. Proses dibatalkan.")
            return

        # Hash password menggunakan bcrypt
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        # Simpan ke database
        query = "INSERT INTO users (username, nama_lengkap, password) VALUES (%s, %s, %s)"
        cursor.execute(query, (username, nama_lengkap, hashed_password))
        conn.commit()

        print(f"\n✅ User admin '{username}' berhasil dibuat!")

    except mysql.connector.Error as err:
        print(f"\n❌ Gagal terhubung atau menyimpan ke database: {err}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == "__main__":
    create_admin_user()