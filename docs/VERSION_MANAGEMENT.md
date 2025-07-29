# VidScript 版本管理指南

## 概述

VidScript 使用專業的語義化版本控制（Semantic Versioning），提供統一的版本管理系統。

## 版本號格式

使用 `MAJOR.MINOR.PATCH` 格式：
- **MAJOR**: 不兼容的 API 變更
- **MINOR**: 向後兼容的功能新增  
- **PATCH**: 向後兼容的錯誤修復

## 使用方法

### 1. 查看當前版本
```bash
# 使用批次檔案（推薦）
scripts\version.bat current

# 或直接使用 Python
python tools\version_manager.py --current
```

### 2. 增加版本號

#### 修復版本（1.2.0 → 1.2.1）
```bash
scripts\version.bat increment patch "修復音訊下載錯誤" "改進錯誤提示"
```

#### 功能版本（1.2.0 → 1.3.0）
```bash
scripts\version.bat increment minor "新增批次處理功能" "支援更多語言"
```

#### 重大版本（1.2.0 → 2.0.0）
```bash
scripts\version.bat increment major "重構核心架構" "API 重大變更"
```

### 3. 設定特定版本
```bash
scripts\version.bat set 2.0.0 "重大版本發布"
```

### 4. 發布新版本（推薦）
```bash
# 自動增加版本號、創建 Git 標籤、生成變更日誌
scripts\version.bat release patch "修復bug" "效能改進"
scripts\version.bat release minor "新功能" "界面改進"
```

### 5. 生成變更日誌
```bash
scripts\version.bat changelog
```

## 檔案結構

```
VidScript/
├── version.py              # 版本資訊中心（單一真相來源）
├── setup.py               # 套件安裝配置
├── CHANGELOG.md           # 自動生成的變更日誌
├── tools/
│   └── version_manager.py # 版本管理工具
└── scripts/
    └── version.bat        # Windows 批次工具
```

## 最佳實踐

### 1. 發布流程
1. 開發功能或修復
2. 更新版本號：`scripts\version.bat release minor "新功能描述"`
3. 推送到倉庫：`git push origin master --tags`

### 2. 版本號規則
- **補丁版本**：錯誤修復、性能改進、文檔更新
- **次要版本**：新功能、非破壞性改進、新增API
- **主要版本**：破壞性變更、重構、移除功能

### 3. 發布說明規則
- 使用現在式：「新增」而非「新增了」
- 描述具體：「修復音訊下載錯誤」而非「修復bug」
- 分類清楚：功能、修復、改進

## 自動化功能

- **統一版本源**：所有檔案從 `version.py` 獲取版本資訊
- **自動更新**：更新版本時自動同步所有相關檔案
- **Git 整合**：自動創建版本標籤
- **變更日誌**：自動生成和維護 CHANGELOG.md

## 範例工作流程

```bash
# 1. 查看當前狀態
scripts\version.bat current

# 2. 開發新功能後發布
scripts\version.bat release minor "新增語音識別" "支援更多格式"

# 3. 推送到倉庫
git add .
git commit -m "Release v1.3.0: 新增語音識別功能"
git push origin master --tags
```

這樣的版本管理系統確保了：
- ✅ 版本號一致性
- ✅ 自動化發布流程
- ✅ 清晰的版本歷史
- ✅ 專業的開發實踐
