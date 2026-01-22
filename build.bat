@echo off
echo ==========================================
echo      CrazyCarAnalyzer Build Script
echo ==========================================

echo [1/3] Installing Dependencies...
pip install -r requirements.txt
pip install pyinstaller

echo [2/3] Cleaning previous builds...
rmdir /s /q build
rmdir /s /q dist
del /q *.spec

echo [3/3] Building EXE...
pyinstaller --noconfirm --onefile --windowed ^
    --name "CrazyCarAnalyzer" ^
    --add-data "src/assets;src/assets" ^
    --hidden-import "customtkinter" ^
    --hidden-import "PIL" ^
    --hidden-import "PIL._tkinter_finder" ^
    --hidden-import "babel.numbers" ^
    main.py

echo ==========================================
echo Build Complete! Check 'dist' folder.
echo ==========================================
pause
