import os
import sys
import psutil
import socket
import logging
from datetime import datetime
from pathlib import Path

def setup_logging():
    """設定日誌記錄"""
    log_dir = Path(__file__).parent / "logs"
    log_dir.mkdir(exist_ok=True)
    
    today = datetime.now().strftime("%Y-%m-%d")
    log_file = log_dir / f"streamlit_background_{today}.log"
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8', mode='a'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    return logging.getLogger(__name__)

def check_port_occupied(port=8501):
    """檢查端口是否被占用"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect(('localhost', port))
            return True  # 端口被占用
    except (ConnectionRefusedError, OSError):
        return False  # 端口未被占用

def find_streamlit_processes():
    """找到所有 Streamlit 相關的程序"""
    streamlit_processes = []
    
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            # 檢查程序命令行是否包含 streamlit
            if proc.info['cmdline']:
                cmdline = ' '.join(proc.info['cmdline'])
                if 'streamlit' in cmdline.lower() and 'app_streamlit.py' in cmdline:
                    streamlit_processes.append(proc)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    
    return streamlit_processes

def stop_streamlit():
    """停止 Streamlit 服務"""
    logger = logging.getLogger(__name__)
    
    logger.info("正在搜尋 Streamlit 程序...")
    
    # 找到 Streamlit 程序
    processes = find_streamlit_processes()
    
    if not processes:
        if check_port_occupied(8501):
            logger.warning("端口 8501 被占用，但找不到 Streamlit 程序")
            logger.info("嘗試使用 netstat 查找占用程序...")
            
            # 在 Windows 上使用 netstat 找到占用端口的程序
            if sys.platform.startswith('win'):
                import subprocess
                try:
                    result = subprocess.run(['netstat', '-ano'], capture_output=True, text=True)
                    for line in result.stdout.split('\n'):
                        if ':8501' in line and 'LISTENING' in line:
                            parts = line.split()
                            if len(parts) >= 5:
                                pid = parts[-1]
                                logger.info(f"發現占用端口 8501 的程序 PID: {pid}")
                                try:
                                    proc = psutil.Process(int(pid))
                                    logger.info(f"程序名稱: {proc.name()}")
                                    proc.terminate()
                                    logger.info(f"已終止程序 {pid}")
                                except (psutil.NoSuchProcess, psutil.AccessDenied, ValueError):
                                    logger.error(f"無法終止程序 {pid}")
                except Exception as e:
                    logger.error(f"使用 netstat 查找程序時發生錯誤: {e}")
        else:
            logger.info("沒有發現運行中的 Streamlit 服務")
        return True
    
    # 終止找到的程序
    terminated_count = 0
    for proc in processes:
        try:
            logger.info(f"正在終止 Streamlit 程序 PID: {proc.pid}")
            proc.terminate()
            
            # 等待程序終止
            try:
                proc.wait(timeout=5)
                logger.info(f"程序 {proc.pid} 已正常終止")
                terminated_count += 1
            except psutil.TimeoutExpired:
                logger.warning(f"程序 {proc.pid} 未在 5 秒內終止，強制結束...")
                proc.kill()
                logger.info(f"程序 {proc.pid} 已強制終止")
                terminated_count += 1
                
        except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
            logger.error(f"無法終止程序 {proc.pid}: {e}")
    
    # 最終檢查
    if not check_port_occupied(8501):
        logger.info(f"成功停止 {terminated_count} 個 Streamlit 程序")
        logger.info("端口 8501 已釋放")
        return True
    else:
        logger.error("停止程序後端口 8501 仍被占用")
        return False

def main():
    """主函數"""
    logger = setup_logging()
    
    logger.info("=" * 50)
    logger.info("YouTube Financial Report Generator v3.0")
    logger.info("停止 Streamlit 服務")
    logger.info("=" * 50)
    
    success = stop_streamlit()
    
    if success:
        logger.info("Streamlit 服務已成功停止")
    else:
        logger.error("停止 Streamlit 服務時發生問題")
        return 1
    
    return 0

if __name__ == "__main__":
    try:
        import psutil
    except ImportError:
        print("缺少 psutil 套件，正在安裝...")
        import subprocess
        subprocess.run([sys.executable, "-m", "pip", "install", "psutil"], check=True)
        import psutil
    
    sys.exit(main())
