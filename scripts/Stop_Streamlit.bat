@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul 2>&1

echo ==========================================
echo    YouTube Financial Report Generator v1.0.0
echo    YouTube 財經報告生成器 v1.0.0 - 停止服務
echo ==========================================
echo.

:: 切換到專案根目錄
cd /d "%~dp0\.."

echo [INFO] 正在停止 Streamlit 應用程式...
echo [INFO] Stopping Streamlit application...
echo.

:: 啟動虛擬環境
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
    echo [INFO] 虛擬環境已啟動
) else (
    echo [WARNING] 找不到虛擬環境，使用系統 Python
)

:: 執行 Python 停止腳本（正確的路徑）
if exist "tools\stop_streamlit.py" (
    echo [INFO] 執行停止腳本...
    python tools\stop_streamlit.py
) else (
    echo [ERROR] 找不到停止腳本: tools\stop_streamlit.py
    echo [INFO] 使用替代方法停止 Streamlit...
    
    :: 替代方法：直接殺死 streamlit 進程
    taskkill /f /im "streamlit.exe" 2>nul
    taskkill /f /im "python.exe" /fi "WINDOWTITLE eq *streamlit*" 2>nul
    
    :: 使用 Python 直接停止
    python -c "import psutil; [p.terminate() for p in psutil.process_iter(['pid', 'name', 'cmdline']) if any('streamlit' in str(cmd).lower() for cmd in p.info.get('cmdline', []))]" 2>nul
    
    echo [INFO] Streamlit 進程已停止
)

echo.
echo [INFO] 停止操作完成
pause
