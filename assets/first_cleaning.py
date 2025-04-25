import pandas as pd
import re
import emoji
import time
import unicodedata
from colorama import init, Fore, Style
import os
import json
from judol_algoritm import GamblingAdDetector

# Inisialisasi colorama
init(autoreset=True)


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
    print()
    output_dir = 'results'
    input_file = os.path.join(output_dir, 'comments.csv')
    output_file = os.path.join(output_dir, 'cleaned_comments.csv')

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

    try:
        # Only print header if file exists
        if not os.path.exists(input_file):
            print(Fore.RED + f"File tidak ditemukan: {input_file}")
            print()
            return

        print(Fore.YELLOW + f"Membaca file input: {input_file}")
        df = pd.read_csv(input_file)
        original_count = len(df)
        print()
        print(Fore.CYAN + f"Ditemukan {original_count} komentar")
        print()

        if 'comment_id' not in df.columns or 'comment' not in df.columns:
            raise ValueError("File CSV harus mengandung kolom 'comment_id' dan 'comment'")

        print(Fore.YELLOW + "Memulai pembersihan komentar...")
        print()
        start_time = time.time()

        cleaned_comments = []
        gambling_count = 0
        for i, row in df.iterrows():
            show_progress(i + 1, original_count, start_time)
            # Prevent arrow key escape sequences in comment
            comment_val = row['comment']
            if isinstance(comment_val, str) and (
                comment_val in ["\x1b[A", "\x1b[B", "\x1b[C", "\x1b[D", "^[[A", "^[[B", "^[[C", "^[[D"] or
                "\x1b" in comment_val or comment_val.startswith("^[[")
            ):
                continue
            cleaned = clean_text(comment_val)
            if cleaned is not None:
                deobf = detector.deobfuscate_text(cleaned)
                is_gambling = detector.keyword_number_pattern.search(deobf) is not None
                if is_gambling:
                    gambling_count += 1
                cleaned_comments.append({
                    'comment_id': row['comment_id'],
                    'cleaned_comment': cleaned,
                    'gambling_ad': int(is_gambling)
                })

        cleaned_df = pd.DataFrame(cleaned_comments)
        final_count = len(cleaned_df)

        removed_count = original_count - final_count
        removal_percentage = (removed_count / original_count * 100) if original_count > 0 else 0

        print()
        # Ensure results directory exists
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        print(Fore.GREEN + f"Hasil disimpan di: {output_file}")
        print(Fore.GREEN + "="*60)
        print()

        cleaned_df.to_csv(output_file, index=False, encoding='utf-8')

    except FileNotFoundError:
        print(Fore.RED + f"File tidak ditemukan: {input_file}")
        print()
    except Exception as e:
        print()
        print(Fore.RED + f"Error: {str(e)}")
        print()

if __name__ == "__main__":
    main()
