@echo off# Set working directory to script's parent directory (project root)
cd /d "%~dp0\.."

echo [INFO] 正在停止 Streamlit 應用程式...
echo [INFO] Stopping Streamlit application...
echo.

:: Check if psutil is installed
python -c "import psutil" 2>nul
if errorlevel 1 (
    echo [INFO] 安裝必要套件...
    echo [INFO] Installing required packages...
    pip install psutil
)

:: Run Python stop script
python tools/stop_streamlit.pyelayedexpansion
chcp 65001 >nul 2>&1

echo ==========================================
echo    YouTube Financial Report Generator v1.0.0
echo    YouTube 財經報告生成器 v1.0.0 - 停止服務
echo ==========================================
echo.

:: Set working directory to batch file location
cd /d "%~dp0"

echo [INFO] 正在停止 Streamlit 應用程式...
echo [INFO] Stopping Streamlit application...
echo.

:: Check if psutil is installed
python -c "import psutil" 2>nul
if errorlevel 1 (
    echo [INFO] 安裝必要套件...
    echo [INFO] Installing required packages...
    pip install psutil
)

:: Run Python stop script
python tools/stop_streamlit.py

echo.
pause
