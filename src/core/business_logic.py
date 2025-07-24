"""
主要業務邏輯處理模組
協調各個模組完成影片處理流程
"""
import os
import time
import streamlit as st
from src.core.config import DEFAULT_REPORT_NAME, TRANSCRIPT_FILENAME
from src.services.video_processor import VideoProcessor
from src.services.ai_service import AIService
from src.utils.file_manager import FileManager


class BusinessLogic:
    """業務邏輯處理器"""
    
    @staticmethod
    def process_video(youtube_url, api_key, delete_transcript, save_path, cookie_file=None, whisper_model="base", custom_prompt=None):
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
                        if delete_transcript:
                            # 如果要刪除逐字稿，進行AI修飾
                            if AIService.refine_with_ai(final_report_path, api_key, custom_prompt):
                                success = True
                        else:
                            # 如果保留逐字稿，直接使用原始逐字稿作為最終報告
                            if os.path.exists(TRANSCRIPT_FILENAME):
                                # 複製逐字稿到最終報告路徑
                                import shutil
                                shutil.copy2(TRANSCRIPT_FILENAME, final_report_path)
                                success = True
                else:
                    # 如果沒有字幕，則使用語音轉文字
                    if VideoProcessor.download_audio(youtube_url, cookie_file):
                        if VideoProcessor.transcribe_audio(whisper_model):
                            if delete_transcript:
                                # 如果要刪除逐字稿，進行AI修飾
                                if AIService.refine_with_ai(final_report_path, api_key, custom_prompt):
                                    success = True
                            else:
                                # 如果保留逐字稿，直接使用原始逐字稿作為最終報告
                                if os.path.exists(TRANSCRIPT_FILENAME):
                                    # 複製逐字稿到最終報告路徑
                                    import shutil
                                    shutil.copy2(TRANSCRIPT_FILENAME, final_report_path)
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
    def process_transcript_file(transcript_file, api_key, delete_transcript, save_path, custom_prompt=None):
        """處理上傳的逐字稿檔案"""
        
        with st.container():
            st.subheader("📈 處理進度")
            
            # 建立報告檔案路徑
            final_report_path = os.path.join(save_path, f"{DEFAULT_REPORT_NAME}.txt")
            
            success = False
            
            try:
                st.write("📝 步驟 1/3: 讀取逐字稿檔案...")
                
                # 讀取上傳的逐字稿檔案
                transcript_content = transcript_file.read().decode('utf-8')
                
                # 將內容寫入臨時逐字稿檔案
                with open(TRANSCRIPT_FILENAME, 'w', encoding='utf-8') as f:
                    f.write(transcript_content)
                
                st.success(f"✅ 逐字稿檔案已讀取，內容長度: {len(transcript_content)} 字元")
                
                if delete_transcript:
                    # 如果要刪除逐字稿，進行AI修飾
                    st.write("📝 步驟 2/3: 進行AI修飾...")
                    if AIService.refine_with_ai(final_report_path, api_key, custom_prompt):
                        success = True
                else:
                    # 如果保留逐字稿，直接使用原始逐字稿作為最終報告
                    st.write("📝 步驟 2/3: 保存原始逐字稿...")
                    if os.path.exists(TRANSCRIPT_FILENAME):
                        # 複製逐字稿到最終報告路徑
                        import shutil
                        shutil.copy2(TRANSCRIPT_FILENAME, final_report_path)
                        success = True
            
            except Exception as e:
                st.error(f"❌ 發生嚴重錯誤：{e}")
                import traceback
                st.error(f"詳細錯誤資訊：{traceback.format_exc()}")
                success = False
            
            finally:
                st.write("📝 步驟 3/3: 清理臨時檔案...")
                FileManager.cleanup_files(delete_transcript)
            
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
