@echo off
title Build Firewall & Network Tools EXE
color 0B

echo ============================================
echo   Building Firewall & Network Tools EXE
echo ============================================
echo.

:: Check if app is running
echo [Checking] Looking for running instances...
taskkill /F /IM NetworkTools.exe >nul 2>&1
taskkill /F /IM FirewallNetworkTools.exe >nul 2>&1
timeout /t 2 /nobreak >nul
echo [OK] No running instances
echo.

:: Clean previous builds
echo [1/4] Cleaning previous builds...
if exist "dist" (
    rmdir /s /q "dist" 2>nul
    if exist "dist" (
        echo [WARNING] Cannot delete dist folder. It may be in use.
        echo Please close any program using files in dist folder.
        echo Waiting 5 seconds...
        timeout /t 5 /nobreak >nul
        rmdir /s /q "dist" 2>nul
    )
)
if exist "build" rmdir /s /q "build" 2>nul
if exist "*.spec" del /q "*.spec" 2>nul
echo [OK] Cleanup complete
echo.

:: Install requirements
echo [2/4] Installing requirements...
if exist "requirements.txt" (
    pip install -r requirements.txt
) else (
    echo [WARNING] requirements.txt not found, installing default packages...
    pip install flask pandas openpyxl
)
echo [OK] Requirements installed
echo.

:: Install PyInstaller
echo [Installing] PyInstaller...
pip install pyinstaller --upgrade
echo.

:: Find PyInstaller location
echo [3/4] Building EXE file...
echo Finding PyInstaller...

:: Try to find pyinstaller
set PYINSTALLER_PATH=
for /f "tokens=*" %%i in ('where pyinstaller 2^>nul') do set PYINSTALLER_PATH=%%i

if "%PYINSTALLER_PATH%"=="" (
    echo PyInstaller not found in PATH, using Python module...
    set PYINSTALLER_CMD=python -m PyInstaller
) else (
    echo PyInstaller found at: %PYINSTALLER_PATH%
    set PYINSTALLER_CMD=pyinstaller
)

:: Build EXE
echo.
echo Building... This may take 2-5 minutes...
echo.

%PYINSTALLER_CMD% ^
    --onefile ^
    --name "NetworkTools" ^
    --hidden-import flask ^
    --hidden-import pandas ^
    --hidden-import openpyxl ^
    --hidden-import concurrent.futures ^
    --hidden-import socket ^
    --hidden-import subprocess ^
    --hidden-import re ^
    --hidden-import time ^
    --hidden-import base64 ^
    --hidden-import io ^
    --hidden-import os ^
    --collect-all flask ^
    --console ^
    network-tools.py

:: Check result
echo.
if exist "dist\NetworkTools.exe" (
    echo.
    echo [4/4] ============================================
    echo        BUILD SUCCESSFUL!
    echo ============================================
    echo.
    echo EXE file location:
    echo %CD%\dist\NetworkTools.exe
    echo.
    echo File size:
    dir "dist\NetworkTools.exe" | find "NetworkTools.exe"
    echo.
    echo ============================================
    echo HOW TO DISTRIBUTE:
    echo 1. Copy NetworkTools.exe to any Windows PC
    echo 2. No Python installation needed!
    echo 3. Double-click to run
    echo ============================================
    echo.
) else (
    echo.
    echo [4/4] ============================================
    echo        BUILD FAILED!
    echo ============================================
    echo.
    echo Troubleshooting:
    echo 1. Make sure app.py is in current folder
    echo 2. Check error messages above
    echo 3. Try running as Administrator
    echo.
)

pause