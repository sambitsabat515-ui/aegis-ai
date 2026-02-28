import os
import json
import subprocess
import logging

logger = logging.getLogger(__name__)

class AppLauncher:
    def __init__(self, config_file="apps.json"):
        self.config_file = config_file
        self.apps = self.load_config()

    def load_config(self):
        default_apps = {
            "whatsapp": os.path.expandvars(r"%LOCALAPPDATA%\WhatsApp\WhatsApp.exe"),
            "chrome": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            "calculator": "calc.exe",
            "notepad": "notepad.exe",
            "spotify": os.path.expandvars(r"%APPDATA%\Spotify\Spotify.exe")
        }
        
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    apps = json.load(f)
                    # Merge defaults if missing
                    for k, v in default_apps.items():
                        if k not in apps:
                            apps[k] = v
                    return apps
            except Exception as e:
                logger.error(f"Error loading config: {e}")
                return default_apps
        else:
            self.save_config(default_apps)
            return default_apps

    def save_config(self, apps):
        try:
            with open(self.config_file, 'w') as f:
                json.dump(apps, f, indent=4)
        except Exception as e:
            logger.error(f"Failed to save apps config: {e}")

    def get_available_apps(self):
        return list(self.apps.keys())

    def launch_app(self, app_name):
        app_name = app_name.lower().strip()
        
        # Simple fuzzy match based on keys
        target = None
        for key in self.apps:
            if key in app_name or app_name.replace(" ", "") in key.replace(" ", ""):
                target = key
                break
                
        if not target:
            logger.info(f"App '{app_name}' not in apps.json. Falling back to OS PATH execution.")
            os.system(f"start {app_name}: 2>nul || start {app_name} 2>nul")
            return True

        path = self.apps[target]
        
        try:
            logger.info(f"Launching mapped application: {path}")
            # Use subprocess to launch and detach
            subprocess.Popen(path, shell=True, creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP)
            return True
        except Exception as e:
            logger.error(f"Failed to launch {target} at {path}: {e}")
            # Ultimate fallback
            os.system(f"start {target}: 2>nul || start {target} 2>nul")
            return True
