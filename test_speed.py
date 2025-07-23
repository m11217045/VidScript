#!/usr/bin/env python3
"""
VidScript Faster-Whisper 速度測試
測試當前項目配置的實際性能
"""

import os
import sys
import time
import tempfile
import wave
import numpy as np

# 添加項目路徑
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def create_test_audio(duration_seconds):
    """創建指定長度的測試音檔"""
    sample_rate = 16000
    
    # 創建模擬語音的音檔（有多個頻率成分）
    t = np.linspace(0, duration_seconds, sample_rate * duration_seconds)
    
    # 組合多個頻率模擬語音特徵
    audio = np.zeros_like(t)
    for freq in [150, 300, 600, 1200]:  # 模擬人聲頻率
        audio += 0.1 * np.sin(2 * np.pi * freq * t)
    
    # 添加一些隨機噪音
    audio += 0.05 * np.random.normal(0, 1, len(t))
    
    # 歸一化並轉換為 16-bit
    audio = audio / np.max(np.abs(audio)) * 0.8
    audio_int16 = (audio * 32767).astype(np.int16)
    
    # 保存為臨時 WAV 檔案
    temp_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
    with wave.open(temp_file.name, 'w') as wav_file:
        wav_file.setnchannels(1)  # 單聲道
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(audio_int16.tobytes())
    
    return temp_file.name

def test_project_configuration():
    """測試項目中的 faster-whisper 配置"""
    print("🚀 測試 VidScript 項目配置...")
    
    try:
        from faster_whisper import WhisperModel
        import torch
        
        # 檢查環境
        print(f"PyTorch 版本: {torch.__version__}")
        print(f"CUDA 可用: {torch.cuda.is_available()}")
        if torch.cuda.is_available():
            print(f"GPU: {torch.cuda.get_device_name(0)}")
            print(f"CUDA 版本: {torch.version.cuda}")
        
        # 測試不同的音檔長度
        test_durations = [5, 15, 30, 60]  # 秒
        
        # 測試配置（與項目中使用的相同）
        configs = [
            {
                "name": "CPU 模式", 
                "device": "cpu", 
                "compute_type": "int8",
                "description": "CPU 基準測試"
            }
        ]
        
        # 添加 GPU 配置（如果可用）
        if torch.cuda.is_available():
            configs.extend([
                {
                    "name": "GPU Float16", 
                    "device": "cuda", 
                    "compute_type": "float16",
                    "description": "GPU 高精度模式"
                },
                {
                    "name": "GPU Int8_Float16 (推薦)", 
                    "device": "cuda", 
                    "compute_type": "int8_float16",
                    "description": "GPU 最佳性能模式"
                }
            ])
        
        # 存儲結果
        all_results = {}
        
        for config in configs:
            print(f"\n{'='*50}")
            print(f"🔧 測試配置: {config['name']}")
            print(f"📝 描述: {config['description']}")
            print(f"⚙️ 設備: {config['device']}, 計算類型: {config['compute_type']}")
            
            try:
                # 載入模型
                print("\n🔄 載入模型...")
                start_time = time.time()
                
                model = WhisperModel(
                    "small",  # 使用 small 模型（與項目配置一致）
                    device=config["device"],
                    compute_type=config["compute_type"]
                )
                
                load_time = time.time() - start_time
                print(f"✅ 模型載入完成，耗時: {load_time:.2f} 秒")
                
                # GPU 記憶體監控
                if config["device"] == "cuda":
                    allocated = torch.cuda.memory_allocated(0) / 1024**3
                    reserved = torch.cuda.memory_reserved(0) / 1024**3
                    print(f"📊 GPU 記憶體 - 已分配: {allocated:.3f}GB, 保留: {reserved:.3f}GB")
                
                # 測試不同長度的音檔
                config_results = {"load_time": load_time, "tests": {}}
                
                for duration in test_durations:
                    print(f"\n🎵 測試 {duration} 秒音檔...")
                    
                    # 創建測試音檔
                    audio_file = create_test_audio(duration)
                    
                    try:
                        # 執行轉錄
                        start_time = time.time()
                        segments, info = model.transcribe(
                            audio_file,
                            beam_size=5,
                            language="zh"  # 指定中文避免語言檢測
                        )
                        
                        # 消費生成器確保完整轉錄
                        segment_list = list(segments)
                        transcribe_time = time.time() - start_time
                        
                        # 計算性能指標
                        speed_factor = duration / transcribe_time  # 速度倍數
                        rtf = transcribe_time / duration  # 實時倍數
                        
                        # 保存結果
                        result = {
                            "duration": duration,
                            "transcribe_time": transcribe_time,
                            "speed_factor": speed_factor,
                            "rtf": rtf,
                            "segments": len(segment_list),
                            "language": info.language,
                            "language_probability": info.language_probability
                        }
                        
                        config_results["tests"][duration] = result
                        
                        # 顯示結果
                        print(f"   ⏱️ 轉錄時間: {transcribe_time:.2f} 秒")
                        print(f"   🚀 速度倍數: {speed_factor:.1f}x (比實時快 {speed_factor:.1f} 倍)")
                        print(f"   📈 實時倍數: {rtf:.3f} ({'✅ 比實時快' if rtf < 1.0 else '⚠️ 比實時慢'})")
                        print(f"   🗣️ 檢測語言: {info.language} (置信度: {info.language_probability:.2f})")
                        print(f"   📝 轉錄段落: {len(segment_list)} 個")
                        
                    finally:
                        # 清理臨時檔案
                        if os.path.exists(audio_file):
                            os.remove(audio_file)
                
                all_results[config["name"]] = config_results
                
                # 清理模型
                del model
                if config["device"] == "cuda":
                    torch.cuda.empty_cache()
                
                print(f"✅ {config['name']} 測試完成")
                
            except Exception as e:
                print(f"❌ {config['name']} 測試失敗: {e}")
                import traceback
                traceback.print_exc()
                continue
        
        return all_results
        
    except ImportError as e:
        print(f"❌ 導入錯誤: {e}")
        print("請確認 faster-whisper 已正確安裝")
        return None
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return None

