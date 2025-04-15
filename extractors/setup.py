from setuptools import setup, find_packages

setup(
    name="data_scout_extractors",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "beautifulsoup4>=4.9.3",
        "lxml>=4.9.0",
        "pandas>=1.3.0",
        "numpy>=1.21.0",
    ],
    author="DataScout Team",
    author_email="your.email@example.com",
    description="A collection of data extractors for various data sources",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/data_scout",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
) 