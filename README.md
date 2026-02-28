# FRIDAY AI - Voice Controlled Desktop Assistant

FRIDAY AI is a privacy-first, voice-activated AI companion that monitors the screen, detects digital threats in real-time, and warns the user via speech. It also includes an integrated **Voice-Controlled Application Launcher**.

## Setup & Running

FRIDAY AI is compiled as a standalone desktop application. 

1. Launch the application by double-clicking **`run.bat`** (or by executing `Aegis AI.exe` inside the `dist_v4/Aegis AI/` directory).
2. Ensure your microphone and speakers are active.
3. The UI dashboard will open automatically.

## Voice Commands

FRIDAY AI listens for the wake word: **"Hey Friday"** (or just **"Friday"**)

Follow it immediately with a command, for example:
- *"Hey Friday, scan screen"*
- *"Hey Friday, explain threats"*
- *"Hey Friday, block sender"*
- *"Hey Friday, open WhatsApp"*
- *"Hey Friday, open Calculator"*

## How to Add New Applications

The assistant uses a configuration file to map voice commands to application paths.

1. Run the application once. This will auto-generate an `apps.json` file in your main Aegis AI folder.
2. Open `apps.json` in any text editor (like Notepad).
3. Add a new entry following the pattern `"app_name": "path_to_executable"`.
   
   Example:
   ```json
   {
       "whatsapp": "C:\\Users\\Name\\AppData\\Local\\WhatsApp\\WhatsApp.exe",
       "chrome": "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
       "discord": "C:\\Users\\Name\\AppData\\Local\\Discord\\Update.exe --processStart Discord.exe"
   }
   ```
4. Restart FRIDAY AI to load the new commands. The new `"open discord"` command will automatically appear in your UI dashboard!

## How to Change the Wake Word

If you want to change the assistant's name (e.g., to "Jarvis"):
1. Open `core/audio.py` in the source code.
2. Locate the line: `if "hey friday" in text:` (around line 58)
3. Change `"hey friday"` to `"jarvis"`.
4. Run `build.bat` to recompile the application executable.

## How to Run at System Startup

To make FRIDAY AI run automatically when you turn on your computer:
1. Press `Win + R` to open the Run dialog.
2. Type `shell:startup` and press Enter. This opens your Windows Startup folder.
3. Right-click inside the folder, select **New > Shortcut**.
4. Browse and select the `Aegis AI.exe` file located in `dist_v4\Aegis AI\`.
5. Click Next and Finish. FRIDAY AI will now boot with your PC silently!
