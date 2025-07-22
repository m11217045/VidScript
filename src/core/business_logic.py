"""
主要業務邏輯處理模組
協調各個模組完成影片處理流程
"""
import os
import time
import streamlit as st
from src.core.config import DEFAULT_REPORT_NAME
from src.services.video_processor import VideoProcessor
from src.services.ai_service import AIService
from src.utils.file_manager import FileManager


class BusinessLogic:
    """業務邏輯處理器"""
    
    @staticmethod
    def process_video(youtube_url, api_key, delete_transcript, save_path, cookie_file=None, whisper_model="base"):
        """處理影片的主要邏輯"""
        
        with st.container():
            st.subheader("📈 處理進度")
            
            # 建立報告檔案路徑
            final_report_path = os.path.join(save_path, f"{DEFAULT_REPORT_NAME}.txt")
            
            success = False
            
            try:
                # 優先嘗試使用 CC 字幕
                if VideoProcessor.check_and_download_subtitles(youtube_url, cookie_file):
                    if FileManager.convert_vtt_to_text():
                        if AIService.refine_with_ai(final_report_path, api_key):
                            success = True
                else:
                    # 如果沒有字幕，則使用語音轉文字
                    if VideoProcessor.download_audio(youtube_url, cookie_file):
                        if VideoProcessor.transcribe_audio(whisper_model):
                            if AIService.refine_with_ai(final_report_path, api_key):
                                success = True
            
            except Exception as e:
                st.error(f"❌ 發生嚴重錯誤：{e}")
                import traceback
                st.error(f"詳細錯誤資訊：{traceback.format_exc()}")
                success = False
            
            finally:
                FileManager.cleanup_files(delete_transcript, cookie_file)
            
            return BusinessLogic._display_results(success, final_report_path)
    
    @staticmethod
    def _display_results(success, final_report_path):
        """顯示處理結果"""
        if success:
            st.success(f"🎉 報告生成完成！")
            st.info(f"📁 檔案路徑: {final_report_path}")
            
            # 顯示報告內容
            try:
                with open(final_report_path, 'r', encoding='utf-8') as f:
                    report_content = f.read()
                
                st.subheader("📄 生成的報告")
                st.markdown(report_content)
                
                # 提供下載按鈕
                st.download_button(
                    label="📥 下載報告",
                    data=report_content,
                    file_name=f"{DEFAULT_REPORT_NAME}.md",
                    mime="text/markdown"
                )
                
                return True
                
            except Exception as e:
                st.warning(f"⚠️ 無法讀取報告檔案進行預覽: {e}")
                return True
        else:
            st.error("❌ 報告生成失敗，請檢查上方錯誤訊息")
            return False
    
    @staticmethod
    def prepare_cookie_file(cookie_file):
        """準備 Cookie 檔案"""
        if cookie_file:
            cookie_path = f"temp_cookie_{int(time.time())}.txt"
            with open(cookie_path, "wb") as f:
                f.write(cookie_file.getbuffer())
            return cookie_path
        return None
