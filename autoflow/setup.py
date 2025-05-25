from setuptools import setup, find_packages

setup(
    name="autoflow",
    version="0.1.0",
    description="自動化工作流程框架",
    author="DataScout Team",
    author_email="info@datascout.com",
    packages=find_packages(),
    install_requires=[
        "aiohttp>=3.9.0",
        "pydantic>=2.0.0",
        "loguru>=0.7.0",
        "python-telegram-bot>=20.6",
        "supabase>=2.0.0",
        "playwright>=1.40.0",
    ],
    entry_points={
        "console_scripts": [
            "autoflow=autoflow.cli:main",
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