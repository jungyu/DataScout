#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
日誌處理工具模組

提供日誌處理相關的工具類和函數，包括：
1. 日誌配置
2. 日誌格式化
3. 日誌過濾
4. 日誌輪轉
5. 日誌壓縮
6. 日誌清理
7. 日誌分析
8. 日誌聚合
9. 日誌告警
10. 日誌導出
11. 日誌搜索
"""

import os
import gzip
import shutil
import logging
import logging.handlers
import json
import csv
import re
import smtplib
import requests
from email.mime.text import MIMEText
from typing import Optional, Dict, Any, List, Tuple, Union
from pathlib import Path
from dataclasses import dataclass
from datetime import datetime, timedelta
from collections import defaultdict

def setup_logger(name: str, 
                level_name: str = 'INFO',
                log_dir: str = 'logs',
                log_file: Optional[str] = None,
                console_output: bool = True,
                file_output: bool = True) -> 'Logger':
    """
    設置並返回一個日誌記錄器
    
    Args:
        name: 日誌記錄器名稱
        level_name: 日誌等級名稱
        log_dir: 日誌目錄
        log_file: 日誌文件名
        console_output: 是否輸出到控制台
        file_output: 是否輸出到文件
        
    Returns:
        配置好的日誌記錄器
    """
    level = getattr(logging, level_name.upper())
    config = LogConfig(
        level_name=level_name,
        log_dir=log_dir,
        log_file=log_file,
        console_output=console_output,
        file_output=file_output
    )
    return Logger(name, config)

@dataclass
class LogConfig:
    """日誌配置數據類"""
    level_name: str = 'INFO'
    format: str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    date_format: str = '%Y-%m-%d %H:%M:%S'
    log_dir: str = 'logs'
    log_file: Optional[str] = None
    max_bytes: int = 10 * 1024 * 1024  # 10MB
    backup_count: int = 5
    console_output: bool = True
    file_output: bool = True
    compress_logs: bool = True
    max_days: int = 30
    analyze_logs: bool = True
    alert_threshold: int = 10  # 錯誤數量閾值
    alert_interval: int = 300  # 告警間隔（秒）
    alert_email: Optional[str] = None
    alert_webhook: Optional[str] = None
    alert_smtp_server: Optional[str] = None
    alert_smtp_port: Optional[int] = None
    alert_smtp_user: Optional[str] = None
    alert_smtp_password: Optional[str] = None
    
    @property
    def level(self) -> int:
        """獲取日誌等級"""
        return getattr(logging, self.level_name.upper())

class LogFilter(logging.Filter):
    """日誌過濾器"""
    
    def __init__(self, name: str = '', level: int = logging.NOTSET):
        """
        初始化過濾器
        
        Args:
            name: 過濾器名稱
            level: 日誌等級
        """
        super().__init__(name)
        self.level = level
        
    def filter(self, record: logging.LogRecord) -> bool:
        """
        過濾日誌記錄
        
        Args:
            record: 日誌記錄
            
        Returns:
            是否通過過濾
        """
        return record.levelno >= self.level

class LogFormatter(logging.Formatter):
    """日誌格式化器"""
    
    def __init__(self, fmt: str = None, datefmt: str = None):
        """
        初始化格式化器
        
        Args:
            fmt: 格式化字符串
            datefmt: 日期格式化字符串
        """
        super().__init__(fmt, datefmt)
        
    def format(self, record: logging.LogRecord) -> str:
        """
        格式化日誌記錄
        
        Args:
            record: 日誌記錄
            
        Returns:
            格式化後的日誌字符串
        """
        # 添加額外的上下文信息
        if not hasattr(record, 'context'):
            record.context = {}
            
        # 格式化消息
        message = super().format(record)
        
        # 如果有上下文信息，添加到消息末尾
        if record.context:
            context_str = ' '.join(f'{k}={v}' for k, v in record.context.items())
            message = f'{message} [{context_str}]'
            
        return message

class Logger:
    """日誌處理工具類"""
    
    def __init__(self, name: str, config: Optional[LogConfig] = None):
        """
        初始化日誌處理器
        
        Args:
            name: 日誌記錄器名稱
            config: 日誌配置
        """
        self.name = name
        self.config = config or LogConfig()
        self.logger = self._setup_logger()
        self._error_count = 0
        self._last_alert_time = datetime.now()
        self._context = {}
        
    def _setup_logger(self) -> logging.Logger:
        """
        設置日誌記錄器
        
        Returns:
            配置好的日誌記錄器
        """
        logger = logging.getLogger(self.name)
        logger.setLevel(self.config.level)
        
        # 清除現有的處理器
        logger.handlers.clear()
        
        # 創建格式化器
        formatter = LogFormatter(
            fmt=self.config.format,
            datefmt=self.config.date_format
        )
        
        # 添加控制台處理器
        if self.config.console_output:
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)
            
        # 添加文件處理器
        if self.config.file_output and self.config.log_file:
            # 確保日誌目錄存在
            log_dir = Path(self.config.log_dir)
            log_dir.mkdir(parents=True, exist_ok=True)
            
            # 創建文件處理器
            file_handler = logging.handlers.RotatingFileHandler(
                filename=log_dir / self.config.log_file,
                maxBytes=self.config.max_bytes,
                backupCount=self.config.backup_count,
                encoding='utf-8'
            )
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
            
        return logger
        
    def _log(self, level: int, msg: str, context: Optional[Dict[str, Any]] = None, **kwargs):
        """
        記錄日誌
        
        Args:
            level: 日誌等級
            msg: 日誌消息
            context: 上下文信息
            **kwargs: 其他參數
        """
        # 合併上下文信息
        log_context = self._context.copy()
        if context:
            log_context.update(context)
            
        # 創建日誌記錄
        record = self.logger.makeRecord(
            self.name,
            level,
            "",
            0,
            msg,
            None,
            None
        )
        record.context = log_context
        
        # 處理日誌
        self.logger.handle(record)
        
        # 檢查是否需要發送告警
        if level >= logging.ERROR:
            self._error_count += 1
            self._check_alert()
            
    def _check_alert(self) -> None:
        """檢查是否需要發送告警"""
        now = datetime.now()
        if (self._error_count >= self.config.alert_threshold and 
            (now - self._last_alert_time).total_seconds() >= self.config.alert_interval):
            
            # 發送告警
            alert_msg = f"錯誤數量超過閾值: {self._error_count}"
            if self.config.alert_email:
                self._send_email_alert(alert_msg)
            if self.config.alert_webhook:
                self._send_webhook_alert(alert_msg)
                
            # 更新告警時間
            self._last_alert_time = now
            
    def _send_email_alert(self, message: str) -> None:
        """
        發送郵件告警
        
        Args:
            message: 告警消息
        """
        if not all([self.config.alert_smtp_server, self.config.alert_smtp_port,
                   self.config.alert_smtp_user, self.config.alert_smtp_password]):
            self.logger.warning("郵件告警配置不完整")
            return
            
        try:
            msg = MIMEText(message)
            msg['Subject'] = f"日誌告警 - {self.name}"
            msg['From'] = self.config.alert_smtp_user
            msg['To'] = self.config.alert_email
            
            with smtplib.SMTP(self.config.alert_smtp_server, self.config.alert_smtp_port) as server:
                server.starttls()
                server.login(self.config.alert_smtp_user, self.config.alert_smtp_password)
                server.send_message(msg)
                
        except Exception as e:
            self.logger.error(f"發送郵件告警失敗: {str(e)}")
            
    def _send_webhook_alert(self, message: str) -> None:
        """
        發送Webhook告警
        
        Args:
            message: 告警消息
        """
        try:
            data = {
                'logger': self.name,
                'message': message,
                'timestamp': datetime.now().isoformat()
            }
            requests.post(self.config.alert_webhook, json=data)
            
        except Exception as e:
            self.logger.error(f"發送Webhook告警失敗: {str(e)}")
            
    def debug(self, msg: str, context: Optional[Dict[str, Any]] = None, **kwargs):
        """記錄調試日誌"""
        self._log(logging.DEBUG, msg, context, **kwargs)
        
    def info(self, msg: str, context: Optional[Dict[str, Any]] = None, **kwargs):
        """記錄信息日誌"""
        self._log(logging.INFO, msg, context, **kwargs)
        
    def warning(self, msg: str, context: Optional[Dict[str, Any]] = None, **kwargs):
        """記錄警告日誌"""
        self._log(logging.WARNING, msg, context, **kwargs)
        
    def error(self, msg: str, context: Optional[Dict[str, Any]] = None, **kwargs):
        """記錄錯誤日誌"""
        self._log(logging.ERROR, msg, context, **kwargs)
        
    def critical(self, msg: str, context: Optional[Dict[str, Any]] = None, **kwargs):
        """記錄嚴重錯誤日誌"""
        self._log(logging.CRITICAL, msg, context, **kwargs)
        
    def exception(self, msg: str, context: Optional[Dict[str, Any]] = None, **kwargs):
        """記錄異常日誌"""
        self._log(logging.ERROR, msg, context, exc_info=True, **kwargs)
        
    def add_context(self, **kwargs):
        """添加上下文信息"""
        self._context.update(kwargs)
        
    def clear_context(self):
        """清除上下文信息"""
        self._context.clear()
        
    def get_logger(self) -> logging.Logger:
        """
        獲取底層日誌記錄器
        
        Returns:
            日誌記錄器
        """
        return self.logger
        
    def compress_logs(self) -> None:
        """壓縮日誌文件"""
        if not self.config.compress_logs:
            return
            
        log_dir = Path(self.config.log_dir)
        if not log_dir.exists():
            return
            
        # 獲取所有日誌文件
        log_files = list(log_dir.glob("*.log.*"))
        
        for log_file in log_files:
            # 跳過已經壓縮的文件
            if log_file.suffix == '.gz':
                continue
                
            # 壓縮文件
            with open(log_file, 'rb') as f_in:
                with gzip.open(f"{log_file}.gz", 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
                    
            # 刪除原文件
            log_file.unlink()
            
    def clean_logs(self, days: Optional[int] = None) -> None:
        """
        清理舊日誌文件
        
        Args:
            days: 保留的天數，如果為None則使用配置中的值
        """
        if days is None:
            days = self.config.max_days
            
        log_dir = Path(self.config.log_dir)
        if not log_dir.exists():
            return
            
        # 獲取所有日誌文件
        log_files = list(log_dir.glob("*.log*"))
        cutoff_date = datetime.now() - timedelta(days=days)
        
        for log_file in log_files:
            try:
                # 從文件名中提取日期
                date_match = re.search(r'\d{4}-\d{2}-\d{2}', log_file.name)
                if date_match:
                    file_date = datetime.strptime(date_match.group(), '%Y-%m-%d')
                    if file_date < cutoff_date:
                        log_file.unlink()
                else:
                    # 如果無法從文件名提取日期，使用文件修改時間
                    mtime = datetime.fromtimestamp(log_file.stat().st_mtime)
                    if mtime < cutoff_date:
                        log_file.unlink()
                        
            except Exception as e:
                self.logger.error(f"清理日誌文件失敗: {str(e)}")
                
    def analyze_logs(self, log_file: Optional[str] = None) -> Dict[str, Any]:
        """
        分析日誌文件
        
        Args:
            log_file: 日誌文件路徑，如果為None則使用當前日誌文件
            
        Returns:
            分析結果
        """
        if not self.config.analyze_logs:
            return {}
            
        if log_file is None:
            log_file = Path(self.config.log_dir) / self.config.log_file
            
        if not Path(log_file).exists():
            return {}
            
        try:
            # 初始化統計數據
            stats = {
                'total_lines': 0,
                'level_counts': defaultdict(int),
                'error_messages': [],
                'warning_messages': [],
                'start_time': None,
                'end_time': None,
                'duration': None
            }
            
            # 分析日誌文件
            with open(log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    stats['total_lines'] += 1
                    
                    # 提取日誌等級
                    level_match = re.search(r' - (\w+) - ', line)
                    if level_match:
                        level = level_match.group(1)
                        stats['level_counts'][level] += 1
                        
                    # 提取時間戳
                    time_match = re.search(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', line)
                    if time_match:
                        timestamp = datetime.strptime(time_match.group(1), '%Y-%m-%d %H:%M:%S')
                        if stats['start_time'] is None:
                            stats['start_time'] = timestamp
                        stats['end_time'] = timestamp
                        
                    # 提取錯誤和警告消息
                    if ' - ERROR - ' in line:
                        stats['error_messages'].append(line.strip())
                    elif ' - WARNING - ' in line:
                        stats['warning_messages'].append(line.strip())
                        
            # 計算持續時間
            if stats['start_time'] and stats['end_time']:
                stats['duration'] = (stats['end_time'] - stats['start_time']).total_seconds()
                
            return dict(stats)
            
        except Exception as e:
            self.logger.error(f"分析日誌文件失敗: {str(e)}")
            return {}
            
    def get_log_stats(self) -> Dict[str, Any]:
        """
        獲取日誌統計信息
        
        Returns:
            統計信息
        """
        log_dir = Path(self.config.log_dir)
        if not log_dir.exists():
            return {}
            
        try:
            stats = {
                'total_size': 0,
                'file_count': 0,
                'oldest_file': None,
                'newest_file': None,
                'compressed_files': 0
            }
            
            # 獲取所有日誌文件
            log_files = list(log_dir.glob("*.log*"))
            
            for log_file in log_files:
                # 更新文件大小
                stats['total_size'] += log_file.stat().st_size
                stats['file_count'] += 1
                
                # 更新壓縮文件計數
                if log_file.suffix == '.gz':
                    stats['compressed_files'] += 1
                    
                # 更新最舊和最新文件
                mtime = datetime.fromtimestamp(log_file.stat().st_mtime)
                if stats['oldest_file'] is None or mtime < stats['oldest_file']:
                    stats['oldest_file'] = mtime
                if stats['newest_file'] is None or mtime > stats['newest_file']:
                    stats['newest_file'] = mtime
                    
            return stats
            
        except Exception as e:
            self.logger.error(f"獲取日誌統計信息失敗: {str(e)}")
            return {}
            
    def export_logs(self, output_file: str, format: str = 'json', 
                   start_time: Optional[datetime] = None,
                   end_time: Optional[datetime] = None,
                   level: Optional[str] = None) -> bool:
        """
        導出日誌
        
        Args:
            output_file: 輸出文件路徑
            format: 輸出格式（json或csv）
            start_time: 開始時間
            end_time: 結束時間
            level: 日誌等級
            
        Returns:
            是否導出成功
        """
        try:
            log_file = Path(self.config.log_dir) / self.config.log_file
            if not log_file.exists():
                return False
                
            # 讀取日誌文件
            logs = []
            with open(log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    # 解析日誌行
                    match = re.match(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) - (\w+) - (\w+) - (.+)', line)
                    if not match:
                        continue
                        
                    timestamp, name, level_name, message = match.groups()
                    log_time = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
                    
                    # 應用過濾條件
                    if start_time and log_time < start_time:
                        continue
                    if end_time and log_time > end_time:
                        continue
                    if level and level_name != level:
                        continue
                        
                    # 添加到日誌列表
                    logs.append({
                        'timestamp': timestamp,
                        'name': name,
                        'level': level_name,
                        'message': message
                    })
                    
            # 導出日誌
            output_path = Path(output_file)
            if format.lower() == 'json':
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(logs, f, indent=2, ensure_ascii=False)
            elif format.lower() == 'csv':
                with open(output_path, 'w', encoding='utf-8', newline='') as f:
                    writer = csv.DictWriter(f, fieldnames=['timestamp', 'name', 'level', 'message'])
                    writer.writeheader()
                    writer.writerows(logs)
            else:
                raise ValueError(f"不支持的輸出格式: {format}")
                
            return True
            
        except Exception as e:
            self.logger.error(f"導出日誌失敗: {str(e)}")
            return False
            
    def search_logs(self, pattern: str, 
                   start_time: Optional[datetime] = None,
                   end_time: Optional[datetime] = None,
                   level: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        搜索日誌
        
        Args:
            pattern: 搜索模式（正則表達式）
            start_time: 開始時間
            end_time: 結束時間
            level: 日誌等級
            
        Returns:
            匹配的日誌記錄列表
        """
        try:
            log_file = Path(self.config.log_dir) / self.config.log_file
            if not log_file.exists():
                return []
                
            # 編譯正則表達式
            regex = re.compile(pattern)
            
            # 搜索日誌
            matches = []
            with open(log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    # 解析日誌行
                    match = re.match(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) - (\w+) - (\w+) - (.+)', line)
                    if not match:
                        continue
                        
                    timestamp, name, level_name, message = match.groups()
                    log_time = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
                    
                    # 應用過濾條件
                    if start_time and log_time < start_time:
                        continue
                    if end_time and log_time > end_time:
                        continue
                    if level and level_name != level:
                        continue
                        
                    # 搜索匹配
                    if regex.search(line):
                        matches.append({
                            'timestamp': timestamp,
                            'name': name,
                            'level': level_name,
                            'message': message
                        })
                        
            return matches
            
        except Exception as e:
            self.logger.error(f"搜索日誌失敗: {str(e)}")
            return [] 