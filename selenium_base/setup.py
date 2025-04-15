"""
DataScout Core 安裝配置
"""

from setuptools import setup, find_packages

setup(
    name="selenium_base",
    version="0.1.0",
    description="DataScout Core Library for Web Scraping",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="DataScout Team",
    author_email="team@datascout.com",
    url="https://github.com/datascout/selenium_base",
    packages=find_packages(),
    install_requires=[
        "selenium>=4.18.1",
        "requests>=2.31.0",
        "beautifulsoup4>=4.12.3",
        "lxml>=5.1.0",
        "pillow>=10.2.0",
        "pyyaml>=6.0.1",
        "python-dotenv>=1.0.1",
        "click>=8.1.7",
        "tqdm>=4.66.2",
        "colorama>=0.4.6",
        "data_scout_extractors>=0.1.0",
        "webdriver_manager>=4.0.1",
        "undetected-chromedriver>=3.5.5",
        "fake-useragent>=1.4.0",
    ],
    extras_require={
        "dev": [
            "pytest>=8.0.2",
            "pytest-cov>=4.1.0",
            "black>=24.2.0",
            "isort>=5.13.2",
            "flake8>=7.0.0",
            "mypy>=1.8.0",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "selenium_base=selenium_base.core.cli:main",
        ],
    },
) 