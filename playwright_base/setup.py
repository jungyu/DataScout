from setuptools import setup, find_packages

setup(
    name="playwright_base",
    version="0.1.0",
    description="基於 Playwright 的網頁自動化與數據採集框架，提供強大的反檢測功能",
    author="DataScout Team",
    author_email="info@datascout.com",
    packages=find_packages(),
    install_requires=[
        "playwright>=1.40.0",
        "python-dotenv>=1.0.0",
        "user-agents>=2.2.0",
        "requests>=2.28.0",
        "pillow>=9.0.0",
        "loguru>=0.7.0",
        "beautifulsoup4>=4.12.0"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)