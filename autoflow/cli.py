#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
AutoFlow 命令行工具

提供命令行界面來執行和管理工作流程。
"""

import asyncio
import logging
from pathlib import Path
from typing import Optional

import click
from loguru import logger

from autoflow.core.flow import Flow
from autoflow.utils.config import load_config

@click.group()
@click.option('--config', '-c', type=click.Path(exists=True), help='配置文件路徑')
@click.option('--debug/--no-debug', default=False, help='啟用調試模式')
def cli(config: Optional[str], debug: bool):
    """AutoFlow 命令行工具"""
    if debug:
        logger.add("autoflow.log", rotation="1 day", level="DEBUG")
    else:
        logger.add("autoflow.log", rotation="1 day", level="INFO")

@cli.command()
@click.argument('flow_path', type=click.Path(exists=True))
def run(flow_path: str):
    """運行指定的工作流程"""
    try:
        flow = Flow.from_file(flow_path)
        asyncio.run(flow.start())
    except Exception as e:
        logger.error(f"運行工作流程時出錯: {e}")
        raise click.ClickException(str(e))

@cli.command()
@click.argument('flow_path', type=click.Path(exists=True))
def stop(flow_path: str):
    """停止指定的工作流程"""
    try:
        flow = Flow.from_file(flow_path)
        asyncio.run(flow.stop())
    except Exception as e:
        logger.error(f"停止工作流程時出錯: {e}")
        raise click.ClickException(str(e))

@cli.command()
@click.argument('flow_path', type=click.Path(exists=True))
def status(flow_path: str):
    """查看工作流程狀態"""
    try:
        flow = Flow.from_file(flow_path)
        click.echo(f"工作流程狀態: {'運行中' if flow.is_running else '已停止'}")
    except Exception as e:
        logger.error(f"獲取工作流程狀態時出錯: {e}")
        raise click.ClickException(str(e))

def main():
    """主函數"""
    cli() 