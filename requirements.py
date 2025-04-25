import subprocess
import sys
import time

def show_progress_bar():
    bar = "⣾⣷⣯⣟⡿⢿⣻⣽"
    for i in range(20):
        print(f"\r⏳ Downloading requirements... {bar[i % len(bar)]}", end="")
        time.sleep(0.1)

def install(requirements_file="requirements.txt"):
    try:
        print(f"📦 Installing libraries from {requirements_file}...\n")
        show_progress_bar()
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "-r", requirements_file],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        print("\r⏳ Downloading requirements... Done!   ")
        print("\n✅ All libraries installed successfully!")
    except subprocess.CalledProcessError as e:
        print("\r⏳ Downloading requirements... Failed! ")
        print("We need to go to the venv.")
        sys.exit(1)
    except Exception as e:
        print(f"⚠️ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    install()
