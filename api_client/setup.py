from setuptools import setup, find_packages

setup(
    name="api_client",
    version="0.1.0",
    description="API 客戶端包，提供統一的 API 調用接口",
    author="DataScout Team",
    author_email="info@datascout.com",
    packages=find_packages(),
    install_requires=[
        "aiohttp>=3.9.0",
        "pydantic>=2.0.0",
        "loguru>=0.7.0",
        "typing-extensions>=4.0.0",
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