import os
import json
import time
import pickle

from google_auth_oauthlib.flow import InstalledAppFlow

# Folder untuk menyimpan client_id, client_secret, dan token
CREDENTIALS_DIR = "credentials"
os.makedirs(CREDENTIALS_DIR, exist_ok=True)

# Scope untuk YouTube Data API
SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]

def input_credentials(index):
    print(f"\n📝 Input manual untuk credentials #{index}:")
    
    client_id = input("🔑 Masukkan Client ID: ").strip()
    client_secret = input("🔒 Masukkan Client Secret: ").strip()

    if not client_id or not client_secret:
        raise ValueError("Client ID dan Client Secret tidak boleh kosong.")

    credentials = {
        "installed": {
            "client_id": client_id,
            "client_secret": client_secret,
            "redirect_uris": ["http://localhost"],
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token"
        }
    }

    # Simpan ke file client_{index}.json
    credentials_file = os.path.join(CREDENTIALS_DIR, f"client_{index}.json")
    with open(credentials_file, "w") as f:
        json.dump(credentials, f, indent=4)

    print(f"💾 Client credentials disimpan di: {credentials_file}")

    # Proses OAuth untuk mendapatkan token
    flow = InstalledAppFlow.from_client_config(credentials, SCOPES)
    creds = flow.run_local_server(port=0)

    # Simpan token ke file token_{index}.pickle
    token_file = os.path.join(CREDENTIALS_DIR, f"token_{index}.pickle")
    with open(token_file, "wb") as token:
        pickle.dump(creds, token)

    print(f"✅ Token berhasil didapatkan dan disimpan di: {token_file}")

def main():
    try:
        jumlah = int(input("🔢 Berapa banyak credentials yang ingin dimasukkan? "))

        for i in range(1, jumlah + 1):
            input_credentials(i)
            time.sleep(1)

        print("\n✅ Semua credentials dan token berhasil dibuat.")
    except Exception as e:
        print(f"\n❌ Terjadi kesalahan: {e}")

if __name__ == "__main__":
    main()
