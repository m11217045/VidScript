"""
VidScript 版本管理模組
使用語義化版本控制 (Semantic Versioning)
版本格式: MAJOR.MINOR.PATCH

版本歷史:
- 1.0.0: 初始版本，基本功能完成
- 1.1.0: 新增逐字稿保存功能，語言選擇功能  
- 1.2.0: 新增已保存逐字稿重新分析功能
"""

# 版本資訊 - 單一真相來源
__version__ = "1.2.1"
__version_info__ = tuple(map(int, __version__.split(".")))

# 詳細版本資訊
VERSION_MAJOR = __version_info__[0]
VERSION_MINOR = __version_info__[1]
VERSION_PATCH = __version_info__[2]

# 應用程式資訊
APP_NAME = "YouTube 財經報告生成器"
APP_NAME_EN = "YouTube Financial Report Generator"
APP_DESCRIPTION = "使用 AI 技術將 YouTube 財經影片轉換為結構化報告"

# 版本狀態
VERSION_STATUS = "stable"  # alpha, beta, rc, stable

def get_version():
    """獲取完整版本字符串"""
    return __version__

def get_version_info():
    """獲取版本資訊元組"""
    return __version_info__

def get_full_version():
    """獲取包含狀態的完整版本"""
    if VERSION_STATUS == "stable":
        return f"v{__version__}"
    else:
        return f"v{__version__}-{VERSION_STATUS}"

def get_app_title():
    """獲取應用程式標題"""
    return f"📊 {APP_NAME} {get_full_version()}"

def get_app_title_en():
    """獲取英文應用程式標題"""
    return f"{APP_NAME_EN} {get_full_version()}"

def is_stable():
    """檢查是否為穩定版本"""
    return VERSION_STATUS == "stable"

def compare_version(other_version):
    """
    比較版本號
    返回: 1 (當前版本較新), 0 (相同), -1 (當前版本較舊)
    """
    try:
        other_info = tuple(map(int, other_version.split(".")))
        if __version_info__ > other_info:
            return 1
        elif __version_info__ == other_info:
            return 0
        else:
            return -1
    except (ValueError, IndexError):
        return None

# 版本發布資訊
RELEASE_NOTES = {
    "1.3.0": [
        "新增批次處理功能",
        "支援多檔案上傳",
        "改進用戶介面"
    ],
    "1.2.1": [
        "修復音訊處理錯誤",
        "改進錯誤提示訊息"
    ],
    "1.2.0": [
        "新增已保存逐字稿重新分析功能",
        "改進用戶界面，新增逐字稿來源選擇",
        "優化版本號管理系統",
        "修復多個小問題"
    ],
    "1.1.0": [
        "新增逐字稿自動保存功能",
        "新增語言選擇選項（中文/英文/自動檢測）",
        "優化語音識別準確度",
        "改進多執行緒下載性能"
    ],
    "1.0.0": [
        "初始版本發布",
        "支援 YouTube 影片下載和轉錄",
        "整合 Faster-Whisper 語音識別",
        "支援 Gemini AI 報告生成",
        "模組化架構設計"
    ]
}

def get_release_notes(version=None):
    """獲取版本發布說明"""
    if version is None:
        version = __version__
    return RELEASE_NOTES.get(version, ["暫無發布說明"])

if __name__ == "__main__":
    # 版本資訊測試
    print(f"當前版本: {get_version()}")
    print(f"完整版本: {get_full_version()}")
    print(f"版本狀態: {VERSION_STATUS}")
    print(f"應用標題: {get_app_title()}")
    print(f"穩定版本: {is_stable()}")
    print("\n最新發布說明:")
    for note in get_release_notes():
        print(f"  • {note}")
