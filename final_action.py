import csv
import os
import pickle
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

def print_header():
    print(Fore.YELLOW + r"""
      ██╗██╗   ██╗██████╗  ██████╗ ██╗      ██████╗ ███████╗███╗   ███╗ ██████╗ ██╗   ██╗███████╗██████╗ 
      ██║██║   ██║██╔══██╗██╔═══██╗██║      ██╔══██╗██╔════╝████╗ ████║██╔═══██╗██║   ██║██╔════╝██╔══██╗
      ██║██║   ██║██║  ██║██║   ██║██║      ██████╔╝█████╗  ██╔████╔██║██║   ██║██║   ██║█████╗  ██████╔╝
 ██   ██║██║   ██║██║  ██║██║   ██║██║      ██╔══██╗██╔══╝  ██║╚██╔╝██║██║   ██║╚██╗ ██╔╝██╔══╝  ██╔══██╗
 ╚█████╔╝╚██████╔╝██████╔╝╚██████╔╝███████╗ ██║  ██║███████╗██║ ╚═╝ ██║╚██████╔╝ ╚████╔╝ ███████╗██║  ██║
  ╚════╝  ╚═════╝ ╚═════╝  ╚═════╝ ╚══════╝   ╚═╝  ╚═╝╚══════╝╚═╝     ╚═╝ ╚═════╝   ╚═══╝  ╚══════╝╚═╝  ╚═╝
    """ + Style.RESET_ALL)
    print(Fore.YELLOW + " YouTube Spam Comment Moderator ".center(50, "="))
    print(Fore.MAGENTA + "By ARS - Version 1.0".center(50) + "\n")

def get_youtube_service():
    """Menghubungkan ke YouTube API dengan OAuth2."""
    global youtube
    creds = None
    
    if os.path.exists(TOKEN_PICKLE):
        with open(TOKEN_PICKLE, "rb") as token:
            creds = pickle.load(token)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print(Fore.YELLOW + "🔁 Memperbarui token akses...")
            creds.refresh(Request())
        else:
            print(Fore.YELLOW + "🔑 Membuka browser untuk autentikasi OAuth...")
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        
        with open(TOKEN_PICKLE, "wb") as token:
            pickle.dump(creds, token)
    
    youtube = build("youtube", "v3", credentials=creds)
    print(Fore.GREEN + "✅ Berhasil terhubung ke YouTube API")

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
        print(Fore.RED + f"⚠️ Error saat menahan komentar {comment_id}: {str(e)}")
        return False

def display_comment(comment, index):
    """Menampilkan komentar dengan format yang rapi"""
    print(Fore.CYAN + f"\n📌 {index}. ID Komentar: {comment['comment_id']}")
    print(Fore.WHITE + "─" * 50)
    print(Fore.YELLOW + f"\"{comment['cleaned_comment']}\"")
    print(Fore.WHITE + "─" * 50)
    print(Fore.RED + "🚩 Ditemukan pola spam: " + Fore.WHITE + comment['spam_detail'].replace("|", ", "))

def review_spam_comments(spam_comments):
    """Memungkinkan user untuk meninjau komentar sebelum ditahan."""
    print(Fore.YELLOW + "\n🔍 " + Fore.CYAN + "DAFTAR KOMENTAR SPAM".center(50))
    print(Fore.YELLOW + "   (Review sebelum ditahan)".center(50) + "\n")
    
    for i, comment in enumerate(spam_comments, 1):
        display_comment(comment, i)
    
    print(Fore.MAGENTA + "\n✏️  INSTRUKSI:")
    print(Fore.WHITE + "   Masukkan nomor komentar yang ingin DIKECUALIKAN")
    print(Fore.WHITE + "   Contoh: " + Fore.GREEN + "1,3,5" + Fore.WHITE + " → akan DILEWATI")
    print(Fore.WHITE + "   Tekan " + Fore.GREEN + "ENTER" + Fore.WHITE + " jika semua ingin ditahan\n")
    
    input_skip = input(Fore.CYAN + "   Pilihan Anda: " + Style.RESET_ALL).strip()
    
    # Proses input user
    skip_indexes = set()
    if input_skip:
        try:
            skip_indexes = {int(idx) - 1 for idx in input_skip.split(",") if idx.strip().isdigit()}
        except ValueError:
            print(Fore.RED + "⚠️ Format input salah! Semua komentar akan ditahan.")
    
    return [comment for i, comment in enumerate(spam_comments) if i not in skip_indexes]

def process_spam_comments(csv_filename):
    """Menahan komentar spam setelah dikonfirmasi oleh user."""
    print_header()
    
    try:
        # Baca file CSV
        print(Fore.YELLOW + f"\n📖 Membaca file: {csv_filename}")
        with open(csv_filename, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            spam_comments = [row for row in reader if row['label'] == 'spam']
        
        if not spam_comments:
            print(Fore.GREEN + "✅ Tidak ada komentar spam untuk ditahan.")
            return
        
        print(Fore.CYAN + f"\n🔍 Ditemukan {len(spam_comments)} komentar spam")
        
        # Koneksi ke YouTube API
        get_youtube_service()
        
        # User melakukan review sebelum penghapusan
        confirmed_spam = review_spam_comments(spam_comments)

        if not confirmed_spam:
            print(Fore.YELLOW + "\n🚫 Semua komentar telah dikecualikan. Tidak ada yang ditahan.")
            return

        print(Fore.YELLOW + "\n🚀 " + Fore.CYAN + "MENAHAN KOMENTAR SPAM".center(50) + "\n")
        
        success_count = 0
        for comment in confirmed_spam:
            comment_id = comment['comment_id']
            if hold_comment(comment_id):
                print(Fore.GREEN + f"   ✅ Berhasil menahan komentar {comment_id}")
                success_count += 1
            else:
                print(Fore.RED + f"   ⚠️ Gagal menahan komentar {comment_id}")
        
        print(Fore.CYAN + f"\n📊 HASIL AKHIR:")
        print(Fore.WHITE + f"   • Total komentar spam: {len(spam_comments)}")
        print(Fore.GREEN + f"   • Berhasil ditahan: {success_count}")
        print(Fore.RED + f"   • Gagal ditahan: {len(confirmed_spam) - success_count}")
        print(Fore.YELLOW + f"\n🎉 Proses moderasi selesai!" + Style.RESET_ALL)
    
    except FileNotFoundError:
        print(Fore.RED + f"\n❌ File tidak ditemukan: {csv_filename}")
    except Exception as e:
        print(Fore.RED + f"\n❌ Error: {str(e)}")

if __name__ == "__main__":
    process_spam_comments("comments_labeled.csv")
