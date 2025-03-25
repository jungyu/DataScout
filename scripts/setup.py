from setuptools import setup, find_packages

setup(
    name='crawler-selenium',
    version='0.1.0',
    description='A web crawler using Selenium',
    author='Aaron',
    author_email='your.email@example.com',
    packages=find_packages(),
    install_requires=[
        'selenium>=4.0.0',
        'webdriver_manager>=3.8.0',
        'pandas>=1.3.0',
        'requests>=2.26.0',
        'beautifulsoup4>=4.9.3',
    ],
    python_requires='>=3.7',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
)
