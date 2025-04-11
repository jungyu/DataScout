from setuptools import setup, find_packages

setup(
    name="datascout",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "selenium>=4.0.0",
        "webdriver_manager>=3.8.0",
        "requests>=2.26.0",
        "beautifulsoup4>=4.9.3",
        "pandas>=1.3.0",
        "numpy>=1.21.0",
        "python-dotenv>=0.19.0",
        "fastapi>=0.68.0",
        "uvicorn>=0.15.0",
    ],
    author="Your Name",
    author_email="your.email@example.com",
    description="A powerful web automation and data collection framework",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/DataScout",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
) 