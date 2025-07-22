import os
import sys
import subprocess
import time
import logging
import socket
from datetime import datetime
from pathlib import Path

def setup_logging():
    """設定日誌記錄"""
    # 創建 logs 目錄
    log_dir = Path(__file__).parent / "logs"
    log_dir.mkdir(exist_ok=True)
    
    # 設定日誌檔案名稱
    today = datetime.now().strftime("%Y-%m-%d")
    log_file = log_dir / f"streamlit_background_{today}.log"
    
    # 設定日誌格式
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    return logging.getLogger(__name__)

def check_port_available(port=8501):
    """檢查端口是否可用"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect(('localhost', port))
            return False  # 端口被占用
    except (ConnectionRefusedError, OSError):
        return True  # 端口可用

def check_dependencies():
    """檢查並安裝依賴套件"""
    logger = logging.getLogger(__name__)
    
    try:
        import streamlit
        logger.info("Streamlit 已安裝")
        return True
    except ImportError:
        logger.info("Streamlit 未安裝，正在安裝必要套件...")
        try:
            # 安裝套件
            subprocess.run([
                sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
            ], check=True, capture_output=True, text=True)
            logger.info("套件安裝完成")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"套件安裝失敗: {e}")
            return False

def start_streamlit_background():
    """在後台啟動 Streamlit"""
    logger = logging.getLogger(__name__)
    
    # 檢查端口是否已被占用
    if not check_port_available(8501):
        logger.info("Streamlit 已在運行 (端口 8501 被占用)")
        return True
    
    # 檢查依賴套件
    if not check_dependencies():
        logger.error("依賴套件檢查失敗")
        return False
    
    try:
        # 設定工作目錄到專案根目錄
        script_dir = Path(__file__).parent
        project_root = script_dir.parent
        os.chdir(project_root)
        
        # 啟動 Streamlit（完全後台，無視窗）
        cmd = [
            sys.executable, "-m", "streamlit", "run", "src/ui/app_streamlit.py",
            "--server.port", "8501",
            "--server.address", "localhost",
            "--server.headless", "true",
            "--browser.gatherUsageStats", "false",
            "--global.showWarningOnDirectExecution", "false"
        ]
        
        logger.info("正在啟動 Streamlit 應用程式...")
        
        # 使用 DETACHED_PROCESS 在 Windows 上完全分離程序
        if sys.platform.startswith('win'):
            CREATE_NO_WINDOW = 0x08000000
            process = subprocess.Popen(
                cmd,
                creationflags=CREATE_NO_WINDOW,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                stdin=subprocess.DEVNULL
            )
        else:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                stdin=subprocess.DEVNULL
            )
        
        # 等待應用程式啟動
        time.sleep(8)
        
        # 檢查是否成功啟動
        if not check_port_available(8501):
            logger.info("Streamlit 應用程式成功啟動")
            logger.info("訪問網址: http://localhost:8501")
            return True
        else:
            logger.error("Streamlit 應用程式啟動失敗")
            return False
            
    except Exception as e:
        logger.error(f"啟動 Streamlit 時發生錯誤: {e}")
        return False

def main():
    """主函數"""
    # 設定日誌
    logger = setup_logging()
    
    logger.info("=" * 50)
    logger.info("YouTube Financial Report Generator v3.0")
    logger.info("後台啟動程式 Background Launcher")
    logger.info("=" * 50)
    
    # 啟動 Streamlit
    success = start_streamlit_background()
    
    if success:
        logger.info("後台啟動完成")
        logger.info("應用程式現在正在後台運行")
        logger.info("您可以關閉此視窗，應用程式將繼續運行")
    else:
        logger.error("後台啟動失敗")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
