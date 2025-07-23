# VidScript - 智能影片分析工具 🎥

> � **已升級至 Faster-Whisper**: 享受 7-40x 的 GPU 加速轉錄性能！

VidScript 是一個強大的影片內容分析工具，結合了先進的語音轉文字技術和 AI 分析能力，能夠自動下載 YouTube 影片、提取音訊、轉錄文字，並生成深度分析報告。

## ✨ 核心功能

- 🎬 **YouTube 影片下載**: 自動下載並處理 YouTube 影片
- 🎙️ **高速語音轉文字**: 使用 Faster-Whisper + GPU 加速 (7-40x 性能提升)
- 🧠 **智能分析**: Google Gemini AI 驅動的內容分析
- 📊 **多種專家角色**: 財經、科技、料理、教學等專業分析師
- 🖥️ **直觀介面**: Streamlit 網頁界面，操作簡單
- ⚡ **性能優化**: RTX 3060 GPU 加速，快速處理

## 🏗️ 專案架構

```
VidScript/
├── 📁 src/                    # 核心源碼
│   ├── 📁 core/              # 核心模組 (配置、業務邏輯)
│   ├── 📁 services/          # 服務模組 (AI、影片處理)
│   ├── 📁 ui/               # 使用者界面 (Streamlit)
│   └── 📁 utils/            # 工具函數
├── 📁 config/               # 配置檔案
├── 📁 scripts/              # 自動化腳本
├── 📁 tools/                # 開發工具
├── 📁 prompts/              # AI 提示範本
├── 📁 _internal/            # 內建工具 (ffmpeg, yt-dlp)
├── main.py                  # 主程式入口
└── test_speed.py           # 性能測試工具
```

## ⚡ 快速開始

### 📋 系統需求

- **作業系統**: Windows 10/11
- **Python**: 3.8+ (建議 3.11)
- **GPU**: NVIDIA RTX 系列 (建議 8GB+ VRAM)
- **網路**: 穩定的網路連線 (用於下載 YouTube 影片)

### 🎯 一鍵安裝 (推薦)

```bash
# 步驟1: 完整環境安裝
scripts\setup.bat

# 步驟2: 啟動應用程式
scripts\Setup_AutoStart.bat
```

**安裝完成後**: 應用程式會自動在瀏覽器開啟 `http://localhost:8501`

### � 手動安裝

```bash
# 1. 安裝 Python 依賴
pip install -r config\requirements.txt

# 2. 設定環境變數 (複製 .env.example 為 .env)
copy .env.example .env

# 3. 啟動應用
streamlit run src\ui\app_streamlit.py
```

## �️ API 設定

### Google Gemini API
1. 前往 [Google AI Studio](https://makersuite.google.com/app/apikey)
2. 創建新的 API Key
3. 編輯 `.env` 檔案：
```
GOOGLE_API_KEY=your_api_key_here
```

## 📖 使用說明

### 基本操作流程

1. **啟動應用**: 運行 `scripts\Setup_AutoStart.bat`
2. **開啟網頁**: 瀏覽器會自動開啟 http://localhost:8501
3. **輸入影片連結**: 貼上 YouTube 影片 URL
4. **選擇分析角色**: 財經專家、科技專家、料理專家等
5. **開始分析**: 點擊「開始分析」按鈕
6. **查看結果**: 等待處理完成，檢視分析報告

### 專家角色選項

- 🏦 **財經專家**: 投資分析、市場觀察、經濟評論
- 💻 **科技專家**: 技術分析、產品評測、趨勢解讀  
- 🍳 **料理專家**: 食譜分析、烹飪技巧、營養建議
- 📚 **教學專家**: 課程內容、學習重點、知識整理
- 📊 **通用分析師**: 綜合分析、重點摘要、全面評估

### 性能監控

系統會顯示：
- 🎯 GPU 使用狀況
- ⏱️ 處理時間統計
- 📊 轉錄品質指標
- 💾 記憶體使用情況

## 🚀 性能優勢

| 功能項目 | 升級前 | 升級後 | 提升幅度 |
|---------|-------|-------|---------|
| **語音轉文字** | OpenAI Whisper | Faster-Whisper | **7-40x** 🔥 |
| **GPU 加速** | 基本支援 | 完全優化 | **極大提升** |
| **記憶體效率** | 高佔用 | 極低佔用 | **節省 80%+** |
| **轉錄準確度** | 98% | 98%+ | **維持/提升** |

## �️ 進階功能

### 服務控制

```bash
# 啟動服務
scripts\Setup_AutoStart.bat

# 停止服務  
scripts\Stop_Streamlit.bat

# 性能測試
python test_speed.py
```

### 開發模式

```bash
# 直接運行主程式
python main.py

# 僅啟動 Streamlit
streamlit run src\ui\app_streamlit.py

# 執行測試
python tests\test_modules.py
```

## 🔧 故障排除

### 常見問題

**Q: GPU 未被正確使用？**
A: 確認已安裝 CUDA 並運行性能測試檢查

**Q: 下載影片失敗？**  
A: 檢查網路連線和 YouTube 連結有效性

**Q: API 調用失敗？**
A: 驗證 Google API Key 是否正確設定

**Q: 應用無法啟動？**
A: 確認 Python 環境和依賴已正確安裝

### 性能測試

```bash
# 運行完整性能測試
python test_speed.py

# 檢查系統配置
python tools\check_environment.py
```

## 📊 專案特色

### ✅ **高性能**
- Faster-Whisper GPU 加速
- 智能記憶體管理
- 多模型自動選擇

### ✅ **易用性**  
- 一鍵安裝配置
- 直觀網頁界面
- 自動化處理流程

### ✅ **專業性**
- 多角色專家分析  
- 深度內容理解
- 結構化輸出報告

### ✅ **可靠性**
- 錯誤處理機制
- 進度追蹤顯示
- 完整日誌記錄

---

## 📞 技術支援

如需協助，請查看：
- 執行 `python tools\check_environment.py` 檢查環境
- 運行 `python test_speed.py` 測試性能  
- 查看應用內的錯誤訊息和建議

**享受您的高速智能影片分析體驗！** 🚀
