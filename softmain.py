import os
import sys
import subprocess
import importlib.util

# Step 1: Install required packages if not installed
def install_if_needed():
    packages = {
        "google-api-python-client": "googleapiclient",
        "google-auth-oauthlib": "google_auth_oauthlib",
        "google-auth-httplib2": "google_auth_httplib2",
        "emoji": "emoji",
        "colorama": "colorama"
    }

    for pip_name, module_name in packages.items():
        if importlib.util.find_spec(module_name) is None:
            print(f"[INFO] Menginstall: {pip_name}...")
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", pip_name])
            except subprocess.CalledProcessError:
                print(f"[ERROR] Gagal menginstall {pip_name}. Silakan install manual jika perlu.")
    
    # Install pandas with error handling
    try:
        print(f"[INFO] Menginstall: pandas (versi terbaru)...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pandas"])
    except subprocess.CalledProcessError:
        print(f"[ERROR] Gagal menginstall pandas versi terbaru.")
        print(f"[INFO] Apakah Anda ingin mencoba menginstall pandas versi lama yang kompatibel? (y/n)")
        if input().strip().lower() == 'y':
            try:
                print(f"[INFO] Menginstall: pandas versi lama...")
                subprocess.check_call([sys.executable, "-m", "pip", "install", "pandas==1.1.5"])
                print(f"[INFO] Pandas versi lama berhasil diinstal.")
            except subprocess.CalledProcessError:
                print(f"[ERROR] Gagal menginstall pandas versi lama.")
        else:
            print(f"[INFO] Pandas tidak diinstal, proses dapat terganggu tanpa pandas.")

install_if_needed()

# Step 2: Import after install
from colorama import init, Fore, Style
import time

# Initialize colorama
init(autoreset=True)

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def show_banner():
    clear_screen()
    print(Fore.YELLOW + r"""
      ██╗██╗   ██╗██████╗  ██████╗ ██╗      ██████╗ ███████╗███╗   ███╗ ██████╗ ██╗   ██╗███████╗██████╗ 
      ██║██║   ██║██╔══██╗██╔═══██╗██║      ██╔══██╗██╔════╝████╗ ████║██╔═══██╗██║   ██║██╔════╝██╔══██╗
      ██║██║   ██║██║  ██║██║   ██║██║      ██████╔╝█████╗  ██╔████╔██║██║   ██║██║   ██║█████╗  ██████╔╝
 ██   ██║██║   ██║██║  ██║██║   ██║██║      ██╔══██╗██╔══╝  ██║╚██╔╝██║██║   ██║╚██╗ ██╔╝██╔══╝  ██╔══██╗
 ╚█████╔╝╚██████╔╝██████╔╝╚██████╔╝███████╗ ██║  ██║███████╗██║ ╚═╝ ██║╚██████╔╝ ╚████╔╝ ███████╗██║  ██║
  ╚════╝  ╚═════╝ ╚═════╝  ╚═════╝ ╚══════╝   ╚═╝  ╚═╝╚══════╝╚═╝     ╚═╝ ╚═════╝   ╚═══╝  ╚══════╝╚═╝  ╚═╝
    """ + Style.RESET_ALL)
    print(Fore.CYAN + " " * 15 + "by ARS - Version 1.0".center(40))
    print(Fore.MAGENTA + "=" * 60 + Style.RESET_ALL)

def show_menu():
    print(Fore.YELLOW + "\n📋" + Fore.CYAN + " MAIN MENU ".center(58, '─') + Style.RESET_ALL)
    print(Fore.GREEN + "1️⃣  " + Fore.WHITE + "Jalankan Autentikasi YouTube")
    print(Fore.GREEN + "2️⃣  " + Fore.WHITE + "Hapus File Kredensial")
    print(Fore.GREEN + "3️⃣  " + Fore.WHITE + "Jalankan Proses Moderasi Komentar")
    print(Fore.RED + "0️⃣  " + Fore.WHITE + "Keluar dari Program")
    print(Fore.MAGENTA + "─" * 60 + Style.RESET_ALL)

def run_autentikasi():
    print(Fore.YELLOW + "\n🚀 Memulai proses autentikasi YouTube..." + Style.RESET_ALL)
    time.sleep(1)
    os.system("python autentikasi.py")
    return_to_menu()

def run_delete_credentials():
    print(Fore.YELLOW + "\n🗑️  Memulai penghapusan kredensial..." + Style.RESET_ALL)
    time.sleep(1)
    os.system("python auth_delete.py")
    return_to_menu()

def run_moderasi():
    print(Fore.YELLOW + "\n🛡️  Memulai proses moderasi komentar..." + Style.RESET_ALL)
    time.sleep(1)
    
    scripts = [
        ("put_comments.py", "1/4 Mengambil komentar dari YouTube..."),
        ("first_cleaning.py", "2/4 Proses pembersihan pertama..."),
        ("second_cleaning.py", "3/4 Proses pembersihan kedua..."),
        ("final_action.py", "4/4 Tindakan final moderasi...")
    ]
    
    for script, message in scripts:
        try:
            print(Fore.CYAN + f"\n{message}" + Style.RESET_ALL)
            loading_animation()
            return_code = os.system(f"python {script}")
            
            if return_code != 0:
                print(Fore.RED + f"\n⚠️ Gagal menjalankan {script} (Kode Error: {return_code})")
                print(Fore.YELLOW + "Apakah Anda ingin melanjutkan ke proses berikutnya? (y/n)" + Style.RESET_ALL)
                if input().strip().lower() != 'y':
                    print(Fore.RED + "Proses moderasi dibatalkan!" + Style.RESET_ALL)
                    return_to_menu()
                    return
                    
        except Exception as e:
            print(Fore.RED + f"\n❌ Error saat menjalankan {script}: {str(e)}" + Style.RESET_ALL)
            print(Fore.YELLOW + "Apakah Anda ingin melanjutkan? (y/n)" + Style.RESET_ALL)
            if input().strip().lower() != 'y':
                return_to_menu()
                return
    
    print(Fore.GREEN + "\n✅ Semua proses moderasi selesai dengan sukses!" + Style.RESET_ALL)
    return_to_menu()

def loading_animation():
    for _ in range(3):
        for frame in ["⢿", "⣻", "⣽", "⣾", "⣷", "⣯", "⣟", "⡿"]:
            print(Fore.YELLOW + f"\rMemuat {frame}", end="")
            time.sleep(0.1)

def return_to_menu():
    input(Fore.CYAN + "\nTekan Enter untuk kembali ke menu utama..." + Style.RESET_ALL)
    main()

def main():
    while True:
        show_banner()
        show_menu()
        
        choice = input(Fore.CYAN + "\n🔢 Masukkan pilihan Anda (0-3): " + Style.RESET_ALL).strip()

        if choice == "1":
            loading_animation()
            run_autentikasi()
        elif choice == "2":
            loading_animation()
            run_delete_credentials()
        elif choice == "3":
            loading_animation()
            run_moderasi()
        elif choice == "0":
            print(Fore.GREEN + "\n👋 Terima kasih telah menggunakan Judol Remover by ARS!")
            print(Fore.YELLOW + "Sampai jumpa lagi!\n" + Style.RESET_ALL)
            time.sleep(1)
            break
        else:
            print(Fore.RED + "\n❌ Pilihan tidak valid! Silakan masukkan angka 0-3." + Style.RESET_ALL)
            time.sleep(1)

if __name__ == "__main__":
    main()
