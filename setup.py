from setuptools import setup, find_packages

setup(
    name="crawler-selenium",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "selenium>=4.0.0",
        "webdriver_manager>=3.8.0",
        "beautifulsoup4>=4.9.3",
        "lxml>=4.9.0"
    ],
) 