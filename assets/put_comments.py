import os
import json
import re
import sys
import csv
import pickle
from colorama import init, Fore, Style
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from judol_algoritm import GamblingAdDetector

# Initialize colorama
init(autoreset=True)

API_KEY_FILE = "credentials/valid_api_keys.json"
TOKEN_FILE = "credentials/token.pickle"
CLIENT_SECRET_FILE = "credentials/client_secret.json"
SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"
VERSION = "3.0"
RESULTS_DIR = "results"

# ---------- Auth Manager ----------
class AuthManager:
    def __init__(self):
        self.use_api_key = False
        self.api_keys = []
        self.api_index = 0
        self.credentials = None

        if os.path.exists(API_KEY_FILE):
            with open(API_KEY_FILE, "r") as f:
                data = json.load(f)
                self.api_keys = data.get("valid_api_keys", [])
                if self.api_keys:
                    self.use_api_key = True
                    print(Fore.YELLOW + f"Menggunakan API Key (tersedia {len(self.api_keys)} keys)")

        if not self.use_api_key:
            print(Fore.CYAN + "Menggunakan OAuth Authentication")
            self.credentials = self.load_oauth_credentials()

    def load_oauth_credentials(self):
        creds = None
        if os.path.exists(TOKEN_FILE):
            with open(TOKEN_FILE, "rb") as token:
                creds = pickle.load(token)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(CLIENT_SECRET_FILE):
                    print(Fore.RED + "\nFile credentials/client_secret.json tidak ditemukan!")
                    print(Fore.YELLOW + "Silakan lakukan konfigurasi Auth terlebih dahulu di menu utama (main menu).")
                    sys.exit(1)
                flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
                creds = flow.run_local_server(port=0)
            with open(TOKEN_FILE, "wb") as token:
                pickle.dump(creds, token)
        return creds

    def get_service(self):
        if self.use_api_key:
            key = self.api_keys[self.api_index]
            return build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=key)
        else:
            return build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, credentials=self.credentials)

    def rotate_key(self):
        if not self.use_api_key:
            print(Fore.RED + "Tidak bisa rotasi, karena menggunakan OAuth.")
            sys.exit(1)
        self.api_index += 1
        if self.api_index >= len(self.api_keys):
            print(Fore.RED + "Semua API key sudah habis.")
            sys.exit(1)
        print(Fore.YELLOW + f"Mengganti API key (key {self.api_index + 1}/{len(self.api_keys)})...")
        return self.get_service()

# ---------- Helper YouTube Functions ----------
def extract_video_id(url):
    match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11})", url)
    return match.group(1) if match else None

def extract_channel_handle(url):
    match = re.search(r"@([0-9A-Za-z_-]+)", url)
    return match.group(1) if match else None

def get_video_title(video_id, auth=None, url=None):
    # Try to get title from HTML only, never use API
    if url:
        return extract_video_title_from_url(url) or "Unknown Title"
    return "Unknown Title"

def get_channel_id_from_handle(handle, auth):
    youtube = auth.get_service()
    while True:
        try:
            response = youtube.channels().list(part="snippet,id", forHandle=handle).execute()
            if response.get("items"):
                channel_data = response["items"][0]
                print(Fore.CYAN + f"Channel: {channel_data['snippet']['title']}")
                return channel_data["id"]
            else:
                print(Fore.RED + "Channel tidak ditemukan.")
                return None
        except HttpError as e:
            print(Fore.RED + f"Error ambil channel ID: {e}")
            if auth.use_api_key:
                youtube = auth.rotate_key()
            else:
                break

def get_videos_from_channel(channel_id, auth):
    youtube = auth.get_service()
    videos = []
    next_page_token = None
    while True:
        try:
            response = youtube.search().list(
                part="snippet",
                channelId=channel_id,
                maxResults=50,
                type="video",
                order="date",
                pageToken=next_page_token
            ).execute()
            
            for item in response.get("items", []):
                video_id = item["id"]["videoId"]
                video_title = item["snippet"]["title"]
                videos.append((video_id, video_title))
            
            next_page_token = response.get("nextPageToken")
            if not next_page_token:
                break
        except HttpError as e:
            print(Fore.RED + f"Error ambil video: {e}")
            if auth.use_api_key:
                youtube = auth.rotate_key()
            else:
                break
    return videos

def get_replies(auth, video_id, parent_id):
    youtube = auth.get_service()
    replies = []
    next_page_token = None
    while True:
        try:
            response = youtube.comments().list(
                part="snippet",
                parentId=parent_id,
                textFormat="plainText",
                maxResults=100,
                pageToken=next_page_token
            ).execute()
            for item in response.get("items", []):
                replies.append((video_id, item["id"], item["snippet"]["textDisplay"]))
            next_page_token = response.get("nextPageToken")
            if not next_page_token:
                break
        except HttpError as e:
            print(Fore.RED + f"Error ambil reply: {e}")
            if auth.use_api_key:
                youtube = auth.rotate_key()
            else:
                break
    return replies

