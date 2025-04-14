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
        "selenium>=4.0.0",
        "requests>=2.25.0",
        "beautifulsoup4>=4.9.0",
        "lxml>=4.9.0",
        "pillow>=8.0.0",
        "pyyaml>=5.4.0",
        "python-dotenv>=0.19.0",
        "click>=8.0.0",
        "tqdm>=4.62.0",
        "colorama>=0.4.4",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0.0",
            "pytest-cov>=2.12.0",
            "black>=21.5b2",
            "isort>=5.9.0",
            "flake8>=3.9.0",
            "mypy>=0.910",
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