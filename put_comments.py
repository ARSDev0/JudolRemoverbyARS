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

# Initialize colorama
init(autoreset=True)

API_KEY_FILE = "credentials/valid_api_keys.json"
TOKEN_FILE = "credentials/token.pickle"
CLIENT_SECRET_FILE = "credentials/client_secret.json"
SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

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
                    print(Fore.YELLOW + f"🔑 Menggunakan API Key (tersedia {len(self.api_keys)} keys)")

        if not self.use_api_key:
            print(Fore.CYAN + "🔓 Menggunakan OAuth Authentication")
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
            print(Fore.RED + "❌ Tidak bisa rotasi, karena menggunakan OAuth.")
            sys.exit(1)
        self.api_index += 1
        if self.api_index >= len(self.api_keys):
            print(Fore.RED + "❌ Semua API key sudah habis.")
            sys.exit(1)
        print(Fore.YELLOW + f"🔁 Mengganti API key (key {self.api_index + 1}/{len(self.api_keys)})...")
        return self.get_service()

# ---------- Helper YouTube Functions ----------
def extract_video_id(url):
    match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11})", url)
    return match.group(1) if match else None

def extract_channel_handle(url):
    match = re.search(r"@([0-9A-Za-z_-]+)", url)
    return match.group(1) if match else None

def get_video_title(video_id, auth):
    youtube = auth.get_service()
    try:
        response = youtube.videos().list(
            part="snippet",
            id=video_id
        ).execute()
        if response.get("items"):
            return response["items"][0]["snippet"]["title"]
        return "Unknown Title"
    except HttpError:
        return "Unknown Title"

def get_channel_id_from_handle(handle, auth):
    youtube = auth.get_service()
    while True:
        try:
            response = youtube.channels().list(part="snippet,id", forHandle=handle).execute()
            if response.get("items"):
                channel_data = response["items"][0]
                print(Fore.CYAN + f"📺 Channel: {channel_data['snippet']['title']}")
                return channel_data["id"]
            else:
                print(Fore.RED + "❌ Channel tidak ditemukan.")
                return None
        except HttpError as e:
            print(Fore.RED + f"⚠️ Error ambil channel ID: {e}")
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
            print(Fore.RED + f"⚠️ Error ambil video: {e}")
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
            print(Fore.RED + f"⚠️ Error ambil reply: {e}")
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
            print(Fore.RED + f"⚠️ Error ambil komentar: {e}")
            if auth.use_api_key:
                youtube = auth.rotate_key()
            else:
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
    print(Fore.MAGENTA + "By ARS - Version 1.0".center(50) + "\n")

# ---------- Main Program ----------
if __name__ == "__main__":
    print_banner()
    auth = AuthManager()

    print(Fore.CYAN + "📌 Pilih mode:")
    print(Fore.GREEN + "1️⃣  Scan komentar dari satu video")
    print(Fore.GREEN + "2️⃣  Scan komentar dari semua video dalam channel")
    choice = input(Fore.YELLOW + "➡️  Masukkan pilihan (1/2): " + Style.RESET_ALL).strip()

    if choice == "1":
        video_url = input(Fore.CYAN + "🎥 Masukkan URL video YouTube: " + Style.RESET_ALL).strip()
        video_id = extract_video_id(video_url)
        if not video_id:
            print(Fore.RED + "❌ URL video tidak valid")
            sys.exit(1)
        
        video_title = get_video_title(video_id, auth)
        print(Fore.CYAN + f"📹 Video: {video_title}")
        
        comments = get_all_comments(video_id, auth, video_title)

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
        for idx, (vid, title) in enumerate(videos, 1):
            print(Fore.CYAN + f"\n📥 [{idx}/{len(videos)}] Memproses: {title}")
            comments.extend(get_all_comments(vid, auth, title))
            
    else:
        print(Fore.RED + "❌ Pilihan tidak valid")
        sys.exit(1)

    save_comments_to_csv(comments)
