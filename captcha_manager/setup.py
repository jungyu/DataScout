from setuptools import setup, find_packages

setup(
    name="captcha_manager",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "selenium>=4.0.0",
        "playwright>=1.30.0",
        "pillow>=9.0.0",
        "requests>=2.26.0",
        "python-dotenv>=0.19.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0.0",
            "black>=21.0.0",
            "isort>=5.0.0",
            "mypy>=0.900",
            "flake8>=3.9.0",
        ],
    },
    author="Your Name",
    author_email="your.email@example.com",
    description="A flexible captcha management system for web automation",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/captcha_manager",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
) 