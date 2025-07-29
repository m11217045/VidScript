"""
VidScript 安裝配置
YouTube 財經報告生成器
"""
from setuptools import setup, find_packages
import os
import sys

# 確保可以導入版本模組
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from version import (
        __version__, 
        APP_NAME, 
        APP_DESCRIPTION, 
        APP_NAME_EN,
        get_release_notes
    )
except ImportError:
    __version__ = "1.2.0"
    APP_NAME = "YouTube 財經報告生成器"
    APP_NAME_EN = "YouTube Financial Report Generator"
    APP_DESCRIPTION = "使用 AI 技術將 YouTube 財經影片轉換為結構化報告"
    def get_release_notes():
        return ["版本資訊載入失敗"]

# 讀取 README
def read_readme():
    try:
        with open("README.md", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return APP_DESCRIPTION

# 讀取需求檔案
def read_requirements():
    try:
        with open("config/requirements.txt", "r", encoding="utf-8") as f:
            requirements = []
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    requirements.append(line)
            return requirements
    except FileNotFoundError:
        return [
            "streamlit>=1.28.0",
            "faster-whisper>=1.0.0",
            "google-generativeai>=0.3.0",
            "python-dotenv>=1.0.0",
            "numpy>=1.21.0",
            "requests>=2.25.0"
        ]

setup(
    name="vidscript",
    version=__version__,
    description=APP_DESCRIPTION,
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    author="Development Team",
    author_email="",
    url="https://github.com/m11217045/VidScript",
    
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    
    python_requires=">=3.8",
    install_requires=read_requirements(),
    
    extras_require={
        "dev": [
            "pytest>=6.0",
            "black>=21.0",
            "flake8>=3.9",
            "isort>=5.0"
        ],
        "gpu": [
            "torch>=2.0.0+cu118",
            "torchvision>=0.15.0+cu118",
            "torchaudio>=2.0.0+cu118"
        ]
    },
    
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Multimedia :: Video",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: Microsoft :: Windows",
    ],
    
    keywords="youtube video transcription ai report generation",
    
    entry_points={
        "console_scripts": [
            "vidscript=src.ui.app_streamlit:main",
        ],
    },
    
    include_package_data=True,
    package_data={
        "": ["*.txt", "*.md", "*.yml", "*.yaml"],
    },
    
    zip_safe=False,
)

if __name__ == "__main__":
    print(f"設定 {APP_NAME_EN} {__version__}")
    print(f"描述: {APP_DESCRIPTION}")
    print(f"發布說明:")
    for note in get_release_notes():
        print(f"  • {note}")
