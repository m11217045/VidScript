"""
VidScript 專案環境檢測工具
檢測和驗證專案的 Python 環境設定
"""
import os
import sys
import subprocess

def get_project_root():
    """獲取專案根目錄"""
    current_file = os.path.abspath(__file__)
    # tools/check_environment.py -> project_root
    return os.path.dirname(os.path.dirname(current_file))

def detect_virtual_environments():
    """檢測所有可能的虛擬環境"""
    print("🔍 檢測虛擬環境...")
    
    project_root = get_project_root()
    print(f"📁 專案根目錄: {project_root}")
    
    # 常見的虛擬環境目錄名稱
    venv_names = ['venv', '.venv', 'env', '.env', 'virtualenv']
    
    # 搜尋位置
    search_paths = [
        project_root,  # 專案根目錄
        os.path.dirname(project_root),  # 上一層目錄
        os.path.join(os.path.expanduser("~"), "anaconda3", "envs"),  # Anaconda 環境
        os.path.join(os.path.expanduser("~"), "miniconda3", "envs"),  # Miniconda 環境
    ]
    
    found_environments = []
    
    # 檢查標準虛擬環境
    for search_path in search_paths[:2]:  # 只檢查專案相關路徑
        for venv_name in venv_names:
            venv_path = os.path.join(search_path, venv_name)
            if os.path.exists(venv_path):
                python_exe = get_python_executable(venv_path)
                if python_exe:
                    found_environments.append({
                        'type': 'venv',
                        'name': venv_name,
                        'path': venv_path,
                        'python': python_exe,
                        'location': 'project' if search_path == project_root else 'parent'
                    })
    
    # 檢查 Conda 環境
    conda_envs = detect_conda_environments()
    found_environments.extend(conda_envs)
    
    return found_environments

def get_python_executable(venv_path):
    """獲取虛擬環境的 Python 執行檔路徑"""
    if os.name == 'nt':  # Windows
        possible_paths = [
            os.path.join(venv_path, 'Scripts', 'python.exe'),
            os.path.join(venv_path, 'python.exe'),
        ]
    else:  # Linux/Mac
        possible_paths = [
            os.path.join(venv_path, 'bin', 'python'),
            os.path.join(venv_path, 'bin', 'python3'),
        ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return path
    return None

def detect_conda_environments():
    """檢測 Conda 環境"""
    conda_envs = []
    
    try:
        # 嘗試運行 conda env list
        result = subprocess.run(['conda', 'env', 'list'], 
                              capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            for line in lines:
                if line.strip() and not line.startswith('#'):
                    parts = line.split()
                    if len(parts) >= 2:
                        env_name = parts[0]
                        env_path = parts[-1]
                        
                        # 檢查是否是有效路徑
                        if os.path.exists(env_path):
                            python_exe = get_python_executable(env_path)
                            if python_exe:
                                conda_envs.append({
                                    'type': 'conda',
                                    'name': env_name,
                                    'path': env_path,
                                    'python': python_exe,
                                    'location': 'system'
                                })
    except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.CalledProcessError):
        pass  # Conda 不可用
    
    return conda_envs

def get_current_environment_info():
    """獲取當前環境資訊"""
    print("\n🐍 當前 Python 環境資訊:")
    
    current_python = sys.executable
    python_version = sys.version
    virtual_env = os.environ.get('VIRTUAL_ENV', None)
    conda_env = os.environ.get('CONDA_DEFAULT_ENV', None)
    
    print(f"   Python 執行檔: {current_python}")
    print(f"   Python 版本: {python_version}")
    
    if virtual_env:
        print(f"   虛擬環境: {virtual_env}")
    elif conda_env:
        print(f"   Conda 環境: {conda_env}")
    else:
        print("   環境類型: 系統 Python")
    
    return {
        'python': current_python,
        'version': python_version,
        'virtual_env': virtual_env,
        'conda_env': conda_env
    }

def check_environment_packages(python_exe):
    """檢查指定環境中的套件"""
    try:
        # 檢查關鍵套件
        packages_to_check = [
            'torch', 'faster_whisper', 'streamlit', 
            'google-generativeai', 'numpy', 'psutil'
        ]
        
        installed_packages = {}
        
        for package in packages_to_check:
            try:
                result = subprocess.run([
                    python_exe, '-c', 
                    f'import {package.replace("-", "_")}; print({package.replace("-", "_")}.__version__)'
                ], capture_output=True, text=True, timeout=10)
                
                if result.returncode == 0:
                    version = result.stdout.strip()
                    installed_packages[package] = version
                else:
                    installed_packages[package] = None
            except:
                installed_packages[package] = None
        
        return installed_packages
    except Exception as e:
        print(f"   ❌ 檢查套件時發生錯誤: {e}")
        return {}

def display_environment_summary(environments):
    """顯示環境摘要"""
    print(f"\n📊 發現 {len(environments)} 個虛擬環境:")
    
    if not environments:
        print("   沒有找到虛擬環境")
        return
    
    current_python = sys.executable
    
    for i, env in enumerate(environments, 1):
        print(f"\n{i}. {env['name']} ({env['type']})")
        print(f"   📁 路徑: {env['path']}")
        print(f"   🐍 Python: {env['python']}")
        print(f"   📍 位置: {env['location']}")
        
        # 檢查是否是當前環境
        if current_python == env['python'] or current_python.startswith(env['path']):
            print("   ✅ 當前使用中")
        
        # 檢查套件
        print("   📦 檢查關鍵套件...")
        packages = check_environment_packages(env['python'])
        
        for package, version in packages.items():
            if version:
                print(f"      ✅ {package}: {version}")
            else:
                print(f"      ❌ {package}: 未安裝")

def recommend_environment(environments):
    """推薦最佳環境"""
    print("\n💡 環境建議:")
    
    current_python = sys.executable
    project_root = get_project_root()
    
    # 尋找專案相關的環境
    project_envs = [env for env in environments 
                   if env['location'] == 'project' and 
                   env['path'].startswith(project_root)]
    
    if project_envs:
        best_env = project_envs[0]
        packages = check_environment_packages(best_env['python'])
        
        if all(packages.get(pkg) for pkg in ['torch', 'faster_whisper', 'streamlit']):
            print(f"✅ 建議使用專案環境: {best_env['name']}")
            print(f"   路徑: {best_env['path']}")
            print("   該環境已安裝所需套件")
        else:
            print(f"⚠️ 專案環境 {best_env['name']} 缺少部分套件")
            print("   建議運行: pip install -r scripts/requirements.txt")
    else:
        print("💡 建議創建專案虛擬環境:")
        print("   python -m venv venv")
        print("   # Windows: venv\\Scripts\\activate")
        print("   # Linux/Mac: source venv/bin/activate")
        print("   pip install -r scripts/requirements.txt")

def main():
    """主函數"""
    print("🔧 VidScript 專案環境檢測工具\n")
    
    # 顯示當前環境
    current_info = get_current_environment_info()
    
    # 檢測所有虛擬環境
    environments = detect_virtual_environments()
    
    # 顯示環境摘要
    display_environment_summary(environments)
    
    # 提供建議
    recommend_environment(environments)
    
    print(f"\n📁 專案根目錄: {get_project_root()}")
    print("🎯 要進行性能測試，請運行: python test_speed.py")
    print("💡 如需故障排除，請參考 README.md 中的說明")

if __name__ == "__main__":
    main()
