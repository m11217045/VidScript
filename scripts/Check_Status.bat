@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul 2>&1

echo ==========================================
echo      VidScript 專案狀態檢查工具
echo ==========================================
echo.

:: 切換到專案根目錄
cd /d "%~dp0\.."

echo 🔍 正在檢查專案狀態...
echo.

:: 檢查 Python 環境
echo 📋 Python 環境檢查:
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python 未安裝或未加入 PATH
) else (
    echo ✅ Python 已安裝: 
    python --version
)

:: 檢查虛擬環境
echo.
echo 📋 虛擬環境檢查:
if exist "venv" (
    echo ✅ 虛擬環境已存在
    call venv\Scripts\activate.bat
    
    echo.
    echo 📦 已安裝的套件:
    pip list | findstr -i "torch streamlit faster-whisper google-generativeai numpy requests psutil python-dotenv"
    
    echo.
    echo 🔍 檢查舊版套件:
    pip list | findstr -i "openai-whisper whisper tiktoken"
    if errorlevel 1 (
        echo ✅ 未發現舊版 whisper 套件
    ) else (
        echo ⚠️  發現舊版套件，建議執行 Package_Cleanup.bat
    )
) else (
    echo ❌ 虛擬環境不存在，請執行 setup.bat
)

:: 檢查工具檔案
echo.
echo 📋 工具檔案檢查:
if exist "_internal\ffmpeg.exe" (
    echo ✅ FFmpeg 已存在
) else (
    echo ❌ FFmpeg 不存在
)

if exist "_internal\yt-dlp.exe" (
    echo ✅ yt-dlp 已存在
) else (
    echo ❌ yt-dlp 不存在
)

:: 檢查配置檔案
echo.
echo 📋 配置檔案檢查:
if exist ".env" (
    echo ✅ .env 檔案已存在
    findstr "GOOGLE_API_KEY" .env >nul 2>&1
    if errorlevel 1 (
        echo ⚠️  .env 檔案中未找到 GOOGLE_API_KEY
    ) else (
        echo ✅ GOOGLE_API_KEY 已配置
    )
) else (
    echo ❌ .env 檔案不存在
)

if exist "config\requirements.txt" (
    echo ✅ config\requirements.txt 已存在
) else (
    echo ❌ config\requirements.txt 不存在
)

:: 檢查主要腳本檔案
echo.
echo 📋 主要檔案檢查:
set "important_files=main.py src\ui\app_streamlit.py src\core\config.py src\services\video_processor.py src\services\ai_service.py"

for %%f in (%important_files%) do (
    if exist "%%f" (
        echo ✅ %%f
    ) else (
        echo ❌ %%f 不存在
    )
)

:: 檢查腳本檔案
echo.
echo 📋 腳本檔案檢查:
set "script_files=scripts\setup.bat scripts\Setup_AutoStart.bat scripts\Stop_Streamlit.bat"

for %%f in (%script_files%) do (
    if exist "%%f" (
        echo ✅ %%f
    ) else (
        echo ❌ %%f 不存在
    )
)

:: 執行 Python 環境測試
if exist "venv" (
    echo.
    echo 🧪 執行 Python 環境測試...
    call venv\Scripts\activate.bat
    python -c "
import sys
print('🔧 Python 環境測試...')

# 測試核心套件匯入
try:
    import torch
    print(f'✅ PyTorch {torch.__version__}')
    print(f'   GPU 支援: {torch.cuda.is_available()}')
except ImportError:
    print('❌ PyTorch 未安裝')

try:
    from faster_whisper import WhisperModel
    print('✅ Faster-Whisper 已安裝')
except ImportError:
    print('❌ Faster-Whisper 未安裝')

try:
    import google.generativeai
    print('✅ Google Generative AI 已安裝')
except ImportError:
    print('❌ Google Generative AI 未安裝')

try:
    import streamlit
    print('✅ Streamlit 已安裝')
except ImportError:
    print('❌ Streamlit 未安裝')

try:
    from dotenv import load_dotenv
    print('✅ Python-dotenv 已安裝')
except ImportError:
    print('❌ Python-dotenv 未安裝')

try:
    import requests
    print('✅ Requests 已安裝')
except ImportError:
    print('❌ Requests 未安裝')

try:
    import psutil
    print('✅ PSUtil 已安裝')
except ImportError:
    print('❌ PSUtil 未安裝')

# 檢查舊版套件
old_packages = []
try:
    import whisper
    old_packages.append('openai-whisper')
except ImportError:
    pass

if old_packages:
    print(f'⚠️  發現舊版套件: {old_packages}')
else:
    print('✅ 未發現舊版套件')

print('🎉 環境檢查完成！')
" 2>nul
)

echo.
echo ==========================================
echo 📊 檢查報告摘要
echo ==========================================
echo.
echo 💡 如果發現問題，請執行以下腳本：
echo    🔧 環境問題: scripts\setup.bat
echo    🗑️  套件問題: scripts\Package_Cleanup.bat
echo    🚀 啟動問題: scripts\Setup_AutoStart.bat
echo.

pause
