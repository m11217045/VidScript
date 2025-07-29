#!/usr/bin/env python3
"""
VidScript 版本管理工具
用於管理版本號碼、生成發布說明和標記版本
"""
import argparse
import os
import sys
import re
import subprocess
from datetime import datetime

# 確保可以導入版本模組
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, project_root)

from version import (
    __version__, 
    get_version, 
    get_full_version,
    get_release_notes,
    VERSION_MAJOR,
    VERSION_MINOR, 
    VERSION_PATCH,
    APP_NAME
)

class VersionManager:
    """版本管理器"""
    
    def __init__(self):
        self.current_version = __version__
        self.version_file = "version.py"
        
    def get_current_version(self):
        """獲取當前版本"""
        return self.current_version
    
    def increment_version(self, part="patch"):
        """增加版本號"""
        major, minor, patch = VERSION_MAJOR, VERSION_MINOR, VERSION_PATCH
        
        if part == "major":
            major += 1
            minor = 0
            patch = 0
        elif part == "minor":
            minor += 1
            patch = 0
        elif part == "patch":
            patch += 1
        else:
            raise ValueError("版本部分必須是 'major', 'minor' 或 'patch'")
            
        return f"{major}.{minor}.{patch}"
    
    def update_version_file(self, new_version, release_notes=None):
        """更新版本檔案"""
        try:
            with open(self.version_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 更新版本號
            content = re.sub(
                r'__version__ = "[^"]*"',
                f'__version__ = "{new_version}"',
                content
            )
            
            # 如果有發布說明，更新發布說明
            if release_notes:
                # 在 RELEASE_NOTES 字典中添加新版本
                notes_str = '",\n        "'.join(release_notes)
                new_release_entry = f'''    "{new_version}": [
        "{notes_str}"
    ],'''
                
                # 找到 RELEASE_NOTES 的位置並插入新版本
                content = re.sub(
                    r'(RELEASE_NOTES = \{)',
                    f'\\1\n{new_release_entry}',
                    content
                )
            
            with open(self.version_file, 'w', encoding='utf-8') as f:
                f.write(content)
                
            print(f"✅ 版本檔案已更新為 {new_version}")
            return True
            
        except Exception as e:
            print(f"❌ 更新版本檔案失敗: {e}")
            return False
    
    def create_git_tag(self, version):
        """創建 Git 標籤"""
        try:
            tag_name = f"v{version}"
            result = subprocess.run(
                ["git", "tag", "-a", tag_name, "-m", f"Release {tag_name}"],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print(f"✅ Git 標籤 {tag_name} 已創建")
                return True
            else:
                print(f"❌ 創建 Git 標籤失敗: {result.stderr}")
                return False
                
        except FileNotFoundError:
            print("⚠️ Git 不可用，跳過標籤創建")
            return False
    
    def generate_changelog(self):
        """生成變更日誌"""
        try:
            from version import RELEASE_NOTES
            
            changelog = f"# {APP_NAME} 變更日誌\n\n"
            changelog += f"本文件記錄了 {APP_NAME} 的所有重要變更。\n\n"
            
            # 按版本號排序（新版本在前）
            sorted_versions = sorted(
                RELEASE_NOTES.keys(), 
                key=lambda x: tuple(map(int, x.split('.'))), 
                reverse=True
            )
            
            for version in sorted_versions:
                changelog += f"## {version}\n\n"
                for note in RELEASE_NOTES[version]:
                    changelog += f"- {note}\n"
                changelog += "\n"
            
            # 寫入 CHANGELOG.md
            with open("CHANGELOG.md", "w", encoding="utf-8") as f:
                f.write(changelog)
            
            print("✅ CHANGELOG.md 已生成")
            return True
            
        except Exception as e:
            print(f"❌ 生成變更日誌失敗: {e}")
            return False

def main():
    parser = argparse.ArgumentParser(description="VidScript 版本管理工具")
    parser.add_argument("--current", action="store_true", help="顯示當前版本")
    parser.add_argument("--increment", choices=["major", "minor", "patch"], help="增加版本號")
    parser.add_argument("--set", help="設定特定版本號")
    parser.add_argument("--notes", nargs="+", help="發布說明（多個項目用空格分隔）")
    parser.add_argument("--tag", action="store_true", help="創建 Git 標籤")
    parser.add_argument("--changelog", action="store_true", help="生成變更日誌")
    
    args = parser.parse_args()
    
    vm = VersionManager()
    
    if args.current:
        print(f"當前版本: {get_full_version()}")
        print(f"發布說明:")
        for note in get_release_notes():
            print(f"  • {note}")
        return
    
    if args.changelog:
        vm.generate_changelog()
        return
    
    new_version = None
    
    if args.increment:
        new_version = vm.increment_version(args.increment)
        print(f"增加 {args.increment} 版本: {vm.current_version} → {new_version}")
    
    if args.set:
        # 驗證版本格式
        if re.match(r'^\d+\.\d+\.\d+$', args.set):
            new_version = args.set
            print(f"設定版本: {vm.current_version} → {new_version}")
        else:
            print("❌ 版本格式錯誤，請使用 MAJOR.MINOR.PATCH 格式")
            return
    
    if new_version:
        # 更新版本檔案
        success = vm.update_version_file(new_version, args.notes)
        
        if success and args.tag:
            vm.create_git_tag(new_version)
        
        if success:
            print(f"🎉 版本已更新為 {new_version}")
    
    if not any([args.current, args.increment, args.set, args.changelog]):
        parser.print_help()

if __name__ == "__main__":
    main()
