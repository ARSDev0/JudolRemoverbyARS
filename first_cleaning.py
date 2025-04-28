import pandas as pd
import re
import emoji
import time
import unicodedata
from colorama import init, Fore, Style

# Inisialisasi colorama
init(autoreset=True)

def print_header():
    print(Fore.YELLOW + r"""
      ██╗██╗   ██╗██████╗  ██████╗ ██╗      ██████╗ ███████╗███╗   ███╗ ██████╗ ██╗   ██╗███████╗██████╗ 
      ██║██║   ██║██╔══██╗██╔═══██╗██║      ██╔══██╗██╔════╝████╗ ████║██╔═══██╗██║   ██║██╔════╝██╔══██╗
      ██║██║   ██║██║  ██║██║   ██║██║      ██████╔╝█████╗  ██╔████╔██║██║   ██║██║   ██║█████╗  ██████╔╝
 ██   ██║██║   ██║██║  ██║██║   ██║██║      ██╔══██╗██╔══╝  ██║╚██╔╝██║██║   ██║╚██╗ ██╔╝██╔══╝  ██╔══██╗
 ╚█████╔╝╚██████╔╝██████╔╝╚██████╔╝███████╗ ██║  ██║███████╗██║ ╚═╝ ██║╚██████╔╝ ╚████╔╝ ███████╗██║  ██║
  ╚════╝  ╚═════╝ ╚═════╝  ╚═════╝ ╚══════╝   ╚═╝  ╚═╝╚══════╝╚═╝     ╚═╝ ╚═════╝   ╚═══╝  ╚══════╝╚═╝  ╚═╝
    """ + Style.RESET_ALL)
    print(Fore.YELLOW + " YouTube Comment Cleaner ".center(50, "="))
    print(Fore.MAGENTA + "By ARS - Version 2.1".center(50) + "\n")

def is_language_blocked(char):
    try:
        name = unicodedata.name(char)
    except ValueError:
        return False
    blocked_scripts = [
        "ARABIC",
        "CJK UNIFIED",
        "HANGUL",
        "HIRAGANA",
        "KATAKANA",
        "THAI",
        "HEBREW",
        "DEVANAGARI"
    ]
    return any(script in name for script in blocked_scripts)

def contains_blocked_language(text):
    if not isinstance(text, str):
        return True
    return any(is_language_blocked(char) for char in text)

def merge_spaced_characters(text):
    """
    Gabungkan huruf yang terpisah spasi (misalnya: '𝐀 𝐌 𝐁 𝐈 𝐋' → '𝐀𝐌𝐁𝐈𝐋')
    """
    pattern = re.compile(r'(?:\b\w\s){2,20}\w\b')
    return pattern.sub(lambda match: match.group(0).replace(' ', ''), text)

def clean_text(text):
    if not isinstance(text, str) or contains_blocked_language(text):
        return None

    text = merge_spaced_characters(text)
    text = emoji.replace_emoji(text, replace='')
    text = re.sub(r'\s*@\S+', '', text)
    text = re.sub(r'[^\w\s]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()

    return text if text else None

def show_progress(current, total, start_time):
    progress = current / total
    bar_length = 40
    filled = int(bar_length * progress)
    bar = Fore.GREEN + '█' * filled + Fore.YELLOW + '░' * (bar_length - filled)

    elapsed = time.time() - start_time
    eta = (elapsed / current) * (total - current) if current > 0 else 0

    print(f"\r{bar} {Fore.CYAN}{current}/{total} komentar "
          f"({progress:.1%}) | Waktu: {elapsed:.1f}s | ETA: {eta:.1f}s", end="")

def main():
    print_header()

    input_file = 'comments.csv'
    output_file = 'cleaned_comments.csv'

    try:
        print(Fore.YELLOW + f"\n📖 Membaca file input: {input_file}")
        df = pd.read_csv(input_file)
        original_count = len(df)
        print(Fore.CYAN + f"🔍 Ditemukan {original_count} komentar")

        if 'comment_id' not in df.columns or 'comment' not in df.columns:
            raise ValueError("File CSV harus mengandung kolom 'comment_id' dan 'comment'")

        print(Fore.YELLOW + "\n🧹 Memulai pembersihan komentar...")
        start_time = time.time()

        cleaned_comments = []
        for i, row in df.iterrows():
            show_progress(i + 1, original_count, start_time)
            cleaned = clean_text(row['comment'])
            if cleaned is not None:
                cleaned_comments.append({'comment_id': row['comment_id'], 'cleaned_comment': cleaned})

        cleaned_df = pd.DataFrame(cleaned_comments)
        final_count = len(cleaned_df)

        removed_count = original_count - final_count
        removal_percentage = (removed_count / original_count * 100) if original_count > 0 else 0

        print(Fore.GREEN + "\n\n✅ Pembersihan selesai!")
        print(Fore.CYAN + f"\n📊 Ringkasan:")
        print(Fore.WHITE + f"  • Komentar awal: {original_count}")
        print(Fore.WHITE + f"  • Komentar akhir: {final_count}")
        print(Fore.RED + f"  • Komentar dihapus: {removed_count} ({removal_percentage:.1f}%)")

        cleaned_df.to_csv(output_file, index=False, encoding='utf-8')
        print(Fore.GREEN + f"\n💾 Hasil disimpan di: {output_file}")

    except FileNotFoundError:
        print(Fore.RED + f"\n❌ File tidak ditemukan: {input_file}")
    except Exception as e:
        print(Fore.RED + f"\n❌ Error: {str(e)}")

if __name__ == "__main__":
    main()
