"""
配置管理模組
統一管理所有配置參數和常數
"""
import os

# 檔案名稱配置
AUDIO_FILENAME = "_temp_audio.mp3"
TRANSCRIPT_FILENAME = "_temp_transcript.txt"
SUBTITLE_FILENAME = "_temp_subtitle.vtt"
DEFAULT_REPORT_NAME = "youtube_report"

# 逐字稿儲存配置
TRANSCRIPTS_FOLDER = "saved_transcripts"

# AI 模型選項
AI_PROVIDERS = {
    "gemini-2.5-pro": "gemini-2.5-pro",
    "gemini-2.5-flash": "gemini-2.5-flash",
    "gemini-2.5-flash-lite": "gemini-2.5-flash-lite"
}

# Faster-Whisper 模型選項（針對 VRAM 優化）
WHISPER_MODELS = {
    "Base (低 VRAM)": "base",
    "Small (中等 VRAM)": "small", 
    "Medium (平衡)": "medium"
}

# 語言選項配置
LANGUAGE_OPTIONS = {
    "自動檢測": None,
    "中文": "zh",
    "英文": "en"
}

# 環境變數設定
os.environ["PYTHONIOENCODING"] = "utf-8"
os.environ["PYTHONUTF8"] = "1"
os.environ["TQDM_DISABLE"] = "1"

# 獲取可執行檔案路徑
SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
INTERNAL_DIR = os.path.join(SCRIPT_DIR, "_internal")
YT_DLP_PATH = os.path.join(INTERNAL_DIR, "yt-dlp.exe")
FFMPEG_PATH = os.path.join(INTERNAL_DIR, "ffmpeg.exe")

# 字幕語言優先順序
SUBTITLE_LANGUAGES = ['zh-TW', 'zh-CN', 'zh', 'en']
SUPPORTED_LANGUAGES = ['zh', 'en']
