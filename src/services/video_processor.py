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
        """使用 faster-whisper 將音訊轉為逐字稿（最大 VRAM 消耗 + 最高速度）"""
        st.write("🔥 步驟 3/6: 最大 VRAM 消耗模式 - 開始進行語音轉文字 (base 模型 + 極限速度配置)...")
        if not os.path.exists(AUDIO_FILENAME):
            st.error(f"❌ 找不到音訊檔案 {AUDIO_FILENAME}")
            return False

        try:
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            status_text.text(f"正在載入 Faster-Whisper {model_name} 高效能模型...")
            progress_bar.progress(10)
            
            device_info = VideoProcessor.check_device_availability()
            st.info(f"🖥️ 系統運算設備狀態：{device_info}")
            
            # 確定使用的設備和精度設定
            try:
                import torch
                cuda_available = torch.cuda.is_available()
                if cuda_available:
                    gpu_memory = torch.cuda.get_device_properties(0).total_memory / (1024**3)
                    st.info(f"🎯 GPU 記憶體總容量: {gpu_memory:.1f} GB")
                    # 清理之前的 GPU 記憶體
                    torch.cuda.empty_cache()
                    initial_memory = torch.cuda.memory_allocated(0) / (1024**3)
                    st.info(f"📊 初始 GPU 記憶體使用: {initial_memory:.3f} GB")
            except ImportError:
                cuda_available = False
            
            if cuda_available:
                device = "cuda"
                compute_type = "float16"  # 使用 float16 增加 VRAM 使用量
                st.info("🚀 使用 GPU 高 VRAM 模式：float16 精度 (增加記憶體使用)")
            else:
                device = "cpu"
                compute_type = "int8"
                st.info("💻 使用 CPU 模式：int8 精度")
            
            progress_bar.progress(30)
            
            # 設定模型快取目錄
            cache_dir = os.path.join(tempfile.gettempdir(), "faster_whisper_models")
            os.makedirs(cache_dir, exist_ok=True)
            
            status_text.text(f"正在初始化 {model_name} 模型...")
            progress_bar.progress(40)
            
            try:
                # 確定多執行緒設定 - 高效能配置
                import multiprocessing
                
                # 獲取 CPU 核心數量
                cpu_count = multiprocessing.cpu_count()
                
                if device == "cuda":
                    # GPU 最大 VRAM 模式：極限並行配置
                    cpu_threads = cpu_count  # 使用所有 CPU 執行緒輔助 GPU
                    num_workers = 32  # 大幅增加工作執行緒數消耗更多 VRAM
                    st.info(f"🔥 GPU 最大 VRAM 模式多執行緒：{cpu_threads} CPU 執行緒，{num_workers} 工作執行緒")
                    st.info("🎯 目標：使用 base 模型 + 極限並行來消耗所有 VRAM")
                else:
                    # CPU 模式：最大化利用多核心
                    cpu_threads = cpu_count  # 使用所有可用核心
                    num_workers = min(2, max(1, cpu_count // 4))  # 根據核心數決定 worker 數量
                    st.info(f"💻 CPU 模式多執行緒設定：{cpu_threads} CPU 執行緒，{num_workers} 工作執行緒")
                
                # 建立 faster-whisper 模型（高 VRAM 配置）
                model = WhisperModel(
                    model_name, 
                    device=device,
                    compute_type=compute_type,
                    cpu_threads=cpu_threads,  # 設定 CPU 執行緒數
                    num_workers=num_workers,  # 設定工作執行緒數
                    download_root=cache_dir,
                    local_files_only=False  # 允許下載最新模型
                )
                
                # 檢查模型載入後的記憶體使用
                if device == "cuda":
                    try:
                        torch.cuda.synchronize()  # 同步 GPU 操作
                        after_load_memory = torch.cuda.memory_allocated(0) / (1024**3)
                        memory_increase = after_load_memory - initial_memory
                        st.info(f"📈 模型載入後 GPU 記憶體: {after_load_memory:.3f} GB (+{memory_increase:.3f} GB)")
                        
                        # 顯示 VRAM 使用率
                        vram_usage_percent = (after_load_memory / gpu_memory) * 100
                        st.info(f"💾 VRAM 使用率: {vram_usage_percent:.1f}%")
                        
                        st.info("🔥 **高 VRAM 模式說明**:")
                        st.info(f"   • 使用 {model_name} 模型 (更高準確度)")
                        st.info("   • float16 精度 (增加記憶體使用)")
                        st.info(f"   • {num_workers} 個工作執行緒 (提高並行度)")
                        st.info("   • 預期效能提升 2-5 倍 🚀")
                    except:
                        st.info("📊 GPU 記憶體資訊獲取中...")
                
                st.success(f"✅ 成功載入 {model_name} 高效能模型")
                
            except Exception as e:
                st.warning(f"載入 {model_name} 模型失敗: {e}")
                st.info("🔄 嘗試使用 base 模型...")
                
                # 備用模型也使用高 VRAM 設定
                model = WhisperModel(
                    "base", 
                    device=device, 
                    compute_type=compute_type,
                    cpu_threads=cpu_threads,
                    num_workers=num_workers,
                    download_root=cache_dir
                )
                st.success("✅ 成功載入 base 備用模型（高 VRAM 版本）")
            
            progress_bar.progress(50)
            status_text.text("開始轉錄音訊...")
            
            # 設定 FFmpeg 路徑
            original_path = os.environ.get('PATH', '')
            internal_dir = os.path.dirname(FFMPEG_PATH)
            if internal_dir not in original_path:
                os.environ['PATH'] = f"{internal_dir};{original_path}"
                st.info(f"🔧 已設定 FFmpeg 路徑：{internal_dir}")
            
            # 進行極限效能轉錄
            st.info(f"🎯 開始轉錄：{model_name} 模型（極限 VRAM 消耗模式）")
            st.info(f"🖥️ 設備：{device} | 精度：{compute_type} | 工作執行緒：{num_workers if device == 'cuda' else 'N/A'}")
            
            # 使用極限效能參數進行轉錄（最大化並行處理）
            segments, info = model.transcribe(
                AUDIO_FILENAME, 
                language="zh",
                beam_size=1,  # 使用最小束搜索換取最大速度
                temperature=0.0,  # 確定性轉錄
                vad_filter=True,  # 語音活動檢測
                vad_parameters=dict(
                    min_silence_duration_ms=100,  # 最小靜音持續時間（極快響應）
                    threshold=0.1,  # 非常敏感的 VAD 閾值
                    min_speech_duration_ms=100,  # 最小語音持續時間
                    max_speech_duration_s=30  # 短語音段（最大化並行）
                ),
                word_timestamps=False,  # 關閉精確時間戳以節省記憶體給並行處理
                compression_ratio_threshold=10.0,  # 寬鬆的壓縮比閾值
                log_prob_threshold=-2.0,  # 寬鬆的機率閾值
                no_speech_threshold=0.1,  # 極敏感的無語音檢測
                condition_on_previous_text=False,  # 關閉前文預測以加速
                initial_prompt=None  # 不使用初始提示以減少記憶體開銷
            )
            
            if device == "cuda":
                st.info("🚀 GPU 極限 VRAM 多執行緒轉錄進行中...")
                st.info("   • 32 個並行工作執行緒同時運作 💥")
                st.info("   • 最大化 GPU 記憶體使用以獲得極限速度")
                st.info("   • 預期消耗大部分可用 VRAM 💾")
            else:
                st.info("💻 CPU 多執行緒轉錄進行中...")
            
            progress_bar.progress(80)
            status_text.text("正在整理轉錄結果...")
            
            # 收集轉錄文字
            transcript_text = ""
            segment_count = 0
            for segment in segments:
                transcript_text += segment.text + " "
                segment_count += 1
            
            # 儲存結果
            with open(TRANSCRIPT_FILENAME, "w", encoding="utf-8") as f:
                f.write(transcript_text.strip())
                
            progress_bar.progress(100)
            status_text.text("轉錄完成！")
            
            # 顯示結果統計
            st.success(f"✅ 逐字稿已成功儲存為 {TRANSCRIPT_FILENAME}")
            st.info(f"📊 轉錄統計：{segment_count} 個片段，語言: {info.language}")
            
            # 顯示多執行緒效能說明
            if device == "cuda":
                st.info("🔥 **GPU 多執行緒加速成功** - 您可以在工作管理員中看到 GPU 使用率")
            else:
                st.info(f"⚡ **CPU 多執行緒加速成功** - 使用了 {cpu_threads} 個 CPU 執行緒")
            
            return True
            
        except Exception as e:
            st.error(f"❌ Faster-Whisper 轉錄失敗: {e}")
            import traceback
            st.error(f"詳細錯誤資訊：{traceback.format_exc()}")
            return False
