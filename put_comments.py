import os
import re
import sys
import csv
import pickle
from concurrent.futures import ThreadPoolExecutor, as_completed
from colorama import init, Fore, Style
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Inisialisasi colorama
init(autoreset=True)

# Konstanta
SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"
CREDENTIALS_FOLDER = "credentials"

# ========== AUTH MANAGER (Multi Token Rotation) ==========
class AuthManager:
    def __init__(self):
        self.tokens = []
        self.token_index = 0
        self.load_tokens()

        if not self.tokens:
            print(Fore.RED + "❌ Tidak ada token ditemukan di folder 'credentials/'.")
            sys.exit(1)
        else:
            print(Fore.YELLOW + f"🔑 {len(self.tokens)} OAuth token berhasil dimuat.")

    def load_tokens(self):
        for filename in sorted(os.listdir(CREDENTIALS_FOLDER)):
            if filename.startswith("token_") and filename.endswith(".pickle"):
                path = os.path.join(CREDENTIALS_FOLDER, filename)
                with open(path, "rb") as token_file:
                    creds = pickle.load(token_file)
                    self.tokens.append(creds)

    def get_service(self):
        creds = self.tokens[self.token_index]
        return build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, credentials=creds)

    def rotate_token(self):
        self.token_index += 1
        if self.token_index >= len(self.tokens):
            print(Fore.RED + "❌ Semua token sudah habis, quota exhausted!")
            sys.exit(1)
        print(Fore.YELLOW + f"🔁 Ganti ke token berikutnya (Token {self.token_index + 1}/{len(self.tokens)})...")
        return self.get_service()

# ========== HELPER FUNCTION YOUTUBE ==========
def extract_video_id(url):
    match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11})", url)
    return match.group(1) if match else None

def extract_channel_handle(url):
    match = re.search(r"@([0-9A-Za-z_-]+)", url)
    return match.group(1) if match else None

def safe_api_call(api_func, auth, *args, **kwargs):
    while True:
        youtube = auth.get_service()
        try:
            return api_func(youtube, *args, **kwargs)
        except HttpError as e:
            if e.resp.status in [403, 429]:
                print(Fore.RED + f"⚠️ API Error {e.resp.status}, rotating token...")
                auth.rotate_token()
            else:
                print(Fore.RED + f"⚠️ Non-recoverable error: {e}")
                break
        except Exception as e:
            print(Fore.RED + f"⚠️ Unknown error: {e}")
            break
    return None

def get_video_title(video_id, auth):
    def api_call(youtube):
        response = youtube.videos().list(part="snippet", id=video_id).execute()
        if response.get("items"):
            return response["items"][0]["snippet"]["title"]
        return "Unknown Title"
    return safe_api_call(api_call, auth)

def get_channel_id_from_handle(handle, auth):
    def api_call(youtube):
        response = youtube.channels().list(part="snippet,id", forHandle=handle).execute()
        if response.get("items"):
            channel_data = response["items"][0]
            print(Fore.CYAN + f"📺 Channel: {channel_data['snippet']['title']}")
            return channel_data["id"]
        else:
            print(Fore.RED + "❌ Channel tidak ditemukan.")
            return None
    return safe_api_call(api_call, auth)

def get_videos_from_channel(channel_id, auth):
    videos = []
    next_page_token = None
    while True:
        def api_call(youtube):
            return youtube.search().list(
                part="snippet",
                channelId=channel_id,
                maxResults=50,
                type="video",
                order="date",
                pageToken=next_page_token
            ).execute()

        response = safe_api_call(api_call, auth)
        if not response:
            break

        for item in response.get("items", []):
            video_id = item["id"]["videoId"]
            video_title = item["snippet"]["title"]
            videos.append((video_id, video_title))

        next_page_token = response.get("nextPageToken")
        if not next_page_token:
            break

    return videos

def get_replies(video_id, parent_id, auth):
    replies = []
    next_page_token = None
    while True:
        def api_call(youtube):
            return youtube.comments().list(
                part="snippet",
                parentId=parent_id,
                textFormat="plainText",
                maxResults=100,
                pageToken=next_page_token
            ).execute()

        response = safe_api_call(api_call, auth)
        if not response:
            break

        for item in response.get("items", []):
            replies.append((video_id, item["id"], item["snippet"]["textDisplay"]))

        next_page_token = response.get("nextPageToken")
        if not next_page_token:
            break

    return replies

