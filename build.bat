@echo off
setlocal

echo ==========================================
echo      CrazyCarAnalyzer Build Script
echo      (Using Python 3.11 + Virtual Env)
echo ==========================================

cd /d "%~dp0"

:: 1. Check/Create Virtual Environment
if not exist "venv" (
    echo [1/4] Creating virtual environment with Python 3.11...
    py -3.11 -m venv venv
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment. 
        echo Please ensure Python 3.11 is installed correctly.
        pause
        exit /b 1
    )
) else (
    echo [1/4] Virtual environment already exists.
)

:: 2. Activate Virtual Environment
echo [2/4] Activating virtual environment...
call venv\Scripts\activate
if errorlevel 1 (
    echo [ERROR] Failed to activate venv.
    pause
    exit /b 1
)

:: 3. Install Dependencies
echo [3/4] Installing/Updating dependencies in venv...
:: Upgrade pip first to avoid warnings
python -m pip install --upgrade pip
:: Install requirements
pip install -r requirements.txt
:: Install pyinstaller
pip install pyinstaller

:: 4. Build EXE
echo [4/4] Building EXE with PyInstaller...

:: Clean previous builds
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist *.spec del /q *.spec

:: Run build
pyinstaller --noconfirm --onefile --windowed ^
    --name "CrazyCarAnalyzer" ^
    --add-data "src/assets;src/assets" ^
    --collect-all "ddddocr" ^
    --collect-all "customtkinter" ^
    --hidden-import "PIL" ^
    --hidden-import "PIL._tkinter_finder" ^
    --hidden-import "babel.numbers" ^
    main.py

if errorlevel 1 (
    echo [ERROR] Build failed!
    pause
    exit /b 1
)

echo.
echo ==========================================
echo [SUCCESS] Build Complete!
echo The executable is located at:
echo %~dp0dist\CrazyCarAnalyzer.exe
echo.
echo Dependencies are installed in:
echo %~dp0venv
echo ==========================================
pause
endlocal
