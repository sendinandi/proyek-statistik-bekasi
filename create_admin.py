# create_admin.py (SUDAH DIUPDATE DENGAN KREDENSIAL TIDB CLOUD)

import mysql.connector
from getpass import getpass
import bcrypt

# --- Kredensial Database dari TiDB Cloud ---
DB_HOST = "gateway01.ap-southeast-1.prod.aws.tidbcloud.com"
DB_USER = "4ZEKyrvFbVhmAFA.root"
DB_PASSWORD = "Tz1KtmpI91GSwGqm"
DB_NAME = "diskominfo_bekasi"
DB_PORT = 4000  # Port standar untuk TiDB Cloud

def create_admin_user():
    print("--- Membuat User Admin Baru di Database Cloud ---")
    try:
        # Koneksi sekarang menggunakan kredensial cloud
        conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            port=DB_PORT
        )
        cursor = conn.cursor()

        username = input("Masukkan Username Admin Baru: ")
        nama_lengkap = input("Masukkan Nama Lengkap Anda: ")
        password = getpass("Masukkan Password Baru: ")
        password_confirm = getpass("Konfirmasi Password Baru: ")

        if password != password_confirm:
            print("\n❌ Password tidak cocok. Proses dibatalkan.")
            return

        # Hash password menggunakan bcrypt
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        # Simpan ke database cloud
        query = "INSERT INTO users (username, nama_lengkap, password) VALUES (%s, %s, %s)"
        cursor.execute(query, (username, nama_lengkap, hashed_password))
        conn.commit()

        print(f"\n✅ User admin '{username}' berhasil dibuat di database TiDB Cloud!")

    except mysql.connector.Error as err:
        print(f"\n❌ Gagal terhubung atau menyimpan ke database: {err}")
        print("   Pastikan kredensial sudah benar dan komputer Anda terhubung ke internet.")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == "__main__":
    create_admin_user()