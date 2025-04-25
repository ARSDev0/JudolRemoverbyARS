# Judol Remover by ARS

**Judol Remover** is a Python tool for automatic moderation of spam comments on YouTube, featuring an advanced gambling ad detection algorithm and multi-platform support.

**Version:** Alpha-1.5  
**Author:** Awiones  
**Repo:** [github.com/awiones](https://github.com/awiones)

---

## 🛠️ Requirements

- Python 3.7+
- Internet connection
- Google Cloud Project (to obtain YouTube Client ID, Client Secret, and API Key)

---

## 🚀 Installation

### On PC (Windows/Linux/Mac)

1. **Install Python**  
   Download & install from [python.org](https://www.python.org/downloads/).

2. **Clone/Download this repo**

   ```bash
   git clone <repo-url>
   cd JudolRemoverbyARS
   ```

3. **Install dependencies**  
   Run:
   ```bash
   python main.py
   ```
   Choose the `Install Requirements` menu (option 4) on the main screen.

### On Android (Pydroid3)

1. Install the **Pydroid3** app from the Play Store.
2. Download all project files to the Pydroid3 folder.
3. Run:
   ```
   python main.py
   ```
   Choose the `Install Requirements` menu.

---

## ⚡ How to Use

1. **Run the main program**
   ```
   python main.py
   ```
2. **Main menu:**

   - `1` YouTube Authentication (enter Client ID, Client Secret, and API Key if available)
   - `2` Delete credential files (reset authentication)
   - `3` Run comment moderation (scraping, cleaning, labeling, moderation)
   - `4` Install requirements (must be run the first time)
   - `0` Exit

3. **Workflow:**
   - Install requirements (once)
   - Authenticate (enter Client ID, Client Secret, API Key if desired)
   - Run moderation: choose to scan a video/channel, the process is automatic up to moderation

---

## 🔑 Authentication

- **Client ID & Client Secret**:  
  Obtain from Google Cloud Console (create OAuth Client ID, choose Desktop).
- **API Key (optional, for faster scraping/more quota)**:  
  Obtain from Google Cloud Console (API & Services > Credentials > Create API Key).

Full tutorials are available on YouTube.

---

## 📝 Troubleshooting

- **Dependency errors**: Make sure you have installed requirements (menu 4).
- **Authentication failed**: Make sure your Client ID/Secret are correct, and YouTube Data API v3 is enabled in Google Cloud.
- **Comments not moderated**: Make sure your account has moderation access to the channel.

---

## 🙏 Thanks

For questions or feedback, please contact or check this repo.  
Happy using!
