import re
import unicodedata
import csv
from colorama import init, Fore, Style
import time
import os
import json
from judol_algoritm import GamblingAdDetector

# Initialize colorama
init(autoreset=True)


def bersihkan_teks(teks):
    if not isinstance(teks, str):
        return ""
    
    teks = re.sub(r'\b\d+\s*(?:rb|jt|juta|m|triliun)?\s*(?:rp|idr|usd)\b|\b(?:rp|idr|usd)\s*\d+\b', '', teks, flags=re.IGNORECASE)
    teks = re.sub(r'\b\d{1,2}[:.]\d{2}\b', '', teks)
    teks = re.sub(r'(\w)\²|\d+\⁺[\d⁺]*', '', teks)
    return teks

def is_font_aneh(word):
    """Deteksi karakter aneh termasuk mathematical alphanumerics"""
    for char in word:
        code_point = ord(char)
        if (
            code_point > 127 and
            not unicodedata.category(char).startswith('P') and
            char not in ('²', '³')
        ):
            return True
        if 0x1D400 <= code_point <= 0x1D7FF:  # Mathematical Alphanumeric Symbols
            return True
    return False

def is_kata_angka_repetitif(word):
    return bool(re.fullmatch(r'^[a-zA-Z]+((\d)\2{1,2})$', word))

def is_angka_kompleks(word):
    numbers = re.findall(r'\d+', word)
    return (len(numbers) >= 2 and len(numbers[-1]) in {2, 3} and numbers[-1] == numbers[-1][0]*len(numbers[-1]))

def is_angka_repetitif_setelah_spasi(word):
    if re.fullmatch(r'^\d{3,}$', word) and len(set(word)) == 1:
        return True
    groups = word.split()
    if len(groups) >= 2 and all(g == groups[0] for g in groups):
        return True
    return False

def deteksi_spam(teks):
    teks_bersih = bersihkan_teks(teks)
    kata_kata = re.findall(r'[^\s\.,!?\'"\-]+', teks_bersih)
    
    spam_elements = []
    # Use new gambling ad detector
    deobf_teks = detector.deobfuscate_text(teks)
    gambling_found = False
    if detector.keyword_number_pattern.search(deobf_teks):
        spam_elements.append(('gambling_ad', teks))
        gambling_found = True
    # Broaden gambling detection: suspicious name patterns
    if detector.name_pattern.search(deobf_teks):
        spam_elements.append(('gambling_ad', teks))
        gambling_found = True
    for kata in kata_kata:
        if is_font_aneh(kata):
            spam_elements.append(('font_aneh', kata))
        elif is_kata_angka_repetitif(kata):
            spam_elements.append(('kata_angka_repetitif', kata))
        elif is_angka_kompleks(kata):
            spam_elements.append(('angka_kompleks', kata))
        elif is_angka_repetitif_setelah_spasi(kata):
            spam_elements.append(('angka_repetitif', kata))
    
    return ("spam", [k[1] for k in spam_elements]) if spam_elements else ("ham", [])

def show_progress(current, total, start_time):
    bar_length = 40
    progress = current / total
    filled = int(bar_length * progress)
    bar = Fore.GREEN + '█' * filled + Fore.YELLOW + '░' * (bar_length - filled)
    elapsed = time.time() - start_time
    eta = (elapsed / current * (total - current)) if current else 0
    print(f"\r{bar} {Fore.CYAN}{current}/{total} ({progress:.1%}) | ETA: {eta:.1f}s", end='')

def proses_file_csv(input_file, output_file):
    print()
    output_dir = 'results'
    output_file_path = os.path.join(output_dir, output_file)
    input_file_path = os.path.join(output_dir, input_file)
    try:
        # Only print header if file exists
        if not os.path.exists(input_file_path):
            print(Fore.RED + f"File tidak ditemukan: {input_file_path}")
            print()
            return

        with open(input_file_path, mode='r', encoding='utf-8') as f_in:
            reader = csv.DictReader(f_in)
            rows = list(reader)
            total_comments = len(rows)
            print(Fore.CYAN + f"{total_comments} komentar akan diproses...")
            print()

        data = []
        spam_count = 0
        start_time = time.time()

        for i, row in enumerate(rows, 1):
            show_progress(i, total_comments, start_time)
            comment_id = row.get('comment_id', '')
            teks = row.get('cleaned_comment', '')
            # Prevent arrow key escape sequences in comment
            if isinstance(teks, str) and (
                teks in ["\x1b[A", "\x1b[B", "\x1b[C", "\x1b[D", "^[[A", "^[[B", "^[[C", "^[[D"] or
                "\x1b" in teks or teks.startswith("^[[")
            ):
                continue
            label, spam_detail = deteksi_spam(teks)
            if label == 'spam':
                spam_count += 1
            data.append([comment_id, label, teks, '|'.join(spam_detail)])

        data.sort(key=lambda x: 0 if x[1] == 'spam' else 1)

        # Ensure results directory exists
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        with open(output_file_path, mode='w', encoding='utf-8', newline='') as f_out:
            writer = csv.writer(f_out)
            writer.writerow(['comment_id', 'label', 'cleaned_comment', 'spam_detail'])
            writer.writerows(data)

        ham_count = total_comments - spam_count
        print()
        print(Fore.GREEN + "="*60)
        print(Fore.GREEN + f"Selesai! {spam_count} spam terdeteksi dari {total_comments} komentar.")
        print(Fore.GREEN + f"Hasil disimpan di: {output_file_path}")
        print(Fore.GREEN + "="*60)
        print()

    except FileNotFoundError:
        print(Fore.RED + f"File tidak ditemukan: {input_file_path}")
        print()
    except Exception as e:
        print()
        print(Fore.RED + f"Error: {str(e)}")
        print()

# Load algorithm config from JSON and initialize detector globally
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

if __name__ == "__main__":
    proses_file_csv("cleaned_comments.csv", "comments_labeled.csv")