def analyze_performance_results(results):
    """分析性能測試結果"""
    if not results:
        print("❌ 沒有測試結果可分析")
        return
    
    print(f"\n{'='*60}")
    print("📊 性能分析報告")
    print(f"{'='*60}")
    
    # 創建性能比較表
    print(f"\n📈 轉錄性能對比表:")
    print(f"{'配置':<20} {'音檔長度':<10} {'轉錄時間':<10} {'速度倍數':<10} {'實時倍數':<10}")
    print("-" * 70)
    
    best_config = None
    best_avg_speed = 0
    
    for config_name, config_data in results.items():
        speeds = []
        
        for duration, test_result in config_data["tests"].items():
            speed_factor = test_result["speed_factor"]
            transcribe_time = test_result["transcribe_time"]
            rtf = test_result["rtf"]
            
            speeds.append(speed_factor)
            
            print(f"{config_name:<20} {duration}秒{'':<6} {transcribe_time:<9.2f}秒 {speed_factor:<9.1f}x {rtf:<9.3f}")
        
        # 計算平均速度
        avg_speed = sum(speeds) / len(speeds) if speeds else 0
        if avg_speed > best_avg_speed:
            best_avg_speed = avg_speed
            best_config = config_name
        
        print(f"{'':<20} {'平均':<10} {'':<10} {avg_speed:<9.1f}x")
        print("-" * 70)
    
    # 推薦配置
    print(f"\n🏆 推薦配置分析:")
    
    if best_config:
        print(f"🥇 最佳性能: {best_config} (平均速度 {best_avg_speed:.1f}x)")
        
        # 給出具體的 VidScript 配置建議
        if "GPU" in best_config and "Int8_Float16" in best_config:
            print(f"\n💡 VidScript 項目建議配置:")
            print(f"```python")
            print(f"device = 'cuda'")
            print(f"compute_type = 'int8_float16'")
            print(f"```")
            print(f"🎯 這是目前測試中性能最佳的配置！")
        elif "GPU" in best_config:
            print(f"\n💡 VidScript 項目建議配置:")
            print(f"```python")
            print(f"device = 'cuda'")
            print(f"compute_type = 'float16'")
            print(f"```")
        else:
            print(f"\n💡 VidScript 項目建議配置:")
            print(f"```python")
            print(f"device = 'cpu'")
            print(f"compute_type = 'int8'")
            print(f"```")
            print(f"⚠️ GPU 可能不可用或性能不佳，建議使用 CPU 配置")
    
    # 性能評估
    print(f"\n📋 性能評估:")
    
    cpu_config = None
    gpu_config = None
    
    for config_name, config_data in results.items():
        if "CPU" in config_name:
            cpu_config = config_data
        elif "推薦" in config_name or "Int8_Float16" in config_name:
            gpu_config = config_data
    
    if cpu_config and gpu_config:
        # 比較 30 秒音檔的性能
        if 30 in cpu_config["tests"] and 30 in gpu_config["tests"]:
            cpu_time = cpu_config["tests"][30]["transcribe_time"]
            gpu_time = gpu_config["tests"][30]["transcribe_time"]
            improvement = cpu_time / gpu_time
            
            print(f"🚀 GPU 相對於 CPU 的提升: {improvement:.1f}x")
            if improvement > 5:
                print(f"   🔥 GPU 加速效果顯著！建議使用 GPU 配置")
            elif improvement > 2:
                print(f"   ✅ GPU 加速效果不錯，推薦使用 GPU 配置")
            else:
                print(f"   ⚠️ GPU 加速效果一般，可考慮 CPU 配置")
    
    # 實時性分析
    print(f"\n⏱️ 實時性分析:")
    print(f"   實時倍數 < 0.1: 🔥 極快 (推薦用於大量處理)")
    print(f"   實時倍數 < 0.5: ✅ 很快 (適用於大多數場景)")
    print(f"   實時倍數 < 1.0: 📱 實時 (適用於即時應用)")
    print(f"   實時倍數 > 1.0: ⚠️ 較慢 (可能需要優化)")

def main():
    """主函數"""
    print("🏃‍♂️ VidScript Faster-Whisper 速度測試")
    print("🎯 測試當前項目配置的實際性能")
    print(f"📍 測試目錄: {os.getcwd()}\n")
    
    try:
        # 執行性能測試
        results = test_project_configuration()
        
        if results:
            # 分析結果
            analyze_performance_results(results)
            
            print(f"\n🎉 測試完成！")
            print(f"\n💡 如何應用測試結果:")
            print(f"1. 根據推薦配置修改 VidScript 的模型設定")
            print(f"2. 在 src/services/video_processor.py 中調整參數")
            print(f"3. 觀察實際使用中的性能提升")
            print(f"4. 如果 GPU 性能不佳，可以回退到 CPU 配置")
        else:
            print(f"❌ 測試失敗，請檢查環境配置")
    
    except KeyboardInterrupt:
        print(f"\n⏹️ 測試被用戶中斷")
    except Exception as e:
        print(f"\n❌ 測試過程中發生錯誤: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
