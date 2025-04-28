import os

CREDENTIALS_DIR = "credentials"
FILES_TO_DELETE = [
    "token.pickle",
    "client_secret.json",
    "valid_api_keys.json"
]

def delete_file(file_path):
    if os.path.exists(file_path):
        os.remove(file_path)
        print(f"🗑️  Berhasil menghapus: {file_path}")
    else:
        print(f"ℹ️  File tidak ditemukan (sudah dihapus?): {file_path}")

def main():
    print("🔁 Menghapus file konfigurasi autentikasi...\n")
    for filename in FILES_TO_DELETE:
        path = os.path.join(CREDENTIALS_DIR, filename)
        delete_file(path)
    print("\n✅ Semua konfigurasi yang ditentukan telah diproses.")

if __name__ == "__main__":
    main()
