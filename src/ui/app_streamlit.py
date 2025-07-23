"""
YouTube 財經報告生成器 v1.0.0
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

# 導入自定義模組
from src.core.config import AI_PROVIDERS, WHISPER_MODELS
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
        page_title="YouTube 財經報告生成器",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("📊 YouTube 財經報告生成器 v1.0.0")
    st.markdown("使用 AI 技術將 YouTube 財經影片轉換為結構化報告")
    
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
            "選擇 AI 提供商",
            list(AI_PROVIDERS.keys()),
            index=0
        )
        
        # API Key 設定
        default_api_key = os.getenv("GOOGLE_API_KEY", "")
        api_key = st.text_input(
            "API Key",
            value=default_api_key,
            type="password",
            help="輸入您的 AI API Key"
        )
        
        # Cookie 檔案上傳
        st.subheader("🍪 Cookie 檔案 (選填)")
        cookie_file = st.file_uploader(
            "上傳 Cookie 檔案",
            type=['txt'],
            help="用於存取需要登入的影片"
        )
        
        # 處理選項
        st.subheader("🔧 處理選項")
        
        # Faster-Whisper 模型選擇
        whisper_model_display = st.selectbox(
            "選擇 Faster-Whisper 模型",
            list(WHISPER_MODELS.keys()),
            index=0,
            help="Tiny: 最低 VRAM，Base: 低 VRAM，Small: 中等 VRAM，Medium: 平衡，Large: 高精度高 VRAM"
        )
        whisper_model = WHISPER_MODELS[whisper_model_display]
        
        delete_transcript = st.checkbox(
            "處理完成後刪除逐字稿檔案",
            value=True,
            help="取消勾選以保留逐字稿檔案"
        )
        
        # 儲存路徑
        save_path = st.text_input(
            "報告儲存路徑",
            value=os.path.dirname(os.path.abspath(__file__)),
            help="報告檔案的儲存位置"
        )
    
    # 主要內容區域
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("🎥 YouTube 影片處理")
        youtube_url = st.text_input(
            "輸入 YouTube 影片網址",
            placeholder="https://www.youtube.com/watch?v=...",
            help="貼上要處理的 YouTube 影片連結"
        )
        
        # 開始處理按鈕
        if st.button("🚀 開始生成報告", type="primary", use_container_width=True):
            if not youtube_url.strip():
                st.error("❌ 請輸入 YouTube 影片網址")
            elif not api_key.strip():
                st.error("❌ 請輸入 AI API Key")
            else:
                # 準備 Cookie 檔案
                cookie_path = BusinessLogic.prepare_cookie_file(cookie_file)
                
                # 獲取選中的 prompt
                selected_prompt_content = prompt_manager.get_prompt_content(selected_prompt)
                
                # 開始處理
                BusinessLogic.process_video(
                    youtube_url.strip(),
                    api_key.strip(),
                    delete_transcript,
                    save_path,
                    cookie_path,
                    whisper_model,
                    selected_prompt_content
                )
    
    with col2:
        st.subheader("📋 使用說明")
        st.markdown("""
        ### 步驟：
        1. **選擇專家**: 在左側選擇適合的分析專家
        2. **設定 AI**: 選擇 AI 提供商並輸入 API Key
        3. **輸入網址**: 貼上 YouTube 影片連結
        4. **選填設定**: 上傳 Cookie 檔案（如需要）
        5. **開始處理**: 點擊生成報告按鈕
        
        ### 功能特色：
        - 🎯 **智慧字幕優先**: 優先使用 YouTube 字幕
        - 🎤 **語音轉文字**: Faster-Whisper (VRAM 優化)
        - 🤖 **AI 潤飾**: 支援 Gemini
        - ⚡ **GPU 加速**: 自動檢測 CUDA 支援
        - 📄 **專業報告**: 依專家類型產生結構化報告
        """)


if __name__ == "__main__":
    main()
