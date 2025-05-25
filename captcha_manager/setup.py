from setuptools import setup, find_packages

setup(
    name="captcha_manager",
    version="0.1.0",
    description="驗證碼管理工具，提供多種驗證碼解決方案",
    author="DataScout Team",
    author_email="info@datascout.com",
    packages=find_packages(),
    install_requires=[
        "aiohttp>=3.9.0",
        "pydantic>=2.0.0",
        "loguru>=0.7.0",
        "playwright>=1.40.0",
        "pillow>=10.0.0",
        "numpy>=1.24.0",
    ],
    entry_points={
        "console_scripts": [
            "captcha-manager=captcha_manager.cli:main",
        ],
    },
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