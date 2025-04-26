# Change Log (Updates)

1. **ASCII Art**

   - The ASCII art in the program display has been simplified so it's not too large.

2. **File Naming**

   - File names have been changed for easier and more consistent access:
     - `softmain.py` → `main.py`
     - `installrequirement.py` → `requirements.py`

3. **File Organization**

   - Most files have been moved to the `assets` folder for better organization and maintainability.

4. **Gambling Ads Algorithm**

   - The algorithm for detecting gambling advertisements has been improved for higher accuracy and robustness.

5. **Requirements Installation Improvements**

   - The process for checking and installing libraries (requirements) has been improved so that:
     - If libraries are already installed, installation is skipped.
     - If installation fails due to environment issues (e.g., PEP 668/Kali Linux), the program will automatically create and run a virtual environment (venv).
     - Long error messages from pip are hidden, only a progress bar and short messages are shown.
     - A progress bar is displayed during requirements download.
     - If installation fails in the global environment, a message will appear:  
       **"We need to go to the venv."**

6. **Display & User Experience**

   - Messages during installation and errors are now clearer and more user-friendly.
   - No more misleading messages like "Done!" if installation fails.

7. **ASCII Art Removal**

   - Unnecessary ASCII art has been removed from the scanning comment process for a cleaner display.

8. **UI Improvements & Folder Structure**
   - Improved UI for all scripts: added blank lines between outputs, clearer section headers, and summary boxes.
   - Removed emoji and unnecessary separator lines from all outputs.
   - All results (such as exported CSV files) are now saved in a new `results` folder, which is created automatically if it does not exist.
   - The main comment scanning UI now displays clear section headers, video/channel info, and a summary of the results.

---

**Note:**  
All changes are intended to make the program easier to use, especially on operating systems that restrict global pip installation such as Kali Linux.
