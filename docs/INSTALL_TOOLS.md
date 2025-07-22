# 🔧 工具安裝說明

由於 GitHub 檔案大小限制，專案不包含以下大型二進制檔案：
- `_internal/ffmpeg.exe` (~200MB)
- `_internal/yt-dlp.exe` (~20MB)

## 🚀 快速安裝

### 方法一：自動安裝（推薦）
```bash
# 運行安裝腳本（包含工具下載）
scripts/setup.bat
```

### 方法二：手動下載工具
```bash
# 只下載工具
python scripts/download_tools.py
```

### 方法三：手動安裝

1. **下載 FFmpeg**：
   - 訪問：https://github.com/BtbN/FFmpeg-Builds/releases
   - 下載：`ffmpeg-master-latest-win64-gpl.zip`
   - 解壓後將 `ffmpeg.exe` 放到 `_internal/` 目錄

2. **下載 yt-dlp**：
   - 訪問：https://github.com/yt-dlp/yt-dlp/releases
   - 下載：`yt-dlp.exe`
   - 放到 `_internal/` 目錄

## 📁 目錄結構

安裝完成後，`_internal/` 目錄應包含：
```
_internal/
├── ffmpeg.exe    # 影片/音訊處理工具
└── yt-dlp.exe    # YouTube 下載工具
```

## ⚠️ 注意事項

- 工具檔案總大小約 220MB
- 首次安裝需要網路連接
- Windows 環境專用（Linux/Mac 需修改下載連結）

## 🔍 疑難排解

### 問題：下載失敗
**解決方案**：
1. 檢查網路連接
2. 使用 VPN（如果存取 GitHub 有問題）
3. 手動下載並放置檔案

### 問題：工具無法執行
**解決方案**：
1. 確認檔案完整性
2. 檢查防毒軟體是否阻擋
3. 以管理員權限執行

### 問題：路徑錯誤
**解決方案**：
1. 確認檔案在正確位置
2. 重新運行安裝腳本
3. 檢查環境變數設定
