import os
import json
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from googleapiclient.errors import HttpError

# Direktori kredensial
CREDENTIALS_DIR = "credentials"
os.makedirs(CREDENTIALS_DIR, exist_ok=True)

SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl']
CREDENTIALS_FILE = os.path.join(CREDENTIALS_DIR, "client_secret.json")
TOKEN_FILE = os.path.join(CREDENTIALS_DIR, "token.pickle")
API_KEYS_FILE = os.path.join(CREDENTIALS_DIR, "valid_api_keys.json")

def save_credentials_to_json(client_id, client_secret):
    credentials_data = {
        "installed": {
            "client_id": client_id,
            "client_secret": client_secret,
            "redirect_uris": ["http://localhost"],
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token"
        }
    }
    with open(CREDENTIALS_FILE, 'w') as json_file:
        json.dump(credentials_data, json_file, indent=4)

def login_with_oauth():
    flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
    creds = flow.run_local_server(port=0)
    with open(TOKEN_FILE, 'wb') as token_file:
        pickle.dump(creds, token_file)
    return creds

def test_youtube_api_key(api_key):
    try:
        youtube = build('youtube', 'v3', developerKey=api_key)
        request = youtube.videos().list(part="snippet", chart="mostPopular", maxResults=1)
        request.execute()
        return True
    except HttpError as e:
        if e.resp.status == 403:
            return False
        raise

def validate_and_save_api_keys(api_keys):
    valid_keys = []
    invalid_keys = []
    
    print("\nMemvalidasi API Keys...")
    for key in api_keys:
        if test_youtube_api_key(key):
            valid_keys.append(key)
            print(f"✅ API Key: {key[:5]}...{key[-5:]} VALID")
        else:
            invalid_keys.append(key)
            print(f"❌ API Key: {key[:5]}...{key[-5:]} TIDAK VALID")
    
    if valid_keys:
        with open(API_KEYS_FILE, 'w') as json_file:
            json.dump({"api_keys": valid_keys}, json_file, indent=4)
        print(f"\n{len(valid_keys)} API Key yang valid telah disimpan di {API_KEYS_FILE}")
    
    if invalid_keys:
        print(f"\n{len(invalid_keys)} API Key tidak valid dan tidak disimpan")
    
    return valid_keys

def get_user_input():
    print("=== YouTube API Authentication ===")
    print("\nPilih metode autentikasi:")
    print("1. OAuth saja")
    print("2. OAuth + API Keys")
    choice = input("Masukkan pilihan (1/2): ")
    
    client_id = input("\nMasukkan Client ID: ")
    client_secret = input("Masukkan Client Secret: ")
    
    api_keys = []
    if choice == '2':
        print("\nMasukkan YouTube API Keys (pisahkan dengan koma jika lebih dari satu):")
        keys_input = input("API Keys: ").strip()
        api_keys = [key.strip() for key in keys_input.split(',') if key.strip()]
    
    return client_id, client_secret, api_keys

def authenticate_with_oauth():
    try:
        print("\nMembuka browser untuk autentikasi OAuth...")
        creds = login_with_oauth()
        print("\nBerhasil login! Mengambil data channel...")
        youtube = build('youtube', 'v3', credentials=creds)
        request = youtube.channels().list(part="snippet,statistics", mine=True)
        response = request.execute()
        return response
    except Exception as e:
        raise Exception(f"Gagal autentikasi OAuth: {str(e)}")

def main():
    try:
        client_id, client_secret, api_keys = get_user_input()
        
        # Simpan credentials OAuth
        save_credentials_to_json(client_id, client_secret)
        print(f"\nCredentials OAuth telah disimpan di {CREDENTIALS_FILE}")
        
        # Validasi dan simpan API Keys jika ada
        valid_api_keys = []
        if api_keys:
            valid_api_keys = validate_and_save_api_keys(api_keys)
        
        # Autentikasi dengan OAuth
        channel_info = authenticate_with_oauth()
        
        # Hasil akhir
        result = {
            "status": "success",
            "oauth_credentials": CREDENTIALS_FILE,
            "channel_info": channel_info,
            "valid_api_keys": valid_api_keys if valid_api_keys else None
        }
        
        print("\n=== Hasil Autentikasi ===")
        print(json.dumps(result, indent=2))
        
    except Exception as e:
        error_result = {
            "status": "error",
            "message": str(e)
        }
        print("\n=== Error ===")
        print(json.dumps(error_result, indent=2))

if __name__ == "__main__":
    main()