def get_all_comments(video_id, auth, video_title=None):
    if not video_title:
        video_title = get_video_title(video_id, auth)
    
    youtube = auth.get_service()
    comments = []
    next_page_token = None
    while True:
        try:
            response = youtube.commentThreads().list(
                part="snippet",
                videoId=video_id,
                textFormat="plainText",
                maxResults=100,
                pageToken=next_page_token
            ).execute()

            for item in response.get("items", []):
                top_comment_id = item["id"]
                top_comment_text = item["snippet"]["topLevelComment"]["snippet"]["textDisplay"]
                comments.append((video_id, top_comment_id, top_comment_text))

                if item["snippet"]["totalReplyCount"] > 0:
                    replies = get_replies(auth, video_id, top_comment_id)
                    comments.extend(replies)

            next_page_token = response.get("nextPageToken")
            if not next_page_token:
                break
        except HttpError as e:
            print(Fore.RED + f"Error ambil komentar: {e}")
            if auth.use_api_key:
                youtube = auth.rotate_key()
            else:
                break
    
    print(Fore.GREEN + f"{len(comments)} komentar ditemukan di video: {video_title}")
    return comments

def save_comments_to_csv(comments, filename="comments.csv"):
    # Ensure results directory exists
    if not os.path.exists(RESULTS_DIR):
        os.makedirs(RESULTS_DIR)
    filepath = os.path.join(RESULTS_DIR, filename)

    # --- GamblingAdDetector integration ---
    # Load algorithm config from JSON
    algo_json_path = os.path.join(os.path.dirname(__file__), "json/nama_algoritma.json")
    with open(algo_json_path, "r", encoding="utf-8") as f:
        algo_config = json.load(f)

    detector = GamblingAdDetector()
    detector.keywords = set(algo_config.get("keywords", []))
    detector.suspicious_tlds = set(algo_config.get("suspicious_tlds", []))
    detector.name_patterns = algo_config.get("name_patterns", [])
    detector.suspicious_chars = set(algo_config.get("suspicious_chars", []))
    detector.common_numbers = set(algo_config.get("common_numbers", []))
    detector.obfuscation_chars = algo_config.get("obfuscation_chars", {})
    detector._compile_patterns()
    # --------------------------------------

    with open(filepath, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["video_id", "comment_id", "comment", "gambling_ad"])
        for row in comments:
            # row = (video_id, comment_id, comment)
            deobf = detector.deobfuscate_text(row[2])
            is_gambling = int(detector.keyword_number_pattern.search(deobf) is not None)
            writer.writerow([row[0], row[1], row[2], is_gambling])
    print()
    print(Fore.GREEN + "="*60)
    print(Fore.GREEN + f"Semua komentar berhasil disimpan ke: {filepath}")
    print(Fore.GREEN + "="*60)
    print()

def slugify(text):
    # Replace non-alphanumeric characters with hyphens, collapse multiple hyphens, strip
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_]+', '-', text)
    text = re.sub(r'-+', '-', text)
    return text.strip('-')

def print_banner():
    # Clear screen before showing banner
    os.system('cls' if os.name == 'nt' else 'clear')
    print()
    print(Fore.YELLOW + r"""
    .-----------------------------------------.
    |                                         |
    |       __ ___   ______            __     |
    |   __ / // _ \ /_  __/___  ___   / /___  |
    |  / // // , _/  / /  / _ \/ _ \ / /(_-<  |
    |  \___//_/|_|  /_/   \___/\___//_//___/  |
    |                                         |
    |  Judol Remover                          |
    |                                         |
    |  By ARS        Version {ver:<10}       |
    '-----------------------------------------'
    """.format(ver=VERSION) + Style.RESET_ALL)
    print()

def extract_video_title_from_url(url):
    """
    Try to extract the video title from the YouTube page HTML without using the API.
    Returns None if failed.
    """
    import requests
    from html import unescape
    try:
        video_id = extract_video_id(url)
        if not video_id:
            return None
        # Standard YouTube video URL
        page_url = f"https://www.youtube.com/watch?v={video_id}"
        resp = requests.get(page_url, timeout=10)
        if resp.status_code != 200:
            return None
        # Try to find <title>...</title>
        match = re.search(r'<title>(.*?)</title>', resp.text, re.IGNORECASE | re.DOTALL)
        if match:
            title = match.group(1)
            # Remove " - YouTube" suffix if present
            title = title.replace(" - YouTube", "").strip()
            return unescape(title)
        return None
    except Exception:
        return None

