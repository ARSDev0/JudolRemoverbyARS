import os
import time
import subprocess
from colorama import init, Fore, Back, Style

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
    print(Fore.BLUE + "4️⃣  " + Fore.WHITE + "Install Requirements")
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
            
            # Run the script and capture the return code
            return_code = os.system(f"python {script}")
            
            if return_code != 0:
                print(Fore.RED + f"\n⚠️ Gagal menjalankan {script} (Kode Error: {return_code})")
                print(Fore.YELLOW + "Apakah Anda ingin melanjutkan ke proses berikutnya? (y/n)" + Style.RESET_ALL)
                choice = input().strip().lower()
                if choice != 'y':
                    print(Fore.RED + "Proses moderasi dibatalkan!" + Style.RESET_ALL)
                    return_to_menu()
                    return
                    
        except Exception as e:
            print(Fore.RED + f"\n❌ Error saat menjalankan {script}: {str(e)}" + Style.RESET_ALL)
            print(Fore.YELLOW + "Apakah Anda ingin melanjutkan? (y/n)" + Style.RESET_ALL)
            choice = input().strip().lower()
            if choice != 'y':
                return_to_menu()
                return
    
    print(Fore.GREEN + "\n✅ Semua proses moderasi selesai dengan sukses!" + Style.RESET_ALL)
    return_to_menu()

def install_requirements():
    print(Fore.YELLOW + "\n🔧 Memulai instalasi requirements..." + Style.RESET_ALL)
    time.sleep(1)
    
    requirements = [
        "google-api-python-client",
        "google-auth-oauthlib",
        "google-auth-httplib2",
        "pandas",
        "emoji",
        "colorama"
    ]
    
    print(Fore.CYAN + "\n📦 Daftar package yang akan diinstall:")
    for package in requirements:
        print(Fore.WHITE + f"  • {package}")
    
    print(Fore.YELLOW + "\n⏳ Sedang menginstall...")
    loading_animation()
    
    try:
        for package in requirements:
            subprocess.check_call(["pip", "install", package])
        print(Fore.GREEN + "\n✅ Semua requirements berhasil diinstall!")
    except subprocess.CalledProcessError as e:
        print(Fore.RED + f"\n❌ Gagal menginstall requirements: {str(e)}")
    except Exception as e:
        print(Fore.RED + f"\n❌ Error: {str(e)}")
    
    return_to_menu()

def loading_animation():
    for i in range(3):
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
        
        choice = input(Fore.CYAN + "\n🔢 Masukkan pilihan Anda (0-4): " + Style.RESET_ALL).strip()

        if choice == "1":
            loading_animation()
            run_autentikasi()
        elif choice == "2":
            loading_animation()
            run_delete_credentials()
        elif choice == "3":
            loading_animation()
            run_moderasi()
        elif choice == "4":
            loading_animation()
            install_requirements()
        elif choice == "0":
            print(Fore.GREEN + "\n👋 Terima kasih telah menggunakan Judol Remover by ARS!")
            print(Fore.YELLOW + "Sampai jumpa lagi!\n" + Style.RESET_ALL)
            time.sleep(1)
            break
        else:
            print(Fore.RED + "\n❌ Pilihan tidak valid! Silakan masukkan angka 0-4." + Style.RESET_ALL)
            time.sleep(1)

if __name__ == "__main__":
    main()