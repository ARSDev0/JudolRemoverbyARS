import subprocess
import sys

def install(requirements_file="requirements.txt"):
    try:
        print(f"📦 Menginstall library dari {requirements_file}...\n")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", requirements_file])
        print("\n✅ Semua library berhasil diinstall!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Gagal menginstall: {e}")
    except Exception as e:
        print(f"⚠️ Error tak terduga: {e}")

if __name__ == "__main__":
    install()
