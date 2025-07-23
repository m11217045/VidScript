"""
影片處理模組
處理 YouTube 影片下載、字幕處理、音訊轉錄等功能
"""
import os
import subprocess
import tempfile
import streamlit as st
import whisper
from src.core.config import (
    YT_DLP_PATH, FFMPEG_PATH, AUDIO_FILENAME, SUBTITLE_FILENAME, 
    TRANSCRIPT_FILENAME, SUBTITLE_LANGUAGES, SUPPORTED_LANGUAGES
)


class VideoProcessor:
    """影片處理器"""
    
    @staticmethod
    def check_device_availability():
        """檢查系統可用的運算設備"""
        try:
            import torch
            
            cuda_available = torch.cuda.is_available()
            if cuda_available:
                gpu_count = torch.cuda.device_count()
                gpu_name = torch.cuda.get_device_name(0) if gpu_count > 0 else "未知 GPU"
                cuda_version = torch.version.cuda
                return f"GPU 可用 ({gpu_name}, {gpu_count} 個設備, CUDA {cuda_version})"
            else:
                pytorch_version = torch.__version__
                if '+cpu' in pytorch_version:
                    return "僅 CPU 可用 (安裝的是 CPU-only 版本的 PyTorch)"
                else:
                    return "僅 CPU 可用 (CUDA 不可用 - 可能需要安裝 NVIDIA 驅動或重新安裝支援 CUDA 的 PyTorch)"
        except ImportError:
            return "PyTorch 未安裝，使用 Whisper 預設設定"
        except Exception as e:
            return f"設備檢查失敗：{e}"
    
    @staticmethod
    def check_and_download_subtitles(youtube_url, cookie_file=None):
        """檢查並下載 CC 字幕，優先順序：中文 > 英文 > 其他語言"""
        st.write("🔍 步驟 1/6: 檢查是否有可用的 CC 字幕...")
        
        check_command = [YT_DLP_PATH, "--list-subs", youtube_url]
        if cookie_file:
            check_command.extend(["--cookies", cookie_file])
        
        try:
            process = subprocess.Popen(check_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=subprocess.CREATE_NO_WINDOW)
            stdout, stderr = process.communicate()
            
            if process.returncode != 0:
                st.write("⚠️ 無法獲取字幕列表，將使用語音轉文字...")
                return False
            
            subtitle_info = stdout.decode('utf-8', errors='ignore')
            
            if "Available subtitles" not in subtitle_info and "Available automatic captions" not in subtitle_info:
                st.write("ℹ️ 此影片沒有可用的字幕，將使用語音轉文字...")
                return False
            
            # 檢查是否有實際的字幕語言
            has_subtitles = False
            for line in subtitle_info.split('\n'):
                if any(lang in line for lang in SUPPORTED_LANGUAGES) and ('vtt' in line or 'srt' in line):
                    has_subtitles = True
                    break
            
            if not has_subtitles:
                st.write("⚠️ 雖然有字幕區塊，但沒有找到可用的字幕語言，將使用語音轉文字...")
                return False
            
            st.write("✅ 找到可用字幕，正在下載...")
            return VideoProcessor._download_subtitles(youtube_url, cookie_file)
            
        except FileNotFoundError:
            st.error(f"❌ 錯誤：找不到 yt-dlp。路徑: {YT_DLP_PATH}")
            return False
        except Exception as e:
            st.error(f"❌ 檢查字幕時發生錯誤: {e}")
            return False
    
    @staticmethod
    def _download_subtitles(youtube_url, cookie_file):
        """下載字幕的內部方法"""
        # 嘗試下載字幕
        for lang in SUBTITLE_LANGUAGES:
            st.write(f"📥 嘗試下載 {lang} 字幕...")
            download_command = [
                YT_DLP_PATH, "--write-sub", "--sub-lang", lang, 
                "--skip-download", "--sub-format", "vtt",
                "-o", "_temp_subtitle", youtube_url
            ]
            if cookie_file:
                download_command.extend(["--cookies", cookie_file])
            
            try:
                process = subprocess.Popen(download_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=subprocess.CREATE_NO_WINDOW)
                stdout, stderr = process.communicate()
                
                possible_files = [
                    f"_temp_subtitle.{lang}.vtt",
                    "_temp_subtitle.vtt"
                ]
                
                for subtitle_file in possible_files:
                    if os.path.exists(subtitle_file):
                        if os.path.getsize(subtitle_file) > 0:
                            os.rename(subtitle_file, SUBTITLE_FILENAME)
                            st.write(f"✅ 成功下載 {lang} 字幕")
                            return True
                        else:
                            st.write(f"⚠️ {lang} 字幕檔案為空，嘗試下一個語言...")
                            os.remove(subtitle_file)
                            
            except Exception as e:
                st.write(f"❌ 下載 {lang} 字幕時發生錯誤: {e}")
                continue
        
        # 嘗試下載自動字幕
        return VideoProcessor._download_auto_subtitles(youtube_url, cookie_file)
    
    @staticmethod
    def _download_auto_subtitles(youtube_url, cookie_file):
        """下載自動字幕"""
        st.write("📥 嘗試下載自動生成字幕...")
        download_command = [
            YT_DLP_PATH, "--write-auto-sub", "--skip-download", 
            "--sub-format", "vtt", "-o", "_temp_subtitle", youtube_url
        ]
        if cookie_file:
            download_command.extend(["--cookies", cookie_file])
        
        try:
            process = subprocess.Popen(download_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=subprocess.CREATE_NO_WINDOW)
            stdout, stderr = process.communicate()
            
            for file in os.listdir('.'):
                if file.startswith('_temp_subtitle') and file.endswith('.vtt'):
                    if os.path.getsize(file) > 0:
                        os.rename(file, SUBTITLE_FILENAME)
                        st.write("✅ 成功下載自動生成字幕")
                        return True
                    else:
                        st.write("⚠️ 自動字幕檔案為空...")
                        os.remove(file)
                    
        except Exception as e:
            st.write(f"❌ 下載自動字幕時發生錯誤: {e}")
        
        st.write("ℹ️ 未找到可用的字幕，將使用語音轉文字...")
        return False
    
    @staticmethod
    def download_audio(youtube_url, cookie_file=None):
        """使用 yt-dlp 下載音訊"""
        st.write("🎵 步驟 2/6: 開始下載音訊...")
        
        # 檢查 ffmpeg 是否可用
        ffmpeg_available = False
        try:
            subprocess.run([FFMPEG_PATH, "-version"], 
                          stdout=subprocess.PIPE, 
                          stderr=subprocess.PIPE, 
                          creationflags=subprocess.CREATE_NO_WINDOW,
                          check=True)
            ffmpeg_available = True
            st.info(f"✅ 找到 FFmpeg: {FFMPEG_PATH}")
        except (subprocess.CalledProcessError, FileNotFoundError):
            st.warning(f"⚠️ 未找到 FFmpeg ({FFMPEG_PATH})，將使用 yt-dlp 內建轉換功能")
        
        # 建立下載命令
        command = [
            YT_DLP_PATH, "-x", "--audio-format", "mp3",
            "-o", AUDIO_FILENAME, youtube_url
        ]
        
        # 只有在 ffmpeg 可用時才添加 ffmpeg-location 參數
        if ffmpeg_available:
            command.extend(["--ffmpeg-location", FFMPEG_PATH])
        
        if cookie_file:
            command.extend(["--cookies", cookie_file])

        try:
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=subprocess.CREATE_NO_WINDOW)
            stdout, stderr = process.communicate()
            if process.returncode != 0:
                error_msg = stderr.decode('utf-8', errors='ignore')
                st.error(f"❌ yt-dlp 下載失敗: {error_msg}")
                return False
            st.success(f"✅ 音訊已成功下載為 {AUDIO_FILENAME}")
            return True
        except FileNotFoundError:
            st.error(f"❌ 找不到 yt-dlp。路徑: {YT_DLP_PATH}")
            return False
        except Exception as e:
            st.error(f"❌ 下載時發生未知錯誤: {e}")
            return False
    
    @staticmethod
    def get_model_device(model):
        """獲取模型實際使用的設備"""
        try:
            if hasattr(model, 'device'):
                device = str(model.device)
                return f"GPU ({device})" if 'cuda' in device.lower() else f"CPU ({device})"
            else:
                return "無法確定設備"
        except Exception as e:
            return f"設備檢查失敗：{e}"
    
    @staticmethod
    def transcribe_audio(model_name="base"):
        """使用 whisper 將音訊轉為逐字稿"""
        st.write("🎤 步驟 3/6: 開始進行語音轉文字 (此步驟可能需要較長時間)...")
        if not os.path.exists(AUDIO_FILENAME):
            st.error(f"❌ 找不到音訊檔案 {AUDIO_FILENAME}")
            return False

        try:
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            status_text.text(f"正在載入 Whisper {model_name} 模型...")
            progress_bar.progress(10)
            
            device_info = VideoProcessor.check_device_availability()
            st.info(f"🖥️ 系統運算設備狀態：{device_info}")
            
            cache_dir = os.path.join(tempfile.gettempdir(), "whisper_models")
            os.makedirs(cache_dir, exist_ok=True)
            
            try:
                model = whisper.load_model(model_name, download_root=cache_dir)
            except Exception as e:
                st.warning(f"載入 {model_name} 模型時發生錯誤，嘗試使用 base 模型: {e}")
                model = whisper.load_model("base")
            
            progress_bar.progress(30)
            
            actual_device = VideoProcessor.get_model_device(model)
            st.info(f"🔧 Whisper 模型實際使用設備：{actual_device}")
            
            status_text.text("開始轉錄音訊...")
            progress_bar.progress(50)
            
            # 設定 FFmpeg 路徑供 Whisper 使用
            original_path = os.environ.get('PATH', '')
            internal_dir = os.path.dirname(FFMPEG_PATH)
            if internal_dir not in original_path:
                os.environ['PATH'] = f"{internal_dir};{original_path}"
                st.info(f"🔧 已設定 FFmpeg 路徑：{internal_dir}")
            
            result = model.transcribe(
                AUDIO_FILENAME, 
                language="zh",
                verbose=False
            )
            
            progress_bar.progress(90)
            
            with open(TRANSCRIPT_FILENAME, "w", encoding="utf-8") as f:
                f.write(result["text"])
                
            progress_bar.progress(100)
            status_text.text("轉錄完成！")
            st.success(f"✅ 逐字稿已成功儲存為 {TRANSCRIPT_FILENAME}")
            return True
        except Exception as e:
            st.error(f"❌ Whisper 轉錄失敗: {e}")
            import traceback
            st.error(f"詳細錯誤資訊：{traceback.format_exc()}")
            return False
