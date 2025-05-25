#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Selenium 基礎工具包命令行工具

提供命令行界面來執行和管理瀏覽器自動化任務。
"""

import asyncio
import logging
from pathlib import Path
from typing import Optional

import click
from loguru import logger

from selenium_base.core.browser import Browser
from selenium_base.core.config import BrowserConfig

@click.group()
@click.option('--config', '-c', type=click.Path(exists=True), help='配置文件路徑')
@click.option('--debug/--no-debug', default=False, help='啟用調試模式')
def cli(config: Optional[str], debug: bool):
    """Selenium 基礎工具包命令行工具"""
    if debug:
        logger.add("selenium_base.log", rotation="1 day", level="DEBUG")
    else:
        logger.add("selenium_base.log", rotation="1 day", level="INFO")

@cli.command()
@click.argument('url', type=str)
@click.option('--browser', '-b', type=str, default='chrome', help='瀏覽器類型')
@click.option('--headless/--no-headless', default=False, help='無頭模式')
def browse(url: str, browser: str, headless: bool):
    """使用指定瀏覽器訪問 URL"""
    try:
        config = BrowserConfig(
            browser_type=browser,
            headless=headless
        )
        browser = Browser(config)
        asyncio.run(browser.visit(url))
    except Exception as e:
        logger.error(f"訪問 URL 時出錯: {e}")
        raise click.ClickException(str(e))

@cli.command()
@click.argument('script_path', type=click.Path(exists=True))
@click.option('--browser', '-b', type=str, default='chrome', help='瀏覽器類型')
@click.option('--headless/--no-headless', default=False, help='無頭模式')
def run_script(script_path: str, browser: str, headless: bool):
    """執行自動化腳本"""
    try:
        config = BrowserConfig(
            browser_type=browser,
            headless=headless
        )
        browser = Browser(config)
        asyncio.run(browser.run_script(script_path))
    except Exception as e:
        logger.error(f"執行腳本時出錯: {e}")
        raise click.ClickException(str(e))

def main():
    """主函數"""
    cli() 