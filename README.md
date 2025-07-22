# YouTube 財經報告生成器 v1.0.0

## 📁 專業團隊級專案結構

```
YT_2.0/
├── 📁 src/                     # 源碼目錄
│   ├── 📁 core/               # 核心模組
│   │   ├── config.py          # 配置管理
│   │   ├── business_logic.py  # 業務邏輯
│   │   └── __init__.py        
│   ├── 📁 services/           # 服務模組
│   │   ├── ai_service.py      # AI 服務
│   │   ├── video_processor.py # 影片處理服務
│   │   └── __init__.py        
│   ├── 📁 utils/              # 工具模組
│   │   ├── file_manager.py    # 檔案管理工具
│   │   └── __init__.py        
│   ├── 📁 ui/                 # 用戶界面
│   │   ├── app_streamlit.py   # Streamlit 應用
│   │   └── __init__.py        
│   └── __init__.py            
├── 📁 config/                 # 配置檔案
│   ├── prompt.txt             # AI 提示模板
│   └── requirements.txt       # 依賴清單
├── 📁 scripts/                # 腳本工具
│   ├── setup.bat              # 環境設置腳本
│   ├── Setup_AutoStart.bat    # 自動啟動設置
│   ├── Start_Streamlit_Hidden.vbs # 隱藏啟動
│   ├── Stop_Streamlit.bat     # 停止服務
│   └── quick_stop.bat         # 快速停止
├── 📁 tools/                  # 工具程式
│   ├── background_launcher.py # 後台啟動器
│   └── stop_streamlit.py      # 停止服務工具
├── 📁 tests/                  # 測試檔案
│   └── test_modules.py        # 模組測試
├── 📁 docs/                   # 文檔資料
│   └── README_MODULES.md      # 模組說明
├── 📁 logs/                   # 日誌檔案
├── 📁 _internal/              # 內部工具
│   ├── ffmpeg.exe             # 影片處理工具
│   └── yt-dlp.exe             # YouTube 下載工具
├── main.py                    # 主程式入口
├── .env                       # 環境變數
├── .gitignore                 # Git 忽略檔案
└── venv/                      # 虛擬環境
```

## 🏗️ 架構設計原則

### 1. **分層架構 (Layered Architecture)**
- **UI 層** (`src/ui/`): 用戶界面和交互
- **服務層** (`src/services/`): 業務服務和外部 API
- **核心層** (`src/core/`): 核心業務邏輯和配置
- **工具層** (`src/utils/`): 通用工具和輔助功能

### 2. **關注點分離 (Separation of Concerns)**
- 每個模組職責單一且明確
- 模組間低耦合，高內聚
- 易於測試和維護

### 3. **可擴展性設計**
- 新功能可在對應層級添加
- 支援插件式開發
- 易於水平和垂直擴展

## 🚀 快速開始

### 🎯 一鍵安裝（推薦）

```bash
# 步驟1：完整環境安裝
scripts/setup.bat

# 步驟2：啟動應用程式
scripts/Setup_AutoStart.bat
```

⚠️ **重要提醒**：
- 首次運行會自動下載 FFmpeg 和 yt-dlp 工具
- 請確保已在 `.env` 檔案中設定您的 Google API Key
- Setup_AutoStart.bat 會設定開機自動啟動並立即啟動應用程式

### 📱 使用方法
完成安裝後，應用程式會自動在瀏覽器中開啟：
- 🌐 訪問地址：http://localhost:8501
- 🔄 開機自動啟動已設定完成

### 🛠️ 進階選項

```bash
# 手動運行（開發用）
python main.py
# 或
streamlit run src/ui/app_streamlit.py

# 僅下載工具
python scripts/download_tools.py

# 停止服務
scripts/Stop_Streamlit.bat
```

### 🔧 開發環境設置
```bash
# 安裝依賴（已包含在 setup.bat 中）
pip install -r config/requirements.txt

# 運行測試
python tests/test_modules.py
```

## 📋 API 設定

### Google Gemini API 設定
1. 前往 [Google AI Studio](https://makersuite.google.com/app/apikey)
2. 創建 API Key
3. 編輯 `.env` 檔案：
```bash
GOOGLE_API_KEY = "您的_API_KEY_這裡"
```

### 🔄 服務管理

```bash
# 啟動服務
scripts/Setup_AutoStart.bat

# 停止服務
scripts/Stop_Streamlit.bat

# 快速停止
scripts/quick_stop.bat
```

## 🔧 開發指南

### 添加新功能
1. **AI 服務擴展**: 在 `src/services/ai_service.py` 中添加
2. **新的處理流程**: 在 `src/core/business_logic.py` 中實現
3. **工具函數**: 在 `src/utils/` 中創建新模組
4. **UI 組件**: 在 `src/ui/` 中擴展

### 配置管理
- 應用配置: `src/core/config.py`
- 環境變數: `.env`
- 外部配置: `config/` 目錄

### 測試策略
- 單元測試: `tests/` 目錄
- 集成測試: 使用 `test_modules.py`
- 手動測試: 通過 UI 界面

## 📊 專案優勢

### ✅ **專業標準**
- 符合企業級開發規範
- 清晰的目錄結構
- 完整的文檔和註釋

### ✅ **團隊協作**
- 模組化設計便於分工
- 標準化代碼組織
- 版本控制友好

### ✅ **維護性**
- 易於理解和修改
- 降低技術債務
- 支援持續集成

### ✅ **可擴展性**
- 插件式架構
- 微服務就緒
- 雲原生部署支援
