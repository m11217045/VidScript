@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul 2>&1

echo ==========================================
echo      YouTube 財經報告生成器 - 修復工具
echo ==========================================
echo.

:: 切換到專案根目錄
cd /d "%~dp0\.."

:: 檢查 Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 錯誤：Python 未安裝或未加入 PATH
    echo 請先安裝 Python 3.8 或更高版本
    echo.
    endlocal
    pause
    exit /b 1
)

echo ✅ Python 已安裝: 
python --version
echo.

:: 檢查並創建虛擬環境
if exist "venv" (
    echo 📁 發現現有虛擬環境
    echo [1] 保留現有環境，只更新套件
    echo [2] 刪除並重新創建環境
    echo.
    set /p choice="請選擇 [1-2]: "
    
    if "!choice!"=="2" (
        echo 🗑️  刪除現有虛擬環境...
        rmdir /s /q venv
        goto :create_venv
    ) else (
        echo 📦 保留現有環境，繼續更新套件...
        goto :install_packages
    )
) else (
    goto :create_venv
)

:create_venv
echo.
echo 🔧 創建虛擬環境...
python -m venv venv
if errorlevel 1 (
    echo ❌ 錯誤：無法創建虛擬環境
    endlocal
    pause
    exit /b 1
)
echo ✅ 虛擬環境創建成功

:install_packages
echo.
echo 🚀 啟動虛擬環境並安裝套件...
call venv\Scripts\activate.bat

:: 更新 pip
echo 📦 更新 pip...
python -m pip install --upgrade pip

:: 檢查 requirements.txt 文件
if exist "config\requirements.txt" (
    echo 📝 使用現有的 config\requirements.txt...
    set requirements_file=config\requirements.txt
) else if exist "scripts\requirements.txt" (
    echo 📝 使用現有的 scripts\requirements.txt...
    set requirements_file=scripts\requirements.txt
) else (
    echo 📝 創建 requirements.txt...
    echo streamlit^>=1.28.0>requirements.txt
    echo google-generativeai^>=0.8.0>>requirements.txt
    echo openai-whisper^>=20231117>>requirements.txt
    echo python-dotenv^>=1.0.0>>requirements.txt
    echo torch^>=2.0.0>>requirements.txt
    echo torchaudio^>=2.0.0>>requirements.txt
    echo numpy^>=1.21.0>>requirements.txt
    echo requests^>=2.25.0>>requirements.txt
    set requirements_file=requirements.txt
)

:: 檢查 NVIDIA GPU 並選擇 PyTorch 版本
echo.
echo 🔍 檢查系統 GPU 支援...
nvidia-smi >nul 2>&1
if errorlevel 1 (
    echo ⚠️  未檢測到 NVIDIA GPU 或驅動，安裝 CPU 版本
    set pytorch_install=torch torchaudio --index-url https://download.pytorch.org/whl/cpu
) else (
    echo ✅ 檢測到 NVIDIA GPU，安裝 CUDA 支援版本
    for /f "tokens=*" %%i in ('nvidia-smi ^| findstr "CUDA Version"') do echo %%i
    set pytorch_install=torch torchaudio --index-url https://download.pytorch.org/whl/cu126
)

echo.
echo 📥 安裝核心套件...

:: 先安裝基礎套件
echo 🔧 安裝基礎套件...
pip install numpy requests python-dotenv streamlit psutil

:: 安裝 PyTorch
echo 🔧 安裝 PyTorch...
pip install %pytorch_install%
if errorlevel 1 (
    echo ⚠️  CUDA 版本安裝失敗，嘗試預設版本...
    pip install torch torchaudio
)

:: 安裝 AI 套件
echo 🔧 安裝 AI 套件...
pip install google-generativeai

:: 安裝 Whisper
echo 🔧 安裝 Whisper...
pip install openai-whisper

:: 下載必要工具
echo.
echo 🔧 下載必要工具 (FFmpeg, yt-dlp)...
python tools/download_tools.py

:: 添加 _internal 目錄到系統 PATH
echo.
echo 🔧 配置系統環境變數...
set "internal_path=%CD%\_internal"
if exist "%internal_path%" (
    echo 📁 找到 _internal 目錄: %internal_path%
    
    :: 檢查是否已經在 PATH 中
    echo %PATH% | findstr /i "%internal_path%" >nul
    if errorlevel 1 (
        echo 🔧 添加 _internal 目錄到系統 PATH...
        setx PATH "%PATH%;%internal_path%" >nul 2>&1
        if errorlevel 1 (
            echo ⚠️  無法自動添加到系統 PATH（可能需要管理員權限）
            echo 💡 請手動添加以下路徑到系統 PATH:
            echo    %internal_path%
        ) else (
            echo ✅ 成功添加 _internal 目錄到系統 PATH
            echo ⚠️  請重新啟動命令提示字元以使變更生效
        )
    ) else (
        echo ✅ _internal 目錄已在系統 PATH 中
    )
) else (
    echo ⚠️  _internal 目錄不存在，跳過 PATH 配置
)

:: 驗證安裝
echo.
echo 🔍 驗證安裝結果...
python -c "packages=['torch','whisper','google.generativeai','streamlit','dotenv','numpy','requests','psutil']; missing=[p for p in packages if not globals().update({'__import__':__import__}) and not __import__('importlib').util.find_spec(p)]; print('✅ 套件驗證通過' if not missing else f'❌ 缺少套件: {missing}'); import torch; print(f'🎯 GPU 加速: 可用' if torch.cuda.is_available() else '💻 GPU 加速: 不可用 (使用 CPU)')" 2>nul

:: 測試 FFmpeg 是否可用
echo.
echo 🔧 測試 FFmpeg 是否可用...
"%internal_path%\ffmpeg.exe" -version >nul 2>&1
if errorlevel 1 (
    echo ❌ FFmpeg 無法執行
) else (
    echo ✅ FFmpeg 可以正常執行
)

:: 創建 .env 範例檔案
if not exist ".env" (
    echo.
    echo 💡 請設定 API Keys:
    echo    編輯 .env 檔案，填入您的 API Keys
)

echo.
echo ==========================================
echo 🎉 修復/安裝完成！
echo ==========================================
echo.
echo 💡 接下來請：
echo    1. 確保已設定 .env 檔案中的 API Keys
echo    2. 執行 Setup_AutoStart.bat 啟動程式
echo    3. 如有問題，請重新執行此修復工具
echo.

endlocal
pause
