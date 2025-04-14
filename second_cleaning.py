import re
import unicodedata
import csv
from colorama import init, Fore, Style
import time

# Initialize colorama
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
    print(Fore.YELLOW + " YouTube Spam Detector ".center(50, "="))
    print(Fore.MAGENTA + "By ARS - Version 1.0".center(50) + "\n")

def bersihkan_teks(teks):
    """Hapus konten non-spam sebelum deteksi"""
    if not isinstance(teks, str):
        return ""
    
    # Hapus mata uang (100rb, Rp 50.000)
    teks = re.sub(r'\b\d+\s*(?:rb|jt|juta|m|triliun)?\s*(?:rp|idr|usd)\b|\b(?:rp|idr|usd)\s*\d+\b', '', teks, flags=re.IGNORECASE)
    
    # Hapus format waktu (00:00, 12.30)
    teks = re.sub(r'\b\d{1,2}[:.]\d{2}\b', '', teks)
    
    # Hapus angka pangkat (orang², 10⁵)
    teks = re.sub(r'(\w)\²|\d+\⁺[\d⁺]*', '', teks)
    
    return teks

def is_font_aneh(word):
    """Deteksi karakter non-ASCII khusus (kecuali pangkat)"""
    for char in word:
        if ord(char) > 127 and not unicodedata.category(char).startswith('P') and char not in ('²', '³'):
            return True
    return False

def is_kata_angka_repetitif(word):
    """Deteksi pola seperti 'weton88'"""
    match = re.fullmatch(r'^[a-zA-Z]+((\d)\2{1,2})$', word)
    return bool(match)

def is_angka_kompleks(word):
    """Deteksi pola seperti 'JPT0GEL77'"""
    numbers = re.findall(r'\d+', word)
    return (len(numbers) >= 2 and 
            len(numbers[-1]) in {2,3} and 
            numbers[-1] == numbers[-1][0]*len(numbers[-1]))

def deteksi_spam(teks):
    """Deteksi spam setelah pembersihan teks"""
    teks_bersih = bersihkan_teks(teks)
    kata_kata = re.findall(r'[^\s\.,!?\'"\-]+', teks_bersih)
    
    spam_elements = []
    for kata in kata_kata:
        if is_font_aneh(kata):
            spam_elements.append(('font_aneh', kata))
        elif is_kata_angka_repetitif(kata):
            spam_elements.append(('kata_angka_repetitif', kata))
        elif is_angka_kompleks(kata):
            spam_elements.append(('angka_kompleks', kata))
    
    return ("spam", [k[1] for k in spam_elements]) if spam_elements else ("ham", [])

def show_progress(current, total, start_time):
    """Menampilkan progress bar dan estimasi waktu"""
    progress = current / total
    bar_length = 40
    filled = int(bar_length * progress)
    bar = Fore.GREEN + '█' * filled + Fore.YELLOW + '░' * (bar_length - filled)
    
    elapsed = time.time() - start_time
    eta = (elapsed / current) * (total - current) if current > 0 else 0
    
    print(f"\r{bar} {Fore.CYAN}{current}/{total} komentar "
          f"({progress:.1%}) | Waktu: {elapsed:.1f}s | ETA: {eta:.1f}s", end="")

def proses_file_csv(input_file, output_file):
    """Proses file CSV dengan sistem terbaru dan mengurutkan hasil"""
    print_header()
    
    try:
        # Baca file input
        print(Fore.YELLOW + f"\n📖 Membaca file input: {input_file}")
        with open(input_file, mode='r', encoding='utf-8') as f_in:
            reader = csv.DictReader(f_in)
            rows = list(reader)
            total_comments = len(rows)
            print(Fore.CYAN + f"🔍 Ditemukan {total_comments} komentar untuk diproses")
        
        # Proses deteksi spam
        print(Fore.YELLOW + "\n🛡️ Memulai deteksi spam...")
        start_time = time.time()
        
        data = []
        spam_count = 0
        
        for i, row in enumerate(rows, 1):
            show_progress(i, total_comments, start_time)
            comment_id = row.get('comment_id', '')
            teks = row.get('cleaned_comment', '')
            label, spam_detail = deteksi_spam(teks)
            
            if label == 'spam':
                spam_count += 1
            
            data.append([comment_id, label, teks, '|'.join(spam_detail)])
        
        # Urutkan data: Spam lebih dulu, lalu Ham
        data.sort(key=lambda x: 0 if x[1] == 'spam' else 1)
        
        # Hitung statistik
        ham_count = total_comments - spam_count
        spam_percentage = (spam_count / total_comments * 100) if total_comments > 0 else 0
        
        # Tampilkan ringkasan
        print(Fore.GREEN + "\n\n✅ Deteksi spam selesai!")
        print(Fore.CYAN + f"\n📊 Ringkasan:")
        print(Fore.WHITE + f"  • Total komentar: {total_comments}")
        print(Fore.RED + f"  • Komentar spam: {spam_count} ({spam_percentage:.1f}%)")
        print(Fore.GREEN + f"  • Komentar normal: {ham_count}")
        
        # Simpan hasil
        with open(output_file, mode='w', encoding='utf-8', newline='') as f_out:
            writer = csv.writer(f_out)
            writer.writerow(['comment_id', 'label', 'cleaned_comment', 'spam_detail'])
            writer.writerows(data)
        
        print(Fore.GREEN + f"\n💾 Hasil disimpan di: {output_file}")
    
    except FileNotFoundError:
        print(Fore.RED + f"\n❌ File tidak ditemukan: {input_file}")
    except Exception as e:
        print(Fore.RED + f"\n❌ Error: {str(e)}")

if __name__ == "__main__":
    proses_file_csv('cleaned_comments.csv', 'comments_labeled.csv')
