from setuptools import setup, find_packages

setup(
    name="adapter",
    version="0.1.0",
    description="適配器模式實現，提供靈活的數據轉換和接口適配功能",
    author="DataScout Team",
    author_email="info@datascout.com",
    packages=find_packages(),
    install_requires=[
        "pydantic>=2.0.0",
        "typing-extensions>=4.0.0",
        "loguru>=0.7.0",
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