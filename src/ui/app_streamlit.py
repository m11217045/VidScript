"""
YouTube 財經報告生成器
主程式入口點 - 使用模組化架構
"""
import os
import sys
import streamlit as st
from dotenv import load_dotenv

# 添加專案根目錄到 Python 路徑
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# 導入版本資訊
try:
    from version import get_app_title, get_full_version, APP_DESCRIPTION
except ImportError:
    # 如果無法導入版本模組，使用預設值
    def get_app_title():
        return "📊 YouTube 財經報告生成器 v1.2.0"
    def get_full_version():
        return "v1.2.0"
    APP_DESCRIPTION = "使用 AI 技術將 YouTube 財經影片轉換為結構化報告"

# 導入自定義模組
from src.core.config import AI_PROVIDERS, WHISPER_MODELS, LANGUAGE_OPTIONS
from src.services.video_processor import VideoProcessor
from src.core.business_logic import BusinessLogic
from src.utils.prompt_manager import PromptManager

# 設定編碼環境
import locale
try:
    locale.setlocale(locale.LC_ALL, 'zh_TW.UTF-8')
except:
    pass

# 載入環境變數
load_dotenv()


def main():
    """主應用程式"""
    st.set_page_config(
        page_title=get_app_title().replace("📊 ", ""),
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title(get_app_title())
    st.markdown(APP_DESCRIPTION)
    
    # 側邊欄設定
    with st.sidebar:
        st.header("⚙️ 設定")
        
        # 初始化 Prompt 管理器
        prompt_manager = PromptManager()
        
        # Prompt 選擇
        st.subheader("📝 Prompt選擇")
        available_prompts = prompt_manager.get_available_prompts()
        
        selected_prompt = st.selectbox(
            "選擇專家",
            available_prompts,
            index=0,
            help="選擇適合影片內容的專業分析師"
        )
        
        # 系統資訊
        st.subheader("🖥️ 系統資訊")
        device_info = VideoProcessor.check_device_availability()
        st.info(f"運算設備：{device_info}")
        
        # AI 設定
        st.subheader("🤖 AI 設定")
        ai_provider = st.selectbox(
            "選擇 Gemini 模型版本",
            list(AI_PROVIDERS.keys()),
            index=0,
            help="Pro: 最佳品質但較慢，Flash: 平衡性能，Flash Lite: 最快但基礎功能"
        )
        
        # 顯示選擇的模型資訊
        selected_model_value = AI_PROVIDERS[ai_provider]
        if "pro" in selected_model_value:
            st.success(f"🚀 已選擇: {selected_model_value} (最高品質)")
        elif "flash-lite" in selected_model_value:
            st.info(f"⚡ 已選擇: {selected_model_value} (最快速度)")
        else:
            st.info(f"⚖️ 已選擇: {selected_model_value} (平衡模式)")
        
        # API Key 設定
        default_api_key = os.getenv("GOOGLE_API_KEY", "")
        api_key = st.text_input(
            "API Key",
            value=default_api_key,
            type="password",
            help="輸入您的 AI API Key"
        )
        
        # 顯示逐字稿保存資訊
        st.info("💾 逐字稿將自動保存到 saved_transcripts 資料夾")
        
        # 固定儲存路徑到 main.py 所在目錄
        save_path = project_root
    
    # 主要內容區域
    col1, col2 = st.columns([2, 1])
    
    with col2: 
        # 移動的處理選項到右側
        st.subheader("🔧 處理選項")
        
        # Faster-Whisper 模型選擇
        whisper_model_display = st.selectbox(
            "選擇 Faster-Whisper 模型",
            list(WHISPER_MODELS.keys()),
            index=0,
            help="Base: 低 VRAM，Small: 中等 VRAM，Medium: 平衡"
        )
        whisper_model = WHISPER_MODELS[whisper_model_display]
        
        # 語言選擇
        language_display = st.selectbox(
            "選擇語音語言",
            list(LANGUAGE_OPTIONS.keys()),
            index=0,  # 默認選擇自動檢測
            help="建議使用自動檢測，系統會智慧識別中文或英文內容"
        )
        language = LANGUAGE_OPTIONS[language_display]

        # Cookie 檔案上傳
        st.write("**🍪 Cookie 檔案 (選填)**")
        cookie_file = st.file_uploader(
            "上傳 Cookie 檔案",
            type=['txt'],
            help="用於存取需要登入的影片",
            key="cookie_file_uploader"
        )

    with col1:
        st.subheader("📄 內容來源選擇")
        
        # 輸入模式選擇
        input_mode = st.radio(
            "選擇輸入方式",
            ["YouTube 影片", "逐字稿檔案"],
            index=0,
            horizontal=True,
            help="選擇要處理YouTube影片還是直接上傳逐字稿檔案"
        )
        
        youtube_url = None
        transcript_file = None
        
        if input_mode == "YouTube 影片":
            st.subheader("🎥 YouTube 影片處理")
            youtube_url = st.text_input(
                "輸入 YouTube 影片網址",
                placeholder="https://www.youtube.com/watch?v=...",
                help="貼上要處理的 YouTube 影片連結"
            )
        else:
            st.subheader("📄 逐字稿檔案處理")
            
            # 檢查已保存的逐字稿
            transcripts_folder = "saved_transcripts"
            saved_transcripts = []
            if os.path.exists(transcripts_folder):
                saved_transcripts = [f for f in os.listdir(transcripts_folder) if f.endswith('.txt')]
            
            # 逐字稿來源選擇
            transcript_source = st.radio(
                "逐字稿來源",
                ["上傳新檔案", "選擇已保存的逐字稿"] if saved_transcripts else ["上傳新檔案"],
                index=0,
                horizontal=True,
                help="選擇使用新上傳的檔案或之前保存的逐字稿"
            )
            
            transcript_file = None
            selected_saved_transcript = None
            
            if transcript_source == "上傳新檔案":
                transcript_file = st.file_uploader(
                    "上傳逐字稿檔案",
                    type=['txt', 'md'],
                    help="上傳包含影片內容逐字稿的文字檔案"
                )
            else:
                if saved_transcripts:
                    # 按修改時間排序，最新的在前面
                    saved_transcripts_with_time = []
                    for filename in saved_transcripts:
                        filepath = os.path.join(transcripts_folder, filename)
                        mtime = os.path.getmtime(filepath)
                        saved_transcripts_with_time.append((filename, mtime))
                    
                    saved_transcripts_sorted = [item[0] for item in sorted(saved_transcripts_with_time, key=lambda x: x[1], reverse=True)]
                    
                    selected_saved_transcript = st.selectbox(
                        "選擇已保存的逐字稿",
                        saved_transcripts_sorted,
                        help="選擇要重新處理的逐字稿檔案（按修改時間排序，最新的在前面）"
                    )
                else:
                    st.info("尚無已保存的逐字稿檔案")
        
        # 開始處理按鈕
        if st.button("🚀 開始生成報告", type="primary", use_container_width=True):
            if input_mode == "YouTube 影片":
                if not youtube_url or not youtube_url.strip():
                    st.error("❌ 請輸入 YouTube 影片網址")
                elif not api_key.strip():
                    st.error("❌ 請輸入 AI API Key（進行AI修飾時需要）")
                else:
                    # YouTube 影片處理邏輯
                    # 準備 Cookie 檔案
                    cookie_path = BusinessLogic.prepare_cookie_file(cookie_file)
                    
                    # 獲取選中的 prompt
                    selected_prompt_content = prompt_manager.get_prompt_content(selected_prompt)
                    
                    # 獲取選擇的 AI 模型
                    selected_ai_model = AI_PROVIDERS[ai_provider]
                    
                    # 開始處理
                    BusinessLogic.process_video(
                        youtube_url.strip(),
                        api_key.strip(),
                        save_path,
                        cookie_path,
                        whisper_model,
                        selected_prompt_content,
                        language,
                        selected_ai_model
                    )
            else:
                # 檢查是否有逐字稿輸入
                has_transcript_input = False
                if transcript_source == "上傳新檔案":
                    has_transcript_input = transcript_file is not None
                else:
                    has_transcript_input = selected_saved_transcript is not None
                
                if not has_transcript_input:
                    st.error("❌ 請選擇或上傳逐字稿檔案")
                elif not api_key.strip():
                    st.error("❌ 請輸入 AI API Key（進行AI修飾時需要）")
                else:
                    # 逐字稿檔案處理邏輯
                    # 獲取選中的 prompt
                    selected_prompt_content = prompt_manager.get_prompt_content(selected_prompt)
                    
                    # 獲取選擇的 AI 模型
                    selected_ai_model = AI_PROVIDERS[ai_provider]
                    
                    # 根據來源處理逐字稿
                    if transcript_source == "上傳新檔案":
                        # 處理上傳的檔案
                        BusinessLogic.process_transcript_file(
                            transcript_file,
                            api_key.strip(),
                            save_path,
                            selected_prompt_content,
                            selected_ai_model
                        )
                    else:
                        # 處理已保存的逐字稿
                        BusinessLogic.process_saved_transcript(
                            selected_saved_transcript,
                            api_key.strip(),
                            save_path,
                            selected_prompt_content,
                            selected_ai_model
                        )


if __name__ == "__main__":
    main()
