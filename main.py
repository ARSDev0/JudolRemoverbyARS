import os
import time
import subprocess
import importlib.util
import sys

# Enable arrow key support in input prompts (if available)
try:
    import readline
except ImportError:
    pass

VERSION = "3.0"

def is_all_requirements_installed():
    # Check all packages listed in requirements.txt
    if not os.path.exists("requirements.txt"):
        return True
    with open("requirements.txt") as f:
        lines = f.readlines()
    for line in lines:
        pkg = line.strip()
        if not pkg or pkg.startswith("#"):
            continue
        # Extract module name (before any version specifier)
        mod = pkg.split("==")[0].split(">=")[0].split("<=")[0].strip().replace("-", "_")
        if importlib.util.find_spec(mod) is None:
            return False
    return True

def ensure_requirements():
    print("Searching dependencies...")
    if is_all_requirements_installed():
        return
    print("Installing missing requirements for the first time...")
    try:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"]
        )
        print("All requirements installed!")
    except subprocess.CalledProcessError:
        print("Failed to install requirements with the current Python environment.")
        venv_dir = "venv"
        try:
            if not os.path.isdir(venv_dir):
                subprocess.check_call([sys.executable, "-m", "venv", venv_dir])
                print(f"Virtual environment created at ./{venv_dir}")
            if os.name == "nt":
                venv_python = os.path.join(venv_dir, "Scripts", "python.exe")
            else:
                venv_python = os.path.join(venv_dir, "bin", "python")
            subprocess.check_call(
                [venv_python, "-m", "pip", "install", "-r", "requirements.txt"]
            )
            print("All requirements installed in the virtual environment!")
            print("Re-running script inside the virtual environment...")
            os.execv(venv_python, [venv_python, os.path.abspath(__file__)] + sys.argv[1:])
        except Exception as e:
            print(f"Failed to set up or use virtual environment: {e}")
            print("Please install dependencies manually or check your Python installation.")
            sys.exit(1)

ensure_requirements()

from colorama import init, Fore, Back, Style
init(autoreset=True)

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def show_banner():
    clear_screen()
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

def show_menu():
    print(Fore.YELLOW + " MAIN MENU ".center(60, '─') + Style.RESET_ALL)
    print(Fore.GREEN + "1. " + Fore.WHITE + "Konfigurasi Auth")
    print(Fore.GREEN + "2. " + Fore.WHITE + "Scan Komentar Judol")
    print(Fore.GREEN + "3. " + Fore.WHITE + "Hapus File Kredensial")
    print(Fore.CYAN + "9. " + Fore.WHITE + "Credits") 
    print(Fore.RED + "0. " + Fore.WHITE + "Keluar dari Program")

def run_auth_config():
    print()
    print(Fore.YELLOW + "Konfigurasi Auth..." + Style.RESET_ALL)
    print()
    # Call the autentikasi.py main function for full OAuth/API key flow
    import assets.autentikasi
    assets.autentikasi.main()
    return_to_menu()

def run_delete_credentials():
    print(Fore.YELLOW + "\nMemulai penghapusan kredensial..." + Style.RESET_ALL)
    time.sleep(1)
    # Change path to assets/auth_delete.py
    os.system(f'"{sys.executable}" assets/auth_delete.py')
    return_to_menu()

def run_moderasi():
    print(Fore.YELLOW + "\nMemulai proses moderasi komentar..." + Style.RESET_ALL)
    time.sleep(1)
    scripts = [
        ("assets/put_comments.py", "Mengambil komentar dari YouTube..."),
        ("assets/first_cleaning.py", "Proses pembersihan pertama..."),
        ("assets/second_cleaning.py", "Proses pembersihan kedua..."),
        ("assets/final_action.py", "Tindakan final moderasi...")
    ]
    for script, message in scripts:
        try:
            print(Fore.CYAN + f"\n{message}" + Style.RESET_ALL)
            loading_animation()
            return_code = os.system(f'"{sys.executable}" {script}')
            if return_code != 0:
                print(Fore.RED + f"\nGagal menjalankan {script} (Kode Error: {return_code})")
                print(Fore.YELLOW + "Terjadi error fatal pada proses ini. Silakan perbaiki masalah di atas lalu jalankan ulang proses moderasi dari awal." + Style.RESET_ALL)
                return_to_menu()
                return
        except Exception as e:
            print(Fore.RED + f"\nError saat menjalankan {script}: {str(e)}" + Style.RESET_ALL)
            print(Fore.YELLOW + "Terjadi error fatal pada proses ini. Silakan perbaiki masalah di atas lalu jalankan ulang proses moderasi dari awal." + Style.RESET_ALL)
            return_to_menu()
            return
    print(Fore.GREEN + "\nSemua proses moderasi selesai dengan sukses!" + Style.RESET_ALL)
    return_to_menu()

def run_credits():
    print()
    os.system(f'"{sys.executable}" credits.py')
    return_to_menu()

def install_requirements():
    print(Fore.YELLOW + "\nMemulai instalasi requirements..." + Style.RESET_ALL)
    time.sleep(1)
    def is_package_installed(package_name):
        import importlib.util
        spec = importlib.util.find_spec(package_name)
        return spec is not None
    if is_package_installed("colorama"):
        print(Fore.GREEN + "\nSemua requirements sudah terinstall!")
        return_to_menu()
        return
    print(Fore.CYAN + "\nMenginstall semua requirements dari requirements.txt")
    print(Fore.YELLOW + "\nSedang menginstall...")
    loading_animation()
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print(Fore.GREEN + "\nSemua requirements berhasil diinstall!")
    except subprocess.CalledProcessError as e:
        print(Fore.RED + f"\nGagal menginstall requirements: {str(e)}")
    except Exception as e:
        print(Fore.RED + f"\nError: {str(e)}")
    return_to_menu()

def loading_animation():
    for i in range(3):
        for frame in ["⢿", "⣻", "⣽", "⣾", "⣷", "⣯", "⣟", "⡿"]:
            print(Fore.YELLOW + f"\rMemuat {frame}", end="")
            time.sleep(0.1)
    print("\r" + " " * 30 + "\r", end="")  # Clear the loading line after done

def return_to_menu():
    input(Fore.CYAN + "\nTekan Enter untuk kembali ke menu utama..." + Style.RESET_ALL)
    main()

def main():
    while True:
        show_banner()
        show_menu()
        
        choice = input(Fore.CYAN + "\nMasukkan pilihan Anda: " + Style.RESET_ALL).strip()

        if choice == "1":
            loading_animation()
            run_auth_config()
        elif choice == "2":
            loading_animation()
            run_moderasi()
        elif choice == "3":
            loading_animation()
            run_delete_credentials()
        elif choice == "9":
            loading_animation()
            run_credits()
        elif choice == "0":
            print(Fore.GREEN + "\nTerima kasih telah menggunakan Judol Remover by ARS!")
            print(Fore.YELLOW + "Sampai jumpa lagi!\n" + Style.RESET_ALL)
            time.sleep(1)
            break
        else:
            print(Fore.RED + "\nPilihan tidak valid! Silakan masukkan angka 0-3 atau 9." + Style.RESET_ALL)
            time.sleep(1)

if __name__ == "__main__":
    main()