def get_all_comments(video_id, auth, fetch_replies=True, video_title=None):
    if not video_title:
        video_title = get_video_title(video_id, auth)
    
    comments = []
    next_page_token = None
    while True:
        def api_call(youtube):
            return youtube.commentThreads().list(
                part="snippet",
                videoId=video_id,
                textFormat="plainText",
                maxResults=100,
                pageToken=next_page_token
            ).execute()

        response = safe_api_call(api_call, auth)
        if not response:
            break

        for item in response.get("items", []):
            top_comment_id = item["id"]
            top_comment_text = item["snippet"]["topLevelComment"]["snippet"]["textDisplay"]
            comments.append((video_id, top_comment_id, top_comment_text))

            if fetch_replies and item["snippet"]["totalReplyCount"] > 0:
                replies = get_replies(video_id, top_comment_id, auth)
                comments.extend(replies)

        next_page_token = response.get("nextPageToken")
        if not next_page_token:
            break
    
    print(Fore.GREEN + f"✅ {len(comments)} komentar ditemukan di video: {video_title}")
    return comments

def save_comments_to_csv(comments, filename="comments.csv"):
    with open(filename, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["video_id", "comment_id", "comment"])
        writer.writerows(comments)
    print(Fore.GREEN + f"💾 Semua komentar disimpan ke {filename}")

def print_banner():
    print(Fore.YELLOW + r"""
      ██╗██╗   ██╗██████╗  ██████╗ ██╗      ██████╗ ███████╗███╗   ███╗ ██████╗ ██╗   ██╗███████╗██████╗ 
      ██║██║   ██║██╔══██╗██╔═══██╗██║      ██╔══██╗██╔════╝████╗ ████║██╔═══██╗██║   ██║██╔════╝██╔══██╗
      ██║██║   ██║██║  ██║██║   ██║██║      ██████╔╝█████╗  ██╔████╔██║██║   ██║██║   ██║█████╗  ██████╔╝
 ██   ██║██║   ██║██║  ██║██║   ██║██║      ██╔══██╗██╔══╝  ██║╚██╔╝██║██║   ██║╚██╗ ██╔╝██╔══╝  ██╔══██╗
 ╚█████╔╝╚██████╔╝██████╔╝╚██████╔╝███████╗ ██║  ██║███████╗██║ ╚═╝ ██║╚██████╔╝ ╚████╔╝ ███████╗██║  ██║
  ╚════╝  ╚═════╝ ╚═════╝  ╚═════╝ ╚══════╝   ╚═╝  ╚═╝╚══════╝╚═╝     ╚═╝ ╚═════╝   ╚═══╝  ╚══════╝╚═╝  ╚═╝
    """ + Style.RESET_ALL)
    print(Fore.CYAN + " YouTube Comment Scraper ".center(50, "="))
    print(Fore.MAGENTA + "By ARS - Version 3.0 (Threaded + Options)".center(50) + "\n")

# ========== MAIN ==========
if __name__ == "__main__":
    print_banner()
    auth = AuthManager()

    print(Fore.CYAN + "📌 Pilih mode:")
    print(Fore.GREEN + "1️⃣  Scan komentar dari satu video")
    print(Fore.GREEN + "2️⃣  Scan komentar dari semua video dalam channel")
    choice = input(Fore.YELLOW + "➡️  Masukkan pilihan (1/2): " + Style.RESET_ALL).strip()

    print(Fore.CYAN + "📌 Pilih tipe scraping:")
    print(Fore.GREEN + "1️⃣  Top Comment Only")
    print(Fore.GREEN + "2️⃣  Top Comment + Replies")
    replies_choice = input(Fore.YELLOW + "➡️  Masukkan pilihan (1/2): " + Style.RESET_ALL).strip()
    fetch_replies = replies_choice == "2"

    if choice == "1":
        video_url = input(Fore.CYAN + "🎥 Masukkan URL video YouTube: " + Style.RESET_ALL).strip()
        video_id = extract_video_id(video_url)
        if not video_id:
            print(Fore.RED + "❌ URL video tidak valid")
            sys.exit(1)
        
        video_title = get_video_title(video_id, auth)
        print(Fore.CYAN + f"📹 Video: {video_title}")
        
        comments = get_all_comments(video_id, auth, fetch_replies, video_title)

    elif choice == "2":
        channel_url = input(Fore.CYAN + "📺 Masukkan URL channel YouTube (gunakan format @namachannel): " + Style.RESET_ALL).strip()
        handle = extract_channel_handle(channel_url)
        if not handle:
            print(Fore.RED + "❌ URL harus mengandung @handle channel")
            sys.exit(1)
            
        channel_id = get_channel_id_from_handle(handle, auth)
        if not channel_id:
            sys.exit(1)
            
        videos = get_videos_from_channel(channel_id, auth)
        print(Fore.GREEN + f"\n📊 Total {len(videos)} video ditemukan")

        comments = []

        # Multi-threaded fetch
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = {
                executor.submit(get_all_comments, vid, auth, fetch_replies, title): (vid, title)
                for vid, title in videos
            }
            for future in as_completed(futures):
                try:
                    video_comments = future.result()
                    comments.extend(video_comments)
                except Exception as e:
                    print(Fore.RED + f"⚠️ Error fetching comments: {e}")
            
    else:
        print(Fore.RED + "❌ Pilihan tidak valid")
        sys.exit(1)

    save_comments_to_csv(comments)
