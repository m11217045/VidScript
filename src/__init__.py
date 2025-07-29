"""
YouTube 財經報告生成器 - 源碼包
"""
# 從根目錄的版本管理模組導入版本資訊
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from version import __version__, APP_NAME, APP_DESCRIPTION
    __all__ = ['__version__', 'APP_NAME', 'APP_DESCRIPTION']
except ImportError:
    # 如果無法導入版本模組，使用預設值
    __version__ = "1.2.0"
    APP_NAME = "YouTube 財經報告生成器"
    APP_DESCRIPTION = "使用 AI 技術將 YouTube 財經影片轉換為結構化報告"

__author__ = "Development Team"
