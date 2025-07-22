"""
YouTube 財經報告生成器 v3.0
主程式入口點
"""
import sys
import os

# 添加 src 目錄到 Python 路徑
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.ui.app_streamlit import main

if __name__ == "__main__":
    main()
