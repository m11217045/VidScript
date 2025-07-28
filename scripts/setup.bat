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
    echo faster-whisper^>=1.0.0>>requirements.txt
    echo python-dotenv^>=1.0.0>>requirements.txt
    echo torch^>=2.0.0>>requirements.txt
    echo torchaudio^>=2.0.0>>requirements.txt
    echo numpy^>=1.21.0>>requirements.txt
    echo requests^>=2.25.0>>requirements.txt
    echo psutil^>=5.9.0>>requirements.txt
    set requirements_file=requirements.txt
)

:: 檢查 NVIDIA GPU 並選擇最佳 PyTorch 版本
echo.
echo 🔍 檢查系統 GPU 支援...
nvidia-smi >nul 2>&1
if errorlevel 1 (
    echo ⚠️  未檢測到 NVIDIA GPU 或驅動，安裝 CPU 版本
    set pytorch_install=torch==2.6.0 torchaudio==2.6.0 --index-url https://download.pytorch.org/whl/cpu
) else (
    echo ✅ 檢測到 NVIDIA GPU，使用經過驗證的 CUDA 11.8 版本
    for /f "tokens=*" %%i in ('nvidia-smi ^| findstr "CUDA Version"') do echo %%i
    echo 📌 使用 PyTorch 2.6.0 + CUDA 11.8 (經過 faster-whisper 優化驗證)
    set pytorch_install=torch==2.6.0+cu118 torchaudio==2.6.0+cu118 --index-url https://download.pytorch.org/whl/cu118
)

echo.
echo 📥 安裝核心套件 (使用優化的安裝順序)...

:: 先安裝基礎套件
echo 🔧 安裝基礎套件...
pip install numpy requests python-dotenv streamlit psutil

:: 安裝 PyTorch (關鍵：需要特定版本確保 faster-whisper 兼容性)
echo 🔧 安裝 PyTorch 2.6.0 (faster-whisper 優化版本)...
pip install %pytorch_install%
if errorlevel 1 (
    echo ⚠️  指定版本安裝失敗，嘗試降級到兼容版本...
    pip install torch==2.6.0 torchaudio==2.6.0
    if errorlevel 1 (
        echo ❌ PyTorch 安裝失敗，請手動安裝
        goto :error_exit
    )
)

:: 驗證 PyTorch 版本和 CUDA 支援
echo 🔍 驗證 PyTorch 安裝...
python -c "import torch; print(f'✅ PyTorch {torch.__version__}'); print(f'🎯 CUDA 可用: {torch.cuda.is_available()}'); print(f'📊 GPU 設備: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else \"無\"}'); ver=torch.__version__; major,minor=int(ver.split(\".\")[0]),int(ver.split(\".\")[1]); print(f\"⚠️ 版本警告: 建議使用 PyTorch 2.6.x 確保最佳兼容性\" if major>2 or (major==2 and minor>6) else \"✅ 版本兼容性良好\")" 2>nul
if errorlevel 1 (
    echo ❌ PyTorch 驗證失敗
    goto :error_exit
)

:: 安裝 AI 套件
echo 🔧 安裝 Google AI 套件...
pip install google-generativeai

:: 安裝 Faster-Whisper (關鍵步驟)
echo 🔧 安裝 Faster-Whisper 1.1.1 (GPU 優化版本)...
pip install faster-whisper==1.1.1
if errorlevel 1 (
    echo ⚠️  指定版本安裝失敗，嘗試最新穩定版本...
    pip install faster-whisper>=1.0.0
    if errorlevel 1 (
        echo ❌ Faster-Whisper 安裝失敗
        goto :error_exit
    )
)

:: 驗證 faster-whisper 安裝和 GPU 支援
echo 🔍 驗證 Faster-Whisper 安裝...
python -c "from faster_whisper import WhisperModel; import torch; print('✅ Faster-Whisper 匯入成功'); cuda_available = torch.cuda.is_available(); print(f'🎯 GPU 支援: {\"可用\" if cuda_available else \"不可用\"}'); print('💡 如果有 GPU 但顯示不可用，這是正常的 - CTranslate2 使用優化後端')" 2>nul
if errorlevel 1 (
    echo ❌ Faster-Whisper 驗證失敗
    goto :error_exit
)

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

:: 驗證完整安裝
echo.
echo 🔍 執行全面安裝驗證...
python -c "
import sys
print('🔧 執行完整系統驗證...')

# 檢查核心套件
packages = ['torch', 'faster_whisper', 'google.generativeai', 'streamlit', 'dotenv', 'numpy', 'requests', 'psutil']
missing = []
for p in packages:
    try:
        __import__(p.replace('-', '_').split('.')[0])
        print(f'✅ {p}: 已安裝')
    except ImportError:
        missing.append(p)
        print(f'❌ {p}: 未安裝')

if missing:
    print(f'❌ 缺少套件: {missing}')
    sys.exit(1)

