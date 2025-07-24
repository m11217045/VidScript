@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul 2>&1

echo ==========================================
echo      VidScript 套件優化修復工具
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

:: 檢查虛擬環境
if not exist "venv" (
    echo ❌ 虛擬環境不存在，請先執行 setup.bat
    echo.
    endlocal
    pause
    exit /b 1
)

echo 🚀 啟動虛擬環境...
call venv\Scripts\activate.bat

echo.
echo 🔍 分析當前已安裝的套件...
pip list

echo.
echo 🗑️  移除過時和多餘的套件...

:: 移除 openai-whisper（已遷移到 faster-whisper）
echo 移除 openai-whisper...
pip uninstall openai-whisper -y 2>nul

:: 移除 whisper（重複套件）
echo 移除 whisper...
pip uninstall whisper -y 2>nul

:: 移除其他可能的舊版本
echo 移除可能的舊版本套件...
pip uninstall tiktoken -y 2>nul
pip uninstall more-itertools -y 2>nul

echo.
echo 📥 安裝和更新必要套件...

:: 更新 pip
echo 📦 更新 pip...
python -m pip install --upgrade pip

:: 檢查 NVIDIA GPU
echo.
echo 🔍 檢查系統 GPU 支援...
nvidia-smi >nul 2>&1
if errorlevel 1 (
    echo ⚠️  未檢測到 NVIDIA GPU，使用 CPU 版本
    set pytorch_install=torch==2.6.0 torchaudio==2.6.0 --index-url https://download.pytorch.org/whl/cpu
) else (
    echo ✅ 檢測到 NVIDIA GPU，使用 CUDA 11.8 版本
    set pytorch_install=torch==2.6.0+cu118 torchaudio==2.6.0+cu118 --index-url https://download.pytorch.org/whl/cu118
)

:: 安裝核心套件（按正確順序）
echo.
echo 📦 安裝核心套件...

echo 🔧 安裝基礎套件...
pip install numpy>=1.21.0 requests>=2.25.0 python-dotenv>=1.0.0

echo 🔧 安裝 PyTorch (faster-whisper 優化版本)...
pip install %pytorch_install%

echo 🔧 安裝 Faster-Whisper...
pip install faster-whisper==1.1.1
if errorlevel 1 (
    echo ⚠️  1.1.1 版本安裝失敗，嘗試最新版本...
    pip install faster-whisper>=1.0.0
)

echo 🔧 安裝 Google AI 和 Streamlit...
pip install google-generativeai>=0.8.0 streamlit>=1.28.0

echo 🔧 安裝系統監控套件...
pip install psutil>=5.9.0

echo.
echo 🔍 驗證安裝結果...
python -c "
import sys
print('🔧 執行套件驗證...')

# 檢查核心套件
packages = {
    'torch': 'PyTorch',
    'faster_whisper': 'Faster-Whisper', 
    'google.generativeai': 'Google Gemini AI',
    'streamlit': 'Streamlit',
    'dotenv': 'Python-dotenv',
    'numpy': 'NumPy',
    'requests': 'Requests',
    'psutil': 'PSUtil'
}

missing = []
for module, name in packages.items():
    try:
        __import__(module.replace('-', '_').split('.')[0])
        print(f'✅ {name}: 已安裝')
    except ImportError:
        missing.append(name)
        print(f'❌ {name}: 未安裝')

if missing:
    print(f'❌ 缺少套件: {missing}')
    sys.exit(1)

# 檢查是否有舊版 whisper
try:
    import whisper
    print('⚠️  警告: 檢測到舊版 openai-whisper，建議手動移除')
except ImportError:
    print('✅ 未檢測到舊版 whisper 套件')

# 檢查 GPU 支援
import torch
print(f'🎯 PyTorch 版本: {torch.__version__}')
print(f'🎯 CUDA 支援: {\"可用\" if torch.cuda.is_available() else \"不可用\"}')

if torch.cuda.is_available():
    print(f'🖥️ GPU 設備: {torch.cuda.get_device_name(0)}')
    print(f'💾 VRAM 總量: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB')

# 測試 faster-whisper
try:
    from faster_whisper import WhisperModel
    print('✅ Faster-Whisper 可正常載入')
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f'🚀 推薦配置: device=\"{device}\"')
    print('💡 預期性能提升: 7-40x (相比原始 OpenAI Whisper)')
except Exception as e:
    print(f'❌ Faster-Whisper 測試失敗: {e}')
    sys.exit(1)

print('🎉 所有套件驗證通過！')
" 2>nul

if errorlevel 1 (
    echo ❌ 套件驗證失敗，請檢查上方錯誤訊息
    goto :error_exit
)

:: 更新 requirements.txt
echo.
echo 📝 更新 requirements.txt 檔案...

echo # VidScript 優化套件清單 - 精簡版本>config\requirements.txt
echo # 基於實際使用分析的最小必要套件>>config\requirements.txt
echo.>>config\requirements.txt
echo # 核心 AI 套件>>config\requirements.txt
echo torch==2.6.0+cu118>>config\requirements.txt
echo torchaudio==2.6.0+cu118>>config\requirements.txt
echo faster-whisper==1.1.1>>config\requirements.txt
echo.>>config\requirements.txt
echo # AI 服務>>config\requirements.txt
echo google-generativeai^>=0.8.0>>config\requirements.txt
echo.>>config\requirements.txt
echo # 網頁界面>>config\requirements.txt
echo streamlit^>=1.28.0>>config\requirements.txt
echo.>>config\requirements.txt
echo # 基礎套件>>config\requirements.txt
echo python-dotenv^>=1.0.0>>config\requirements.txt
echo requests^>=2.25.0>>config\requirements.txt
echo numpy^>=1.21.0>>config\requirements.txt
echo psutil^>=5.9.0>>config\requirements.txt

echo ✅ requirements.txt 已更新

echo.
echo ==========================================
echo 🎉 套件優化完成！
echo ==========================================
echo.
echo ✅ 已移除多餘套件：
echo    ❌ openai-whisper (已替換為 faster-whisper)
echo    ❌ whisper (重複套件)
echo.
echo ✅ 已優化必要套件：
echo    🚀 faster-whisper 1.1.1 (GPU 優化)
echo    🔥 PyTorch 2.6.0 + CUDA 11.8
echo    🧠 Google Gemini AI
echo    🖥️ Streamlit 網頁界面
echo.
echo 💡 下一步：
echo    1. 執行 scripts/Setup_AutoStart.bat 啟動程式
echo    2. 確保 .env 檔案已設定 Google API Key
echo.

endlocal
pause
exit /b 0

:error_exit
echo.
echo ==========================================
echo ❌ 套件優化失敗
echo ==========================================
echo.
echo 💡 建議操作：
echo    1. 重新執行 scripts/setup.bat
echo    2. 檢查網路連線
echo    3. 確認虛擬環境狀態
echo.

endlocal
pause
exit /b 1
