"""
檢查 Python 環境配置工具
"""
import os
import sys
from pathlib import Path


def check_python_environment():
    """檢查 Python 環境配置"""
    project_root = Path(__file__).parent.parent
    venv_path = project_root / "venv"
    venv_python = venv_path / "Scripts" / "python.exe"
    
    print(f"🔍 專案根目錄: {project_root}")
    print(f"🔍 虛擬環境路徑: {venv_path}")
    print(f"🔍 Python 執行檔: {venv_python}")
    print()
    
    if venv_path.exists():
        print("✅ 虛擬環境資料夾存在")
        if venv_python.exists():
            print("✅ Python 執行檔存在")
        else:
            print("❌ Python 執行檔不存在")
    else:
        print("❌ 虛擬環境資料夾不存在")
        print("💡 請執行 scripts/setup.bat 來創建虛擬環境")
    
    # 檢查 FFmpeg 和 yt-dlp
    internal_dir = project_root / "_internal"
    ffmpeg_path = internal_dir / "ffmpeg.exe"
    ytdlp_path = internal_dir / "yt-dlp.exe"
    
    print("\n📋 工具檔案檢查:")
    if ffmpeg_path.exists():
        print(f"✅ FFmpeg: {ffmpeg_path}")
    else:
        print(f"❌ FFmpeg 不存在: {ffmpeg_path}")
    
    if ytdlp_path.exists():
        print(f"✅ yt-dlp: {ytdlp_path}")
    else:
        print(f"❌ yt-dlp 不存在: {ytdlp_path}")
    
    # 檢查其他重要檔案
    important_files = [
        project_root / "tools" / "background_launcher.py",
        project_root / "scripts" / "Start_Streamlit_Hidden.vbs"
    ]
    
    print("\n📋 重要檔案檢查:")
    for file_path in important_files:
        if file_path.exists():
            print(f"✅ {file_path.name}")
        else:
            print(f"❌ {file_path.name} - 檔案不存在")
    
    # 檢查 PATH 中是否包含 _internal
    path_env = os.environ.get('PATH', '')
    internal_str = str(internal_dir)
    
    print("\n🔧 PATH 環境變數檢查:")
    if internal_str in path_env:
        print(f"✅ _internal 目錄已在 PATH 中")
    else:
        print(f"❌ _internal 目錄不在 PATH 中")
        print(f"💡 需要添加: {internal_str}")


if __name__ == "__main__":
    check_python_environment()
