"""
自動下載工具腳本
下載 FFmpeg 和 yt-dlp 二進制檔案
"""
import os
import sys
import requests
import zipfile
import tarfile
from pathlib import Path
import platform


def download_file(url, filename):
    """下載檔案並顯示進度"""
    print(f"📥 正在下載 {filename}...")
    
    response = requests.get(url, stream=True)
    response.raise_for_status()
    
    total_size = int(response.headers.get('content-length', 0))
    downloaded = 0
    
    with open(filename, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
                downloaded += len(chunk)
                if total_size > 0:
                    progress = (downloaded / total_size) * 100
                    print(f"\r進度: {progress:.1f}%", end='', flush=True)
    
    print(f"\n✅ {filename} 下載完成")


def download_ffmpeg():
    """下載 FFmpeg"""
    internal_dir = Path("_internal")
    internal_dir.mkdir(exist_ok=True)
    
    # Windows FFmpeg 下載連結
    ffmpeg_url = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
    
    if not (internal_dir / "ffmpeg.exe").exists():
        print("🔧 下載 FFmpeg...")
        
        # 下載 ZIP 檔案
        zip_file = "ffmpeg.zip"
        download_file(ffmpeg_url, zip_file)
        
        # 解壓縮
        print("📦 解壓縮 FFmpeg...")
        with zipfile.ZipFile(zip_file, 'r') as zip_ref:
            # 找到 ffmpeg.exe
            for file_info in zip_ref.filelist:
                if file_info.filename.endswith('ffmpeg.exe'):
                    with zip_ref.open(file_info) as source:
                        with open(internal_dir / "ffmpeg.exe", 'wb') as target:
                            target.write(source.read())
                    break
        
        # 清理
        os.remove(zip_file)
        print("✅ FFmpeg 安裝完成")
    else:
        print("✅ FFmpeg 已存在")


def download_yt_dlp():
    """下載 yt-dlp"""
    internal_dir = Path("_internal")
    internal_dir.mkdir(exist_ok=True)
    
    # yt-dlp 下載連結
    yt_dlp_url = "https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp.exe"
    
    if not (internal_dir / "yt-dlp.exe").exists():
        print("🔧 下載 yt-dlp...")
        download_file(yt_dlp_url, internal_dir / "yt-dlp.exe")
        print("✅ yt-dlp 安裝完成")
    else:
        print("✅ yt-dlp 已存在")


def main():
    """主函數"""
    print("🚀 開始下載必要的工具...")
    
    try:
        download_ffmpeg()
        download_yt_dlp()
        
        print("\n🎉 所有工具下載完成！")
        print("現在可以正常使用應用程式了。")
        
    except Exception as e:
        print(f"\n❌ 下載失敗: {e}")
        print("請檢查網路連接或手動下載檔案。")
        sys.exit(1)


if __name__ == "__main__":
    main()
