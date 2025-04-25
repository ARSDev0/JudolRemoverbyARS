import csv
import os
import pickle
import re
from colorama import init, Fore, Style
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# Initialize colorama
init(autoreset=True)

# Direktori kredensial
CREDENTIALS_DIR = "credentials"
TOKEN_PICKLE = os.path.join(CREDENTIALS_DIR, "token.pickle")
CLIENT_SECRET_FILE = os.path.join(CREDENTIALS_DIR, "client_secret.json")

# Scope untuk mengakses komentar YouTube
SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]

# Variabel global untuk YouTube API service
youtube = None

def get_youtube_service():
    """Menghubungkan ke YouTube API dengan OAuth2."""
    global youtube
    creds = None
    
    if os.path.exists(TOKEN_PICKLE):
        with open(TOKEN_PICKLE, "rb") as token:
            creds = pickle.load(token)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print()
            print(Fore.YELLOW + "Memperbarui token akses...")
            print()
            creds.refresh(Request())
        else:
            print()
            print(Fore.YELLOW + "Membuka browser untuk autentikasi OAuth...")
            print()
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        
        with open(TOKEN_PICKLE, "wb") as token:
            pickle.dump(creds, token)
    
    youtube = build("youtube", "v3", credentials=creds)
    print()
    print(Fore.GREEN + "Berhasil terhubung ke YouTube API")
    print()

def hold_comment(comment_id):
    """Menahan komentar agar tidak tampil secara publik."""
    global youtube
    try:
        request = youtube.comments().setModerationStatus(
            id=comment_id,
            moderationStatus="heldForReview"
        )
        request.execute()
        return True
    except Exception as e:
        print()
        print(Fore.RED + f"Error saat menahan komentar {comment_id}: {str(e)}")
        print()
        return False

def display_comment(comment, index):
    """Menampilkan komentar dengan format yang rapi"""
    print()
    print(Fore.CYAN + f"{index}. ID Komentar: {comment['comment_id']}")
    print()
    print(Fore.YELLOW + f"\"{comment['cleaned_comment']}\"")
    print()
    print(Fore.RED + "Ditemukan pola spam: " + Fore.WHITE + comment['spam_detail'].replace("|", ", "))
    print()

def review_spam_comments(spam_comments):
    """Memungkinkan user untuk meninjau komentar sebelum ditahan."""
    print()
    print(Fore.CYAN + "="*60)
    print(Fore.CYAN + " " * 15 + "DAFTAR KOMENTAR SPAM")
    print(Fore.CYAN + " " * 14 + "(Review sebelum ditahan)")
    print(Fore.CYAN + "="*60)
    print()

    for i, comment in enumerate(spam_comments, 1):
        display_comment(comment, i)

    print(Fore.MAGENTA + "-"*60)
    print(Fore.MAGENTA + "INSTRUKSI:")
    print(Fore.WHITE + "  • Masukkan " + Fore.YELLOW + "nomor komentar" + Fore.WHITE + " yang ingin " + Fore.RED + "DIKECUALIKAN")
    print(Fore.WHITE + "  • Contoh: " + Fore.GREEN + "1,3,5" + Fore.WHITE + " → akan " + Fore.RED + "DILEWATI")
    print(Fore.WHITE + "  • Tekan " + Fore.GREEN + "ENTER" + Fore.WHITE + " jika " + Fore.YELLOW + "semua ingin ditahan")
    print(Fore.MAGENTA + "-"*60)
    print()
    
    # Prevent arrow key escape sequences
    while True:
        input_skip = input(Fore.CYAN + "   Pilihan Anda: " + Style.RESET_ALL).strip()
        if input_skip in ["\x1b[A", "\x1b[B", "\x1b[C", "\x1b[D", "^[[A", "^[[B", "^[[C", "^[[D"]:
            print(Fore.RED + "Tombol arah tidak valid. Silakan masukkan nomor komentar atau tekan ENTER.")
            continue
        if "\x1b" in input_skip or input_skip.startswith("^[["):
            print(Fore.RED + "Input tidak valid. Silakan masukkan nomor komentar atau tekan ENTER.")
            continue
        break

    skip_indexes = set()
    if input_skip:
        try:
            skip_indexes = {int(idx) - 1 for idx in input_skip.split(",") if idx.strip().isdigit()}
        except ValueError:
            print()
            print(Fore.RED + "Format input salah! Semua komentar akan ditahan.")
            print()
    
    return [comment for i, comment in enumerate(spam_comments) if i not in skip_indexes]

def process_spam_comments(csv_filename):
    print()
    results_dir = "results"
    csv_path = os.path.join(results_dir, csv_filename)
    if not os.path.exists(csv_path):
        print(Fore.RED + f"File tidak ditemukan: {csv_path}")
        print()
        return
    
    try:
        print(Fore.YELLOW + f"Membaca file: {csv_path}")
        print()
        
        # Read all comments from CSV
        with open(csv_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            spam_comments = [row for row in reader if row['label'] == 'spam']
        
        if not spam_comments:
            print()
            print(Fore.GREEN + "Tidak ada komentar spam untuk ditahan.")
            print()
            return
        
        print(Fore.CYAN + f"Ditemukan {len(spam_comments)} komentar spam")
        print()

        # Continue with normal spam processing
        get_youtube_service()
        
        # Review spam comments
        confirmed_spam = review_spam_comments(spam_comments)

        if not confirmed_spam:
            print()
            print(Fore.YELLOW + "Semua komentar telah dikecualikan. Tidak ada yang ditahan.")
            print()
            return

        print()
        print(Fore.YELLOW + "="*60)
        print(Fore.YELLOW + " " * 18 + "MENAHAN KOMENTAR SPAM")
        print(Fore.YELLOW + "="*60)
        print()
        
        success_count = 0
        for comment in confirmed_spam:
            comment_id = comment['comment_id']
            if hold_comment(comment_id):
                print(Fore.GREEN + f"Berhasil menahan komentar {comment_id}")
                print()
                success_count += 1
            else:
                print(Fore.RED + f"Gagal menahan komentar {comment_id}")
                print(Fore.YELLOW + "ini hanya berfungsi di channel anda sendiri bukan di video orang lain!")
                print()
        
        print()
        print(Fore.CYAN + "="*60)
        print(Fore.CYAN + "HASIL AKHIR:")
        print(Fore.WHITE + f"   • Total komentar spam: {len(spam_comments)}")
        print(Fore.GREEN + f"   • Berhasil ditahan: {success_count}")
        print(Fore.RED + f"   • Gagal ditahan: {len(confirmed_spam) - success_count}")
        print(Fore.CYAN + "="*60)
        print()
        print(Fore.YELLOW + "Proses moderasi selesai!" + Style.RESET_ALL)
        print()
    
    except FileNotFoundError:
        print(Fore.RED + f"File tidak ditemukan: {csv_path}")
        print()
    except Exception as e:
        print()
        print(Fore.RED + f"Error: {str(e)}")
        print()

if __name__ == "__main__":
    process_spam_comments("comments_labeled.csv")