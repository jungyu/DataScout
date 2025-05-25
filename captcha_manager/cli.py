#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
驗證碼管理器命令行工具

提供命令行界面來執行和管理驗證碼解決任務。
"""

import asyncio
import logging
from pathlib import Path
from typing import Optional

import click
from loguru import logger

from captcha_manager.solver import CaptchaSolver
from captcha_manager.config import SolverConfig

@click.group()
@click.option('--config', '-c', type=click.Path(exists=True), help='配置文件路徑')
@click.option('--debug/--no-debug', default=False, help='啟用調試模式')
def cli(config: Optional[str], debug: bool):
    """驗證碼管理器命令行工具"""
    if debug:
        logger.add("captcha_manager.log", rotation="1 day", level="DEBUG")
    else:
        logger.add("captcha_manager.log", rotation="1 day", level="INFO")

@cli.command()
@click.argument('image_path', type=click.Path(exists=True))
@click.option('--type', '-t', type=str, default='image', help='驗證碼類型')
def solve(image_path: str, type: str):
    """解決指定路徑的驗證碼"""
    try:
        config = SolverConfig(type=type)
        solver = CaptchaSolver(config)
        result = asyncio.run(solver.solve(image_path))
        click.echo(f"驗證碼結果: {result}")
    except Exception as e:
        logger.error(f"解決驗證碼時出錯: {e}")
        raise click.ClickException(str(e))

@cli.command()
@click.argument('url', type=str)
@click.option('--type', '-t', type=str, default='image', help='驗證碼類型')
def solve_url(url: str, type: str):
    """解決指定 URL 的驗證碼"""
    try:
        config = SolverConfig(type=type)
        solver = CaptchaSolver(config)
        result = asyncio.run(solver.solve_url(url))
        click.echo(f"驗證碼結果: {result}")
    except Exception as e:
        logger.error(f"解決驗證碼時出錯: {e}")
        raise click.ClickException(str(e))

def main():
    """主函數"""
    cli() 