#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
安裝配置文件

此模組提供項目的安裝配置，包括：
1. 項目基本信息
2. 依賴包管理
3. 開發工具配置
4. 測試配置
"""

from setuptools import setup, find_packages

# 項目基本信息
PROJECT_NAME = "crawler-selenium"
VERSION = "1.0.0"
DESCRIPTION = "基於 Selenium 的智能爬蟲框架"
AUTHOR = "Aaron-Yu"
AUTHOR_EMAIL = "jungyuyu@gmail.com"
URL = "https://github.com/Aaron-Yu/crawler-selenium"
LICENSE = "MIT"

# 依賴包
INSTALL_REQUIRES = [
    # 核心依賴
    "selenium>=4.16.0",
    "webdriver_manager>=4.0.1",
    "requests>=2.31.0",
    "beautifulsoup4>=4.12.2",
    
    # 數據處理
    "pandas>=2.1.4",
    "numpy>=1.26.2",
    
    # 數據分析
    "matplotlib>=3.8.2",
    "seaborn>=0.13.0",
    
    # 工具庫
    "python-dotenv>=1.0.0",
    "pyyaml>=6.0.1",
    "tqdm>=4.66.1",
    
    # 日誌和監控
    "loguru>=0.7.2",
    "prometheus-client>=0.19.0",
    
    # 安全相關
    "cryptography>=41.0.7",
    "python-jose>=3.3.0",
]

# 開發依賴
EXTRAS_REQUIRE = {
    "dev": [
        "pytest>=7.4.3",
        "pytest-cov>=4.1.0",
        "black>=23.11.0",
        "isort>=5.12.0",
        "flake8>=6.1.0",
        "mypy>=1.7.1",
        "pre-commit>=3.5.0",
    ],
    "docs": [
        "sphinx>=7.2.6",
        "sphinx-rtd-theme>=1.3.0",
        "sphinx-autodoc-typehints>=1.24.0",
    ],
}

# 項目分類信息
CLASSIFIERS = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
    "Programming Language :: Python",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Topic :: Software Development :: Libraries :: Python Modules",
    "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
]

setup(
    name=PROJECT_NAME,
    version=VERSION,
    description=DESCRIPTION,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    url=URL,
    license=LICENSE,
    packages=find_packages(include=["src", "src.*"]),
    package_data={
        "src": ["config/*.json", "templates/*.json"],
    },
    install_requires=INSTALL_REQUIRES,
    extras_require=EXTRAS_REQUIRE,
    python_requires=">=3.8",
    classifiers=CLASSIFIERS,
    entry_points={
        "console_scripts": [
            "crawler=src.main:main",
            "crawler-analyze=scripts.analyze_results:main",
        ],
    },
)
