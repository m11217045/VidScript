"""
檔案管理模組
處理所有檔案操作，包括清理、轉換等
"""
import os
import re
import glob
import streamlit as st
from src.core.config import AUDIO_FILENAME, SUBTITLE_FILENAME, TRANSCRIPT_FILENAME


class FileManager:
    """檔案管理器"""
    
    @staticmethod
    def convert_vtt_to_text():
        """將 VTT 字幕檔轉換為純文字"""
        st.write("📝 步驟 2/6: 轉換字幕為文字格式...")
        
        if not os.path.exists(SUBTITLE_FILENAME):
            st.error(f"❌ 找不到字幕檔案 {SUBTITLE_FILENAME}")
            return False
        
        try:
            with open(SUBTITLE_FILENAME, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            text_lines = []
            for line in lines:
                line = line.strip()
                if (line.startswith('WEBVTT') or 
                    '-->' in line or 
                    line == '' or 
                    line.isdigit()):
                    continue
                
                clean_line = re.sub(r'<[^>]+>', '', line)
                if clean_line:
                    text_lines.append(clean_line)
            
            with open(TRANSCRIPT_FILENAME, 'w', encoding='utf-8') as f:
                f.write(' '.join(text_lines))
            
            st.success(f"✅ 字幕已成功轉換為文字並儲存為 {TRANSCRIPT_FILENAME}")
            return True
            
        except Exception as e:
            st.error(f"❌ 轉換字幕失敗: {e}")
            return False
    
    @staticmethod
    def create_empty_prompt_file(prompt_file):
        """建立空的 prompt.txt 檔案供使用者自行定義"""
        try:
            with open(prompt_file, "w", encoding="utf-8") as f:
                f.write("")
            st.warning(f"⚠️ 已建立空的 {prompt_file} 檔案，請自行編輯後重新執行")
            return False
        except Exception as e:
            st.error(f"❌ 無法建立 {prompt_file} 檔案: {e}")
            return False
    
    @staticmethod
    def cleanup_files(delete_transcript=True, cookie_file=None):
        """移除暫存檔案"""
        st.write("🧹 步驟 5/6: 清理暫存檔案...")
        
        files_to_remove = [AUDIO_FILENAME, SUBTITLE_FILENAME]
        
        if delete_transcript:
            files_to_remove.append(TRANSCRIPT_FILENAME)
        else:
            st.info("ℹ️ 保留逐字稿檔案...")
        
        for filename in files_to_remove:
            try:
                if os.path.exists(filename):
                    os.remove(filename)
                    st.write(f"🗑️ 已移除檔案: {filename}")
            except OSError as e:
                st.warning(f"⚠️ 無法移除檔案 {filename}: {e}")
        
        # 清理指定的 cookie 檔案
        if cookie_file:
            try:
                os.remove(cookie_file)
                st.write(f"🗑️ 已刪除 Cookie 檔案: {cookie_file}")
            except OSError as e:
                st.warning(f"⚠️ 無法刪除 Cookie 檔案 {cookie_file}: {e}")
        
        # 清理所有臨時 cookie 檔案
        temp_cookies = glob.glob("temp_cookie_*.txt")
        for temp_cookie in temp_cookies:
            try:
                os.remove(temp_cookie)
                st.write(f"🗑️ 已清理臨時 Cookie 檔案: {temp_cookie}")
            except OSError as e:
                st.warning(f"⚠️ 無法清理臨時 Cookie 檔案 {temp_cookie}: {e}")
        
        st.write("✅ 步驟 6/6: 清理完畢。")
