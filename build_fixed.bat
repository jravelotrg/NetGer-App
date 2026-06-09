@echo off
title NetGer App Builder - Firewall & Network Tools Pro
color 0A

echo ================================================
echo    NetGer App Builder v1.2.0
echo    Firewall & Network Tools Pro
echo    Created by: Joy Ravelo Tarigan
echo ================================================
echo.

:: Hapus folder build dan dist lama
echo [1/4] Membersihkan folder build dan dist lama...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist *.spec del /q *.spec
echo        Selesai!
echo.

:: Install dependencies (jika perlu)
echo [2/4] Memeriksa dependencies...
pip install flask pandas openpyxl pyinstaller >nul 2>&1
echo        Dependencies siap!
echo.

:: Build dengan PyInstaller
echo [3/4] Membuat executable dengan PyInstaller...
echo        Mohon tunggu, proses ini membutuhkan waktu...
python -m PyInstaller --onefile --windowed --name="NetworkTools" --add-data "templates;templates" --add-data "static;static" app.py

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Gagal membuat executable!
    pause
    exit /b 1
)
echo        Executable berhasil dibuat!
echo.

:: Cek file hasil build
echo [4/4] Memeriksa hasil build...
if exist "dist\NetworkTools.exe" (
    echo        SUCCESS! File ditemukan: dist\NetworkTools.exe
    echo        Ukuran file: 
    dir "dist\NetworkTools.exe" | find "NetworkTools.exe"
) else (
    echo        ERROR: File tidak ditemukan!
)

echo.
echo ================================================
echo    BUILD SELESAI!
echo ================================================
echo.
echo File executable: dist\NetworkTools.exe
echo.
echo Untuk membuat installer:
echo   1. Buka Inno Setup Compiler
echo   2. Buka file setup.iss
echo   3. Tekan Ctrl+F9 untuk compile
echo.
pause