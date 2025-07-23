"""
AI 服務模組
處理所有 AI 相關功能，包括 Gemini API 調用等
"""
import os
import streamlit as st
import google.generativeai as genai
from src.core.config import TRANSCRIPT_FILENAME
from src.utils.file_manager import FileManager


class AIService:
    """AI 服務管理器"""
    
    @staticmethod
    def call_gemini_api(prompt, api_key, output_filename):
        """調用 Google Gemini API"""
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-2.0-flash-exp')
            
            response = model.generate_content(prompt)
            if not response.parts:
                block_reason = response.prompt_feedback.block_reason if response.prompt_feedback else "未知"
                st.error(f"❌ Gemini 模型因故未生成任何內容。原因: {block_reason}")
                return False

            with open(output_filename, "w", encoding="utf-8") as f:
                f.write(response.text)
            st.success(f"✅ 報告已成功由 Gemini 生成並儲存為 {output_filename}")
            return True
        except Exception as e:
            st.error(f"❌ Gemini API 呼叫失敗: {e}")
            return False
    
    @staticmethod
    def refine_with_ai(report_output_filename, api_key, custom_prompt=None):
        """使用 AI 生成報告"""
        st.write("🤖 步驟 4/6: 開始使用 AI 潤飾報告...")
        
        if not api_key:
            st.error("❌ 請提供 API Key。")
            return False

        try:
            # 使用自定義 prompt 或預設的 prompt 檔案
            if custom_prompt:
                prompt_template = custom_prompt
                st.info("🎯 使用自定義 Prompt 進行分析")
            else:
                # 向後兼容：使用 prompt.txt 檔案
                prompt_file = "prompt.txt"
                if not os.path.exists(prompt_file):
                    st.warning(f"⚠️ 找不到 {prompt_file} 檔案，正在建立空檔案...")
                    if not FileManager.create_empty_prompt_file(prompt_file):
                        return False
                
                with open(prompt_file, "r", encoding="utf-8") as f:
                    prompt_template = f.read()
                
                if not prompt_template.strip():
                    st.error("❌ prompt.txt 檔案為空。")
                    return False
            
            with open(TRANSCRIPT_FILENAME, "r", encoding="utf-8") as f:
                transcript_text = f.read()

            if not transcript_text.strip():
                st.error("❌ 逐字稿為空，無法產生報告。")
                return False

            # 組合最終的 prompt
            if "{transcript_text}" in prompt_template:
                final_prompt = prompt_template.format(transcript_text=transcript_text)
            else:
                final_prompt = prompt_template + "\n\n影片內容逐字稿：\n" + transcript_text
            
            return AIService.call_gemini_api(final_prompt, api_key, report_output_filename)
                
        except Exception as e:
            st.error(f"❌ AI API 呼叫失敗: {e}")
            return False
