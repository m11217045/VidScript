"""
影片處理模組
處理 YouTube 影片下載、字幕處理、音訊轉錄等功能
使用 faster-whisper 進行 VRAM 優化
"""
import os
import subprocess
import tempfile
import streamlit as st
from faster_whisper import WhisperModel
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
            if torch.cuda.is_available():
                return f"GPU 可用 ({torch.cuda.get_device_name(0)})"
            return "僅 CPU 可用"
        except ImportError:
            return "PyTorch 未安裝"
    
    @staticmethod
    def check_and_download_subtitles(youtube_url, cookie_file=None):
        """檢查並下載 CC 字幕"""
        st.write("🔍 步驟 1/6: 檢查字幕...")
        
        check_command = [YT_DLP_PATH, "--list-subs", youtube_url]
        if cookie_file:
            check_command.extend(["--cookies", cookie_file])
        
        try:
            process = subprocess.Popen(check_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=subprocess.CREATE_NO_WINDOW)
            stdout, stderr = process.communicate()
            
            if process.returncode != 0:
                st.write("⚠️ 無法獲取字幕，使用語音轉文字")
                return False
            
            subtitle_info = stdout.decode('utf-8', errors='ignore')
            
            # 簡化檢查邏輯：只需要確認有字幕存在
            if not any(marker in subtitle_info for marker in ["Available subtitles", "Available automatic captions"]):
                st.write("ℹ️ 無字幕可用，使用語音轉文字")
                return False
            
            st.write("✅ 找到字幕，開始下載...")
            return VideoProcessor._download_subtitles(youtube_url, cookie_file)
            
        except Exception as e:
            st.error(f"❌ 字幕檢查錯誤: {e}")
            return False
    
    @staticmethod
    def _download_subtitles(youtube_url, cookie_file):
        """下載字幕的內部方法"""
        # 嘗試下載字幕
        for lang in SUBTITLE_LANGUAGES:
            download_command = [
                YT_DLP_PATH, "--write-sub", "--sub-lang", lang, 
                "--skip-download", "--sub-format", "vtt",
                "-o", "_temp_subtitle", youtube_url
            ]
            if cookie_file:
                download_command.extend(["--cookies", cookie_file])
            
            try:
                subprocess.run(download_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=subprocess.CREATE_NO_WINDOW)
                
                # 檢查下載的檔案
                for subtitle_file in [f"_temp_subtitle.{lang}.vtt", "_temp_subtitle.vtt"]:
                    if os.path.exists(subtitle_file) and os.path.getsize(subtitle_file) > 0:
                        os.rename(subtitle_file, SUBTITLE_FILENAME)
                        st.write(f"✅ 成功下載 {lang} 字幕")
                        return True
                        
            except Exception:
                continue
        
        # 嘗試下載自動字幕
        return VideoProcessor._download_auto_subtitles(youtube_url, cookie_file)
    
    @staticmethod
    def _download_auto_subtitles(youtube_url, cookie_file):
        """下載自動字幕"""
        download_command = [
            YT_DLP_PATH, "--write-auto-sub", "--skip-download", 
            "--sub-format", "vtt", "-o", "_temp_subtitle", youtube_url
        ]
        if cookie_file:
            download_command.extend(["--cookies", cookie_file])
        
        try:
            subprocess.run(download_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=subprocess.CREATE_NO_WINDOW)
            
            # 尋找並處理下載的檔案
            for file in os.listdir('.'):
                if file.startswith('_temp_subtitle') and file.endswith('.vtt') and os.path.getsize(file) > 0:
                    os.rename(file, SUBTITLE_FILENAME)
                    st.write("✅ 成功下載自動字幕")
                    return True
                    
        except Exception:
            pass
        
        st.write("ℹ️ 無可用字幕，將使用語音轉文字")
        return False
    
    @staticmethod
    def download_audio(youtube_url, cookie_file=None):
        """使用 yt-dlp 下載音訊"""
        st.write("🎵 步驟 2/6: 下載音訊...")
        
        # 建立下載命令
        command = [YT_DLP_PATH, "-x", "--audio-format", "mp3", "-o", AUDIO_FILENAME, youtube_url]
        
        # 檢查並添加 FFmpeg 路徑
        try:
            subprocess.run([FFMPEG_PATH, "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=subprocess.CREATE_NO_WINDOW, check=True)
            command.extend(["--ffmpeg-location", FFMPEG_PATH])
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass  # 使用 yt-dlp 內建功能
        
        if cookie_file:
            command.extend(["--cookies", cookie_file])

        try:
            result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=subprocess.CREATE_NO_WINDOW)
            if result.returncode != 0:
                st.error(f"❌ 下載失敗: {result.stderr.decode('utf-8', errors='ignore')}")
                return False
            st.success(f"✅ 音訊下載完成")
            return True
        except Exception as e:
            st.error(f"❌ 下載錯誤: {e}")
            return False
    
    @staticmethod
    def get_model_device(model):
        """獲取模型實際使用的設備"""
        try:
            device = str(getattr(model, 'device', 'unknown'))
            return f"GPU ({device})" if 'cuda' in device.lower() else f"CPU ({device})"
        except Exception:
            return "無法確定設備"
    
    @staticmethod
    def transcribe_audio(model_name="base"):
        """使用 faster-whisper 進行語音轉文字"""
        st.write("🔥 步驟 3/6: 開始語音轉文字...")
        if not os.path.exists(AUDIO_FILENAME):
            st.error(f"❌ 找不到音訊檔案 {AUDIO_FILENAME}")
            return False

        try:
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # 檢查設備並設定模型參數
            try:
                import torch
                cuda_available = torch.cuda.is_available()
                if cuda_available:
                    torch.cuda.empty_cache()
            except ImportError:
                cuda_available = False
            
            device = "cuda" if cuda_available else "cpu"
            compute_type = "float16" if cuda_available else "int8"
            
            progress_bar.progress(30)
            
            # 設定模型
            cache_dir = os.path.join(tempfile.gettempdir(), "faster_whisper_models")
            os.makedirs(cache_dir, exist_ok=True)
            
            status_text.text(f"載入 {model_name} 模型...")
            progress_bar.progress(40)
            
            # 設定多執行緒參數
            import multiprocessing
            cpu_count = multiprocessing.cpu_count()
            
            if device == "cuda":
                cpu_threads = cpu_count
                num_workers = min(64, cpu_count * 2)
            else:
                cpu_threads = cpu_count
                num_workers = min(2, max(1, cpu_count // 4))
            
            # 建立模型
            model = WhisperModel(
                model_name, 
                device=device,
                compute_type=compute_type,
                cpu_threads=cpu_threads,
                num_workers=num_workers,
                download_root=cache_dir,
                local_files_only=False
            )
            
            progress_bar.progress(50)
            status_text.text("開始轉錄...")
            
            # 設定 FFmpeg 路徑
            internal_dir = os.path.dirname(FFMPEG_PATH)
            if internal_dir not in os.environ.get('PATH', ''):
                os.environ['PATH'] = f"{internal_dir};{os.environ.get('PATH', '')}"
            
            # 進行轉錄
            segments, info = model.transcribe(
                AUDIO_FILENAME, 
                language="zh",
                beam_size=1,
                temperature=0.0,
                vad_filter=True,
                word_timestamps=False,
                condition_on_previous_text=False
            )
            
            progress_bar.progress(80)
            status_text.text("整理結果...")
            
            # 收集文字
            transcript_text = " ".join(segment.text for segment in segments)
            
            # 儲存結果
            with open(TRANSCRIPT_FILENAME, "w", encoding="utf-8") as f:
                f.write(transcript_text.strip())
                
            progress_bar.progress(100)
            status_text.text("轉錄完成！")
            
            st.success(f"✅ 逐字稿已儲存為 {TRANSCRIPT_FILENAME}")
            return True
            
        except Exception as e:
            st.error(f"❌ 轉錄失敗: {e}")
            return False
