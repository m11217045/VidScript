# YouTube 財經報告生成器 v3.0 - 模組化架構

## 📁 專案結構

```
YT_2.0/
├── app_streamlit.py          # 主程式入口點
├── config.py                 # 配置管理模組
├── video_processor.py        # 影片處理模組
├── ai_service.py             # AI 服務模組  
├── file_manager.py           # 檔案管理模組
├── business_logic.py         # 業務邏輯模組
├── test_modules.py           # 模組測試腳本
└── requirements.txt          # 依賴套件清單
```

## 🏗️ 模組說明

### 1. `config.py` - 配置管理
- 統一管理所有配置參數和常數
- 包含檔案名稱、AI 模型選項、路徑設定等
- 集中化配置便於維護和修改

### 2. `video_processor.py` - 影片處理
- `VideoProcessor` 類別處理所有影片相關功能
- 字幕檢查和下載
- 音訊下載和轉錄
- 設備檢測和 Whisper 處理

### 3. `ai_service.py` - AI 服務
- `AIService` 類別管理 AI 相關功能
- Gemini API 調用
- 報告生成和優化
- 錯誤處理和重試機制

### 4. `file_manager.py` - 檔案管理
- `FileManager` 類別處理檔案操作
- VTT 字幕轉換
- 臨時檔案清理
- Prompt 檔案管理

### 5. `business_logic.py` - 業務邏輯
- `BusinessLogic` 類別協調各模組
- 主要處理流程控制
- 結果顯示和錯誤處理
- Cookie 檔案準備

### 6. `app_streamlit.py` - 主程式
- Streamlit UI 界面
- 用戶輸入處理
- 模組間協調
- 精簡的主程式邏輯

## ✨ 重構優勢

### 🔧 **可維護性提升**
- 每個模組職責單一，易於理解和修改
- 降低模組間耦合度
- 便於單元測試和除錯

### 📦 **可擴展性增強**
- 新功能可在對應模組中添加
- 易於替換或升級特定功能
- 支援插件式開發

### 🛡️ **錯誤隔離**
- 模組間錯誤不會互相影響
- 更好的錯誤追蹤和處理
- 提高系統穩定性

### 🚀 **開發效率**
- 團隊可並行開發不同模組
- 代碼重用性提高
- 減少重複代碼

## 🧪 測試

執行測試腳本驗證所有模組：

```bash
python test_modules.py
```

## 🔄 使用方式

1. **啟動應用程式**：
   ```bash
   streamlit run app_streamlit.py
   ```

2. **導入模組**（用於開發）：
   ```python
   from config import AI_PROVIDERS
   from video_processor import VideoProcessor
   from ai_service import AIService
   ```

## 📈 未來擴展

基於新的模組化架構，可以輕鬆添加：
- 新的 AI 提供商（在 `ai_service.py` 中）
- 新的影片平台支援（在 `video_processor.py` 中）
- 新的檔案格式支援（在 `file_manager.py` 中）
- 新的業務流程（在 `business_logic.py` 中）