def return_to_main_menu():
    # Return to main.py main menu
    import subprocess
    import sys
    main_py = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "main.py"))
    print(Fore.CYAN + "\nKembali ke menu utama..." + Style.RESET_ALL)
    subprocess.call([sys.executable, main_py])
    sys.exit(0)

# ---------- Main Program ----------
if __name__ == "__main__":
    print_banner()
    auth = AuthManager()

    print(Fore.CYAN + "=== PILIH MODE ===")
    print()
    print(Fore.GREEN + "1. Scan komentar dari satu video")
    print(Fore.GREEN + "2. Scan komentar dari semua video dalam channel")
    print(Fore.YELLOW + "0. Kembali ke menu utama")
    print()
    while True:
        choice = input(Fore.YELLOW + "Masukkan pilihan (0/1/2): " + Style.RESET_ALL).strip()
        # Prevent arrow key escape sequences
        if choice in ["\x1b[A", "\x1b[B", "\x1b[C", "\x1b[D", "^[[A", "^[[B", "^[[C", "^[[D"]:
            print(Fore.RED + "Tombol arah tidak valid. Silakan masukkan 0, 1, atau 2.")
            continue
        if "\x1b" in choice or choice.startswith("^[["):
            print(Fore.RED + "Input tidak valid. Silakan masukkan 0, 1, atau 2.")
            continue
        if choice not in ["0", "1", "2"]:
            print(Fore.RED + "Pilihan tidak valid. Silakan masukkan 0, 1, atau 2.")
            continue
        break
    print()

    if choice == "1":
        print()
        while True:
            video_url = input(Fore.CYAN + "Masukkan URL video YouTube: " + Style.RESET_ALL).strip()
            if video_url in ["\x1b[A", "\x1b[B", "\x1b[C", "\x1b[D", "^[[A", "^[[B", "^[[C", "^[[D"]:
                print(Fore.RED + "Tombol arah tidak valid. Silakan masukkan URL video.")
                continue
            if "\x1b" in video_url or video_url.startswith("^[["):
                print(Fore.RED + "Input tidak valid. Silakan masukkan URL video.")
                continue
            break
        video_id = extract_video_id(video_url)
        if not video_id:
            print()
            print(Fore.RED + "URL video tidak valid")
            print()
            sys.exit(1)
        
        # Always get title from HTML, never use API
        video_title = get_video_title(video_id, url=video_url)
        print()
        print(Fore.CYAN + f"Video: {Fore.YELLOW}{video_title}")
        print()
        
        # The following will still fail if quota is exceeded, but title will always be correct
        comments = get_all_comments(video_id, auth, video_title)
        print()
        print(Fore.GREEN + f"Total komentar ditemukan: {len(comments)}")
        print()
        # Save with video-title based filename
        safe_title = slugify(video_title)
        filename = f"{safe_title}-comments.csv"
        save_comments_to_csv(comments, filename=filename)
        # Always also save as comments.csv for pipeline compatibility
        if filename != "comments.csv":
            save_comments_to_csv(comments, filename="comments.csv")
    elif choice == "2":
        print()
        while True:
            channel_url = input(Fore.CYAN + "Masukkan URL channel YouTube (gunakan format @namachannel): " + Style.RESET_ALL).strip()
            if channel_url in ["\x1b[A", "\x1b[B", "\x1b[C", "\x1b[D", "^[[A", "^[[B", "^[[C", "^[[D"]:
                print(Fore.RED + "Tombol arah tidak valid. Silakan masukkan URL channel.")
                continue
            if "\x1b" in channel_url or channel_url.startswith("^[["):
                print(Fore.RED + "Input tidak valid. Silakan masukkan URL channel.")
                continue
            break
        handle = extract_channel_handle(channel_url)
        if not handle:
            print()
            print(Fore.RED + "URL harus mengandung @handle channel")
            print()
            sys.exit(1)
            
        channel_id = get_channel_id_from_handle(handle, auth)
        if not channel_id:
            print()
            sys.exit(1)
            
        videos = get_videos_from_channel(channel_id, auth)
        print()
        print(Fore.GREEN + f"Total {len(videos)} video ditemukan")
        print()
        
        comments = []
        for idx, (vid, title) in enumerate(videos, 1):
            print()
            print(Fore.CYAN + f"[{idx}/{len(videos)}] Memproses: {title}")
            print()
            comments.extend(get_all_comments(vid, auth, title))
        print()
        print(Fore.GREEN + f"Total komentar ditemukan: {len(comments)}")
        print()
        # Save with default filename for all videos
        save_comments_to_csv(comments, filename="comments.csv")
    elif choice == "0":
        return_to_main_menu()
    else:
        print()
        print(Fore.RED + "Pilihan tidak valid")
        print()
        sys.exit(1)

    print(Fore.CYAN + "=== Proses selesai! ===")
    print()
