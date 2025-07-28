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
    def process_video(youtube_url, api_key, save_path, cookie_file=None, whisper_model="base", custom_prompt=None, language="zh"):
        """處理影片的主要邏輯 (自動保存逐字稿模式)"""
        
        with st.container():
            st.subheader("📈 處理進度 (自動保存逐字稿)")
            
            # 確保 save_path 不為 None
            if save_path is None or (isinstance(save_path, str) and save_path.strip() == ""):
                save_path = os.getcwd()  # 使用當前工作目錄作為默認值
                st.warning(f"⚠️ 使用默認儲存路徑: {save_path}")
            
            # 首先獲取影片標題
            st.write("🎯 步驟 1/7: 獲取影片資訊...")
            video_title = VideoProcessor.get_video_title(youtube_url, cookie_file)
            st.success(f"✅ 影片標題: {video_title}")
            
            # 建立報告檔案路徑
            final_report_path = os.path.join(save_path, f"{DEFAULT_REPORT_NAME}.txt")
            
            success = False
            start_time = time.time()
            
            try:
                # 顯示性能資訊
                st.info("🚀 啟動高速模式：多執行緒下載 + GPU 加速轉錄 + 自動保存逐字稿")
                
                # 優先嘗試使用 CC 字幕
                if VideoProcessor.check_and_download_subtitles(youtube_url, cookie_file):
                    if FileManager.convert_vtt_to_text():
                        processing_time = time.time() - start_time
                        st.success(f"⚡ 字幕處理完成！用時: {processing_time:.1f} 秒")
                        
                        # 保存逐字稿到資料夾
                        st.write("💾 步驟 4/7: 保存逐字稿...")
                        FileManager.save_transcript(video_title)
                        
                        # 進行AI修飾
                        st.write("🤖 步驟 5/7: AI 修飾報告...")
                        if AIService.refine_with_ai(final_report_path, api_key, custom_prompt):
                            success = True
                else:
                    # 如果沒有字幕，則使用語音轉文字
                    download_start = time.time()
                    if VideoProcessor.download_audio(youtube_url, cookie_file):
                        download_time = time.time() - download_start
                        st.success(f"⚡ 音訊下載完成！用時: {download_time:.1f} 秒")
                        
                        transcribe_start = time.time()
                        if VideoProcessor.transcribe_audio(whisper_model, language):
                            transcribe_time = time.time() - transcribe_start
                            st.success(f"🔥 語音轉文字完成！用時: {transcribe_time:.1f} 秒")
                            
                            # 保存逐字稿到資料夾
                            st.write("💾 步驟 4/7: 保存逐字稿...")
                            FileManager.save_transcript(video_title)
                            
                            # 進行AI修飾
                            st.write("🤖 步驟 5/7: AI 修飾報告...")
                            if AIService.refine_with_ai(final_report_path, api_key, custom_prompt):
                                success = True
            
            except Exception as e:
                st.error(f"❌ 發生嚴重錯誤：{e}")
                import traceback
                st.error(f"詳細錯誤資訊：{traceback.format_exc()}")
                success = False
            
            finally:
                st.write("🧹 步驟 6/7: 清理暫存檔案...")
                FileManager.cleanup_files(cookie_file)
                
                # 清理臨時逐字稿
                try:
                    if os.path.exists(TRANSCRIPT_FILENAME):
                        os.remove(TRANSCRIPT_FILENAME)
                        st.write(f"🗑️ 已移除臨時逐字稿: {TRANSCRIPT_FILENAME}")
                except OSError as e:
                    st.warning(f"⚠️ 無法移除臨時逐字稿: {e}")
                
                # 顯示總處理時間
                total_time = time.time() - start_time
                st.write("✅ 步驟 7/7: 處理完成")
                if success:
                    st.success(f"🎉 處理完成！總用時: {total_time:.1f} 秒")
                    st.info("⚡ 多執行緒下載 + GPU 加速轉錄模式已啟用")
                    st.info("💾 逐字稿已自動保存到 saved_transcripts 資料夾")
                else:
                    st.error(f"❌ 處理失敗，用時: {total_time:.1f} 秒")
            
            return BusinessLogic._display_results(success, final_report_path)
    
    @staticmethod
    def process_transcript_file(transcript_file, api_key, save_path, custom_prompt=None):
        """處理上傳的逐字稿檔案（自動保存逐字稿）"""
        
        with st.container():
            st.subheader("📈 處理進度 (自動保存逐字稿)")
            
            # 確保 save_path 不為 None
            if save_path is None or (isinstance(save_path, str) and save_path.strip() == ""):
                save_path = os.getcwd()  # 使用當前工作目錄作為默認值
                st.warning(f"⚠️ 使用默認儲存路徑: {save_path}")
            
            # 使用檔案名稱作為標題
            file_title = transcript_file.name.rsplit('.', 1)[0]  # 移除副檔名
            st.success(f"✅ 檔案名稱: {file_title}")
            
            # 建立報告檔案路徑
            final_report_path = os.path.join(save_path, f"{DEFAULT_REPORT_NAME}.txt")
            
            success = False
            
            try:
                st.write("📝 步驟 1/5: 讀取逐字稿檔案...")
                
                # 讀取上傳的逐字稿檔案
                transcript_content = transcript_file.read().decode('utf-8')
                
                # 將內容寫入臨時逐字稿檔案
                with open(TRANSCRIPT_FILENAME, 'w', encoding='utf-8') as f:
                    f.write(transcript_content)
                
                st.success(f"✅ 逐字稿檔案已讀取，內容長度: {len(transcript_content)} 字元")
                
                # 保存逐字稿到資料夾
                st.write("💾 步驟 2/5: 保存逐字稿...")
                FileManager.save_transcript(file_title)
                
                # 進行AI修飾
                st.write("🤖 步驟 3/5: AI 修飾報告...")
                if AIService.refine_with_ai(final_report_path, api_key, custom_prompt):
                    success = True
            
            except Exception as e:
                st.error(f"❌ 發生嚴重錯誤：{e}")
                import traceback
                st.error(f"詳細錯誤資訊：{traceback.format_exc()}")
                success = False
            
            finally:
                st.write("🧹 步驟 4/5: 清理臨時檔案...")
                FileManager.cleanup_files()
                
                # 清理臨時逐字稿
                try:
                    if os.path.exists(TRANSCRIPT_FILENAME):
                        os.remove(TRANSCRIPT_FILENAME)
                        st.write(f"🗑️ 已移除臨時逐字稿: {TRANSCRIPT_FILENAME}")
                except OSError as e:
                    st.warning(f"⚠️ 無法移除臨時逐字稿: {e}")
                
                st.write("✅ 步驟 5/5: 處理完成")
                if success:
                    st.success("🎉 處理完成！")
                    st.info("💾 逐字稿已自動保存到 saved_transcripts 資料夾")
                else:
                    st.error("❌ 處理失敗")
            
            return BusinessLogic._display_results(success, final_report_path)
    
    @staticmethod
    def process_saved_transcript(transcript_filename, api_key, save_path, custom_prompt=None):
        """處理已保存的逐字稿檔案"""
        
        with st.container():
            st.subheader("📈 處理進度 (重新分析已保存逐字稿)")
            
            # 確保 save_path 不為 None
            if save_path is None or (isinstance(save_path, str) and save_path.strip() == ""):
                save_path = os.getcwd()  # 使用當前工作目錄作為默認值
                st.warning(f"⚠️ 使用默認儲存路徑: {save_path}")
            
            # 建構逐字稿檔案路徑
            from src.core.config import TRANSCRIPTS_FOLDER
            transcript_path = os.path.join(TRANSCRIPTS_FOLDER, transcript_filename)
            
            # 使用檔案名稱作為標題（移除副檔名）
            file_title = transcript_filename.rsplit('.', 1)[0]
            st.success(f"✅ 選擇的逐字稿: {file_title}")
            
            # 建立報告檔案路徑
            final_report_path = os.path.join(save_path, f"{DEFAULT_REPORT_NAME}.txt")
            
            success = False
            
            try:
                st.write("📝 步驟 1/4: 讀取已保存的逐字稿...")
                
                # 檢查檔案是否存在
                if not os.path.exists(transcript_path):
                    st.error(f"❌ 找不到逐字稿檔案: {transcript_path}")
                    return False
                
                # 讀取已保存的逐字稿檔案
                with open(transcript_path, 'r', encoding='utf-8') as f:
                    transcript_content = f.read()
                
                # 將內容寫入臨時逐字稿檔案以供AI處理
                with open(TRANSCRIPT_FILENAME, 'w', encoding='utf-8') as f:
                    f.write(transcript_content)
                
                st.success(f"✅ 逐字稿已載入，內容長度: {len(transcript_content)} 字元")
                
                # 進行AI修飾
                st.write("🤖 步驟 2/4: AI 重新分析報告...")
                if AIService.refine_with_ai(final_report_path, api_key, custom_prompt):
                    success = True
            
            except Exception as e:
                st.error(f"❌ 發生嚴重錯誤：{e}")
                import traceback
                st.error(f"詳細錯誤資訊：{traceback.format_exc()}")
                success = False
            
            finally:
                st.write("🧹 步驟 3/4: 清理臨時檔案...")
                
                # 清理臨時逐字稿
                try:
                    if os.path.exists(TRANSCRIPT_FILENAME):
                        os.remove(TRANSCRIPT_FILENAME)
                        st.write(f"🗑️ 已移除臨時逐字稿: {TRANSCRIPT_FILENAME}")
                except OSError as e:
                    st.warning(f"⚠️ 無法移除臨時逐字稿: {e}")
                
                st.write("✅ 步驟 4/4: 處理完成")
                if success:
                    st.success("🎉 重新分析完成！")
                    st.info("🔄 使用新的分析設定重新生成報告")
                else:
                    st.error("❌ 處理失敗")
            
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
