@echo off
echo Installing PyInstaller...
python -m pip install pyinstaller

echo Building Aegis AI...
python -m PyInstaller --noconfirm --onedir --windowed --distpath "dist_v6" --name "Aegis AI" --hidden-import="sounddevice" --hidden-import="numpy" --add-data "ui;ui" --add-data "core;core" main.py

echo Build complete! You can find the executable in the 'dist_v6\Aegis AI' folder.
pause
