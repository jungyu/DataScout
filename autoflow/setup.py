from setuptools import setup, find_packages

setup(
    name="autoflow",
    version="0.1.0",
    package_dir={"": "autoflow"},
    packages=find_packages(where="autoflow"),
    install_requires=[
        "python-dotenv==1.0.1",
        "supabase>=2.0.0",
        "yfinance==0.2.36",
        "pandas==2.2.1",
        "python-telegram-bot==20.6",
        "aiohttp==3.9.3",
        "asyncio==3.4.3",
        "httpx==0.25.2",
    ],
    python_requires=">=3.8",
) 