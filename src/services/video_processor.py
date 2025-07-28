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
    TRANSCRIPT_FILENAME, SUBTITLE_LANGUAGES, SUPPORTED_LANGUAGES, LANGUAGE_OPTIONS
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
    def get_video_title(youtube_url, cookie_file=None):
        """獲取YouTube影片標題"""
        try:
            # 嘗試第一種方法：--get-title
            command = [YT_DLP_PATH, "--get-title", "--no-warnings", youtube_url]
            if cookie_file:
                command.extend(["--cookies", cookie_file])
            
            # 設定環境變數確保正確的編碼
            env = os.environ.copy()
            env['PYTHONIOENCODING'] = 'utf-8'
            env['PYTHONUTF8'] = '1'
            
            process = subprocess.Popen(
                command, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE, 
                creationflags=subprocess.CREATE_NO_WINDOW,
                env=env
            )
            stdout, stderr = process.communicate()
            
            title = None
            if process.returncode == 0:
                title = VideoProcessor._decode_title(stdout)
            
            # 如果第一種方法失敗，嘗試第二種方法：--print
            if not title or title == "unknown_video":
                command_alt = [YT_DLP_PATH, "--print", "title", "--no-warnings", youtube_url]
                if cookie_file:
                    command_alt.extend(["--cookies", cookie_file])
                
                process_alt = subprocess.Popen(
                    command_alt, 
                    stdout=subprocess.PIPE, 
                    stderr=subprocess.PIPE, 
                    creationflags=subprocess.CREATE_NO_WINDOW,
                    env=env
                )
                stdout_alt, stderr_alt = process_alt.communicate()
                
                if process_alt.returncode == 0:
                    title = VideoProcessor._decode_title(stdout_alt)
            
            return title if title else "unknown_video"
            
        except Exception as e:
            st.warning(f"⚠️ 獲取影片標題時發生錯誤: {e}")
            return "unknown_video"
    
    @staticmethod
    def _decode_title(stdout_bytes):
        """解碼標題的輔助方法"""
        try:
            # 嘗試多種編碼方式
            title = None
            for encoding in ['utf-8', 'cp950', 'big5', 'gbk', 'cp1252']:
                try:
                    decoded = stdout_bytes.decode(encoding).strip()
                    # 檢查是否包含亂碼
                    if decoded and not any(ord(c) > 127 and not c.isprintable() for c in decoded):
                        title = decoded
                        break
                except (UnicodeDecodeError, UnicodeError):
                    continue
            
            if not title:
                # 如果所有編碼都失敗，使用 errors='replace'
                title = stdout_bytes.decode('utf-8', errors='replace').strip()
            
            # 清理標題中不適合檔案名稱的字元
            import re
            # 先移除不可見字元和控制字元
            title = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', title)
            # 替換檔案系統不允許的字元
            clean_title = re.sub(r'[<>:"/\\|?*]', '_', title)
            # 保留中文字元，只替換其他特殊字元
            clean_title = re.sub(r'[^\w\s\-_\.\(\)一-龯〇]', '_', clean_title)
            clean_title = clean_title.strip()
            
            # 移除多餘的底線和空格
            clean_title = re.sub(r'_+', '_', clean_title)
            clean_title = re.sub(r'\s+', ' ', clean_title)
            clean_title = clean_title.strip('_').strip()
            
            return clean_title if clean_title else None
            
        except Exception:
            return None
    
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
        """下載字幕的內部方法 (多執行緒最佳化)"""
        # 嘗試下載字幕
        for lang in SUBTITLE_LANGUAGES:
            download_command = [
                YT_DLP_PATH, "--write-sub", "--sub-lang", lang, 
                "--skip-download", "--sub-format", "vtt",
                "-o", "_temp_subtitle", 
                # 多執行緒加速設定 (字幕檔案較小，使用適中參數)
                "--concurrent-fragments", "8",
                "--fragment-retries", "5",
                "--retries", "3",
                "--socket-timeout", "20",
                "--no-warnings",
                youtube_url
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
        """下載自動字幕 (多執行緒最佳化)"""
        download_command = [
            YT_DLP_PATH, "--write-auto-sub", "--skip-download", 
            "--sub-format", "vtt", "-o", "_temp_subtitle",
            # 多執行緒加速設定
            "--concurrent-fragments", "8",
            "--fragment-retries", "5", 
            "--retries", "3",
            "--socket-timeout", "20",
            "--no-warnings",
            youtube_url
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
        
        # 建立優化的下載命令
        command = [
            YT_DLP_PATH, 
            "-x", "--audio-format", "mp3", 
            "-o", AUDIO_FILENAME, 
            # 多執行緒加速設定
            "--concurrent-fragments", "16",    # 同時下載16個片段 (最大化)
            "--fragment-retries", "10",        # 片段重試次數
            "--retries", "5",                  # 整體重試次數
            "--http-chunk-size", "10M",        # 10MB 區塊大小
            "--buffer-size", "32K",            # 32KB 緩衝區 (加大)
            # 網路優化
            "--socket-timeout", "30",          # 30秒超時
            "--throttled-rate", "100K",        # 最低速度限制 (避免掛起)
            # 品質最佳化 (音訊用，速度優先)
            "--format", "bestaudio[ext=m4a]/bestaudio[ext=webm]/bestaudio",
            # 跳過不必要的檢查以提升速度
            "--no-check-certificate",
            "--no-warnings",
            youtube_url
        ]
        
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
                # 如果高速模式失敗，嘗試降級到標準模式
                st.write("⚠️ 高速模式失敗，切換到標準模式...")
                fallback_command = [YT_DLP_PATH, "-x", "--audio-format", "mp3", "-o", AUDIO_FILENAME, youtube_url]
                if cookie_file:
                    fallback_command.extend(["--cookies", cookie_file])
                result = subprocess.run(fallback_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=subprocess.CREATE_NO_WINDOW)
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
    def transcribe_audio(model_name="base", language="zh"):
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
            
            # 顯示語言資訊
            if language:
                language_name = [k for k, v in LANGUAGE_OPTIONS.items() if v == language]
                language_display = language_name[0] if language_name else language
                st.info(f"🌍 語言設定: {language_display}")
            else:
                st.info("🌍 語言設定: 自動檢測 (支援中文/英文智慧識別)")
            
            progress_bar.progress(30)
            
            # 設定模型
            cache_dir = os.path.join(tempfile.gettempdir(), "faster_whisper_models")
            os.makedirs(cache_dir, exist_ok=True)
            
            status_text.text(f"載入 {model_name} 模型...")
            progress_bar.progress(40)
            
            # 設定多執行緒參數 (最大化性能)
            import multiprocessing
            cpu_count = multiprocessing.cpu_count()
            
            if device == "cuda":
                # GPU 模式：最大化並行處理
                cpu_threads = cpu_count * 2  # GPU 時可以使用更多 CPU 執行緒
                num_workers = min(4, cpu_count)  # GPU 模式下適中的 worker 數量
            else:
                # CPU 模式：平衡性能與資源使用
                cpu_threads = cpu_count
                num_workers = min(2, max(1, cpu_count // 2))  # CPU 模式下保守的 worker 數量
            
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
            
            # 進行轉錄 (最佳化參數)
            segments, info = model.transcribe(
                AUDIO_FILENAME, 
                language=language,  # 使用傳入的語言參數
                beam_size=1,           # 最快的 beam search
                temperature=0.0,       # 確定性輸出，避免重複計算
                vad_filter=True,       # 啟用 VAD 過濾靜音
                word_timestamps=False, # 不需要詞級時間戳，節省計算
                condition_on_previous_text=False,  # 不依賴前文，並行處理
                # 新增效能優化參數
                no_speech_threshold=0.6,  # 提高靜音檢測靈敏度
                log_prob_threshold=-1.0,  # 降低機率門檻，提升速度
                compression_ratio_threshold=2.4,  # 適中的壓縮比門檻
                initial_prompt=VideoProcessor._get_language_prompt(language)  # 根據語言調整提示
            )
            
            progress_bar.progress(80)
            status_text.text("整理結果...")
            
            # 顯示檢測到的語言資訊
            detected_language = getattr(info, 'language', 'unknown')
            detected_probability = getattr(info, 'language_probability', 0.0)
            
            if detected_language in ['zh', 'en']:
                lang_name = "中文" if detected_language == 'zh' else "英文"
                confidence = f"{detected_probability:.1%}" if detected_probability > 0 else "N/A"
                st.info(f"🔍 檢測到語言: {lang_name} (信心度: {confidence})")
            
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
    
    @staticmethod
    def _get_language_prompt(language):
        """根據語言返回適當的初始提示"""
        prompts = {
            "zh": "以下是中文語音內容：",
            "en": "The following is English speech content:"
        }
        return prompts.get(language, "")
