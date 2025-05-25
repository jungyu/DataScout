#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
數據提取器命令行工具

提供命令行界面來執行和管理數據提取任務。
"""

import asyncio
import logging
from pathlib import Path
from typing import Optional

import click
from loguru import logger

from extractors.core.extractor import BaseExtractor
from extractors.core.config import ExtractorConfig

@click.group()
@click.option('--config', '-c', type=click.Path(exists=True), help='配置文件路徑')
@click.option('--debug/--no-debug', default=False, help='啟用調試模式')
def cli(config: Optional[str], debug: bool):
    """數據提取器命令行工具"""
    if debug:
        logger.add("extractors.log", rotation="1 day", level="DEBUG")
    else:
        logger.add("extractors.log", rotation="1 day", level="INFO")

@cli.command()
@click.argument('url', type=str)
@click.option('--type', '-t', type=str, required=True, help='提取器類型')
@click.option('--output', '-o', type=click.Path(), help='輸出文件路徑')
def extract(url: str, type: str, output: Optional[str]):
    """從指定 URL 提取數據"""
    try:
        config = ExtractorConfig(type=type)
        extractor = BaseExtractor.create(config)
        result = asyncio.run(extractor.extract(url))
        
        if output:
            with open(output, 'w', encoding='utf-8') as f:
                f.write(str(result))
        else:
            click.echo(result)
    except Exception as e:
        logger.error(f"提取數據時出錯: {e}")
        raise click.ClickException(str(e))

@cli.command()
@click.argument('file_path', type=click.Path(exists=True))
@click.option('--type', '-t', type=str, required=True, help='提取器類型')
@click.option('--output', '-o', type=click.Path(), help='輸出文件路徑')
def extract_file(file_path: str, type: str, output: Optional[str]):
    """從指定文件提取數據"""
    try:
        config = ExtractorConfig(type=type)
        extractor = BaseExtractor.create(config)
        result = asyncio.run(extractor.extract_file(file_path))
        
        if output:
            with open(output, 'w', encoding='utf-8') as f:
                f.write(str(result))
        else:
            click.echo(result)
    except Exception as e:
        logger.error(f"提取數據時出錯: {e}")
        raise click.ClickException(str(e))

def main():
    """主函數"""
    cli() 