from setuptools import setup, find_packages

setup(
    name="telegram-bot",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "python-telegram-bot==20.6",
        "python-dotenv==1.0.1",
        "aiohttp==3.9.3",
        "asyncio==3.4.3",
    ],
    python_requires=">=3.8",
    author="DataScout",
    author_email="your.email@example.com",
    description="一個可擴展的 Telegram 機器人框架",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/telegram-bot",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    entry_points={
        "console_scripts": [
            "telegram-bot=telegram_bot.bot:main",
        ],
    },
) 