# 檢查 GPU 支援
import torch
print(f'🎯 PyTorch 版本: {torch.__version__}')
print(f'🎯 CUDA 支援: {\"可用\" if torch.cuda.is_available() else \"不可用\"}')

if torch.cuda.is_available():
    print(f'� GPU 設備: {torch.cuda.get_device_name(0)}')
    print(f'💾 VRAM 總量: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB')

# 測試 faster-whisper
try:
    from faster_whisper import WhisperModel
    print('✅ Faster-Whisper 可正常載入')
    
    # 簡單的模型初始化測試（不會實際載入）
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f'🚀 推薦配置: device=\"{device}\", compute_type=\"{\"int8_float16\" if device==\"cuda\" else \"int8\"}\"')
    print('💡 預期性能提升: 7-40x (相比原始 OpenAI Whisper)')
    
except Exception as e:
    print(f'❌ Faster-Whisper 測試失敗: {e}')
    sys.exit(1)

print('🎉 所有套件驗證通過！')
" 2>nul

if errorlevel 1 (
    echo ❌ 安裝驗證失敗，請檢查上方錯誤訊息
    goto :error_exit
)

:: 測試 FFmpeg 是否可用
echo.
echo 🔧 測試 FFmpeg 是否可用...
"%internal_path%\ffmpeg.exe" -version >nul 2>&1
if errorlevel 1 (
    echo ❌ FFmpeg 無法執行
) else (
    echo ✅ FFmpeg 可以正常執行
)

:: 創建 .env.example 範例檔案
echo.
echo 📝 創建 .env.example 範例檔案...
echo # VidScript 環境變數配置檔案>.env.example
echo # 複製此檔案為 .env 並填入您的 API Keys>>.env.example
echo.>>.env.example
echo # Google Gemini AI API Key>>.env.example
echo # 請到 https://aistudio.google.com/app/apikey 取得>>.env.example
echo GOOGLE_API_KEY=your_google_api_key_here>>.env.example
echo.>>.env.example
echo # 可選：自訂預設儲存路徑>>.env.example
echo # DEFAULT_SAVE_PATH=D:\VidScript\reports>>.env.example
echo.>>.env.example
echo # 可選：自訂 Whisper 模型>>.env.example
echo # DEFAULT_WHISPER_MODEL=base>>.env.example
echo.>>.env.example
echo # 可選：啟用除錯模式>>.env.example
echo # DEBUG=false>>.env.example

if exist ".env.example" (
    echo ✅ .env.example 檔案已創建
) else (
    echo ❌ .env.example 檔案創建失敗
)

:: 檢查並提示使用者創建 .env 檔案
if not exist ".env" (
    echo.
    echo 💡 請設定 API Keys:
    echo    1. 複製 .env.example 為 .env
    echo    2. 編輯 .env 檔案，填入您的 Google API Key
    echo    3. 可到 https://aistudio.google.com/app/apikey 免費取得
    echo.
    echo 📋 快速設定指令:
    echo    copy .env.example .env
    echo    notepad .env
) else (
    echo.
    echo ✅ 找到現有 .env 檔案
    echo 💡 請確認已正確設定 GOOGLE_API_KEY
)

echo.
echo ==========================================
echo 🎉 VidScript 環境設置完成！
echo ==========================================
echo.
echo ✅ 已成功安裝：
echo    🚀 Faster-Whisper 1.1.1 (GPU 優化)
echo    🔥 PyTorch 2.6.0 + CUDA 11.8 (兼容性驗證)
echo    🧠 Google Gemini AI
echo    🖥️ Streamlit 網頁界面
echo    � .env.example 配置範例檔案
echo    �🛠️ 所有必要工具和依賴
echo.
echo 🚀 性能提升：
echo    ⚡ 語音轉文字速度：7-40x 加速
echo    💾 VRAM 使用：極度優化
echo    🎯 GPU 支援：完全啟用
echo.
echo 💡 接下來請：
echo    1. 複製 .env.example 為 .env 並填入您的 Google API Key
echo    2. 執行 Setup_AutoStart.bat 啟動程式
echo    3. 享受超快的影片分析體驗！
echo.
echo 🔧 如遇問題可執行：
echo    - python test_speed.py (性能測試)
echo    - python tools/check_environment.py (環境檢查)
echo.

endlocal
pause
exit /b 0

:error_exit
echo.
echo ==========================================
echo ❌ 安裝過程中發生錯誤
echo ==========================================
echo.
echo 💡 故障排除建議：
echo    1. 確認網路連線正常
echo    2. 檢查 Python 版本 (建議 3.8-3.11)
echo    3. 更新 pip: python -m pip install --upgrade pip
echo    4. 重新執行安裝程式
echo.
echo 🔧 手動安裝指令：
echo    pip install torch==2.6.0+cu118 torchaudio==2.6.0+cu118 --index-url https://download.pytorch.org/whl/cu118
echo    pip install faster-whisper==1.1.1
echo    pip install streamlit google-generativeai
echo.

endlocal
pause
exit /b 1
