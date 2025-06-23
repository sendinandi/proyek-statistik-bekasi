-- Membuat database jika belum ada, jadi aman untuk dijalankan kapan saja
CREATE DATABASE IF NOT EXISTS diskominfo_bekasi;

-- Menggunakan database yang baru dibuat atau yang sudah ada
USE diskominfo_bekasi;

-- 1. Tabel untuk menyimpan data user admin
-- Tabel ini menyimpan username dan password yang sudah di-hash (dienkripsi)
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    nama_lengkap VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Tabel untuk menyimpan METADATA (informasi) dari setiap file yang diupload
-- Ini adalah "katalog" dari semua dataset Anda
CREATE TABLE IF NOT EXISTS uploaded_datasets (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nama_dataset_tampilan VARCHAR(255) NOT NULL, -- Judul yang diinput admin
    kategori VARCHAR(100) NOT NULL,
    tahun_mulai INT NULL, -- Tahun awal data (bisa sama dengan tahun_akhir)
    tahun_akhir INT NULL, -- Tahun akhir data
    nama_file_asli VARCHAR(255), -- Nama original file yang diupload
    path_file VARCHAR(512) NOT NULL UNIQUE, -- Lokasi file di server
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);