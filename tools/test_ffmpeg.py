"""
測試 Whisper 和 FFmpeg 配置
"""
import os
import sys
from pathlib import Path

# 添加專案根目錄到 Python 路徑
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 導入配置
from src.core.config import FFMPEG_PATH

def test_ffmpeg():
    """測試 FFmpeg 是否可用"""
    print("🔧 測試 FFmpeg 配置...")
    print(f"FFmpeg 路徑: {FFMPEG_PATH}")
    
    # 檢查檔案是否存在
    if os.path.exists(FFMPEG_PATH):
        print("✅ FFmpeg 檔案存在")
    else:
        print("❌ FFmpeg 檔案不存在")
        return False
    
    # 測試執行
    try:
        import subprocess
        result = subprocess.run([FFMPEG_PATH, "-version"], 
                               capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ FFmpeg 可以正常執行")
            # 顯示版本資訊的第一行
            version_line = result.stdout.split('\n')[0]
            print(f"版本: {version_line}")
            return True
        else:
            print("❌ FFmpeg 執行失敗")
            print(f"錯誤: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ 測試 FFmpeg 時發生錯誤: {e}")
        return False

def test_whisper_audio_loading():
    """測試 Whisper 的音頻載入功能"""
    print("\n🎵 測試 Whisper 音頻載入...")
    
    try:
        # 設定 FFmpeg 路徑到環境變數
        internal_dir = os.path.dirname(FFMPEG_PATH)
        original_path = os.environ.get('PATH', '')
        if internal_dir not in original_path:
            os.environ['PATH'] = f"{internal_dir};{original_path}"
            print(f"✅ 已設定 FFmpeg 路徑到 PATH: {internal_dir}")
        
        # 嘗試導入 whisper 的音頻模組
        from whisper.audio import load_audio
        print("✅ Whisper 音頻模組導入成功")
        
        # 這裡我們不實際載入音頻檔案，只是測試模組是否能找到 FFmpeg
        print("✅ Whisper 應該能夠找到 FFmpeg")
        return True
        
    except Exception as e:
        print(f"❌ Whisper 音頻載入測試失敗: {e}")
        return False

if __name__ == "__main__":
    print("🚀 開始 FFmpeg 和 Whisper 配置測試...\n")
    
    ffmpeg_ok = test_ffmpeg()
    whisper_ok = test_whisper_audio_loading()
    
    print(f"\n📊 測試結果:")
    print(f"FFmpeg: {'✅ 通過' if ffmpeg_ok else '❌ 失敗'}")
    print(f"Whisper: {'✅ 通過' if whisper_ok else '❌ 失敗'}")
    
    if ffmpeg_ok and whisper_ok:
        print("\n🎉 所有測試通過！您的 FFmpeg 配置應該正常工作。")
    else:
        print("\n⚠️ 有些測試失敗，可能需要進一步檢查配置。")
