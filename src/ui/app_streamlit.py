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
            help="Base: 低 VRAM，Small: 中等 VRAM，Medium: 平衡"
        )
        whisper_model = WHISPER_MODELS[whisper_model_display]
        
        # 顯示逐字稿保存資訊
        st.info("💾 逐字稿將自動保存到 saved_transcripts 資料夾")
        
        # 儲存路徑
        try:
            default_save_path = os.path.dirname(os.path.abspath(__file__))
            if not default_save_path:
                default_save_path = os.getcwd()
        except Exception:
            default_save_path = os.getcwd()
            
        save_path = st.text_input(
            "報告儲存路徑",
            value=default_save_path,
            help="報告檔案的儲存位置"
        )
        
        # 確保路徑有效
        if not save_path or (isinstance(save_path, str) and save_path.strip() == ""):
            save_path = default_save_path
            
        # 最終安全檢查
        if not save_path:
            save_path = os.getcwd()
    
    # 主要內容區域
    col1, col2 = st.columns([2, 1])
    
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
            st.subheader("📄 逐字稿檔案上傳")
            transcript_file = st.file_uploader(
                "上傳逐字稿檔案",
                type=['txt', 'md'],
                help="上傳包含影片內容逐字稿的文字檔案"
            )
        
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
                    
                    # 開始處理
                    BusinessLogic.process_video(
                        youtube_url.strip(),
                        api_key.strip(),
                        save_path,
                        cookie_path,
                        whisper_model,
                        selected_prompt_content
                    )
            else:
                if not transcript_file:
                    st.error("❌ 請上傳逐字稿檔案")
                elif not api_key.strip():
                    st.error("❌ 請輸入 AI API Key（進行AI修飾時需要）")
                else:
                    # 逐字稿檔案處理邏輯
                    # 獲取選中的 prompt
                    selected_prompt_content = prompt_manager.get_prompt_content(selected_prompt)
                    
                    # 開始處理逐字稿
                    BusinessLogic.process_transcript_file(
                        transcript_file,
                        api_key.strip(),
                        save_path,
                        selected_prompt_content
                    )
    
    with col2:
        st.subheader("📋 使用說明")
        st.markdown("""
        ### 步驟：
        1. **選擇專家**: 在左側選擇適合的分析專家
        2. **設定 AI**: 選擇 AI 提供商並輸入 API Key
        3. **選擇輸入方式**: 
           - **YouTube 影片**: 貼上影片連結自動提取內容
           - **逐字稿檔案**: 直接上傳文字檔案
        4. **選填設定**: 上傳 Cookie 檔案（YouTube模式需要時）
        5. **開始處理**: 點擊生成報告按鈕
        
        ### 功能特色：
        - 🎯 **雙重輸入模式**: YouTube影片 + 逐字稿檔案
        - 🎤 **語音轉文字**: Faster-Whisper (VRAM 優化)
        - 🤖 **AI 潤飾**: 支援 Gemini 進行專業報告生成
        - ⚡ **GPU 加速**: 自動檢測 CUDA 支援
        - 📄 **專業報告**: 依專家類型產生結構化報告
        - 💾 **自動保存**: 逐字稿以YouTube標題命名保存至 saved_transcripts 資料夾
        """)
        
        # 顯示保存的逐字稿資料夾資訊
        st.subheader("📁 逐字稿歷史記錄")
        transcripts_folder = "saved_transcripts"
        if os.path.exists(transcripts_folder):
            transcript_files = [f for f in os.listdir(transcripts_folder) if f.endswith('.txt')]
            if transcript_files:
                st.write(f"已保存 {len(transcript_files)} 個逐字稿檔案:")
                for i, filename in enumerate(transcript_files[-5:], 1):  # 顯示最近5個
                    st.write(f"{i}. {filename}")
                if len(transcript_files) > 5:
                    st.write(f"... 還有 {len(transcript_files) - 5} 個檔案")
            else:
                st.write("暫無保存的逐字稿")
        else:
            st.write("逐字稿資料夾將在首次使用時建立")


if __name__ == "__main__":
    main()
