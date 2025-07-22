"""
測試腳本 - 驗證模組化重構後的系統
"""
import sys
import os

# 添加專案根目錄到 Python 路徑
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

try:
    print("🔄 測試模組匯入...")
    
    # 測試配置模組
    from src.core.config import AI_PROVIDERS, WHISPER_MODELS, YT_DLP_PATH, FFMPEG_PATH
    print("✅ Config 模組匯入成功")
    
    # 測試影片處理模組
    from src.services.video_processor import VideoProcessor
    device_info = VideoProcessor.check_device_availability()
    print(f"✅ VideoProcessor 模組匯入成功 - 設備狀態: {device_info}")
    
    # 測試 AI 服務模組
    from src.services.ai_service import AIService
    print("✅ AIService 模組匯入成功")
    
    # 測試檔案管理模組
    from src.utils.file_manager import FileManager
    print("✅ FileManager 模組匯入成功")
    
    # 測試業務邏輯模組
    from src.core.business_logic import BusinessLogic
    print("✅ BusinessLogic 模組匯入成功")
    
    # 檢查配置
    print(f"\n📋 配置檢查:")
    print(f"   AI 提供商: {list(AI_PROVIDERS.keys())}")
    print(f"   Whisper 模型: {list(WHISPER_MODELS.keys())}")
    print(f"   yt-dlp 路徑: {YT_DLP_PATH}")
    print(f"   FFmpeg 路徑: {FFMPEG_PATH}")
    
    print("\n🎉 模組化重構測試通過！系統準備就緒。")
    
except Exception as e:
    print(f"❌ 測試失敗: {e}")
    import traceback
    traceback.print_exc()
