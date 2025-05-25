from setuptools import setup, find_packages

setup(
    name="autoflow",
    version="0.1.0",
    packages=find_packages(include=['autoflow', 'autoflow.*']),
    install_requires=[
        "python-dotenv==1.0.1",
        "supabase==2.3.1",
        "yfinance==0.2.36",
        "pandas==2.2.1",
        "python-telegram-bot==20.6",
        "aiohttp==3.9.3",
        "asyncio==3.4.3",
        "httpx~=0.25.0",
    ],
    python_requires=">=3.8",
) 