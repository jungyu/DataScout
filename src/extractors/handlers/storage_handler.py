#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
數據存儲處理模組

提供多種格式的數據存儲、轉換和管理功能，支持本地文件和數據庫存儲。
"""

import os
import json
import time
import logging
import gzip
import pickle
import shutil
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, Callable, BinaryIO, Set, Tuple
import threading
import tempfile
import uuid

# 嘗試導入可選依賴
try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

try:
    import sqlite3
    SQLITE_AVAILABLE = True
except ImportError:
    SQLITE_AVAILABLE = False

try:
    import boto3
    from botocore.exceptions import ClientError
    AWS_AVAILABLE = True
except ImportError:
    AWS_AVAILABLE = False

from src.extractors.exceptions import StorageError


class StorageFormat:
    """存儲格式常量"""
    JSON = "json"
    CSV = "csv"
    EXCEL = "xlsx"
    PICKLE = "pkl"
    SQLITE = "db"
    TEXT = "txt"
    HTML = "html"
    JSONL = "jsonl"  # 每行一個JSON對象


class StorageHandler:
    """
    數據存儲處理器，支持多種存儲格式和目標
    
    支持本地文件存儲、數據庫存儲、雲存儲以及數據格式轉換
    """
    
    def __init__(
        self,
        base_dir: str = "output",
        logger: Optional[logging.Logger] = None,
        compress: bool = False,
        auto_backup: bool = False,
        max_file_size: int = 100 * 1024 * 1024,  # 100MB
        date_format: str = "%Y%m%d_%H%M%S"
    ):
        """
        初始化存儲處理器
        
        Args:
            base_dir: 基本存儲目錄
            logger: 日誌記錄器
            compress: 是否壓縮存儲文件
            auto_backup: 是否自動備份
            max_file_size: 單個文件的最大尺寸（字節）
            date_format: 日期格式化字符串
        """
        self.base_dir = base_dir
        self.logger = logger or logging.getLogger(__name__)
        self.compress = compress
        self.auto_backup = auto_backup
        self.max_file_size = max_file_size
        self.date_format = date_format
        
        # 文件鎖，用於並發寫入保護
        self.file_locks = {}
        
        # 檢查並創建基礎目錄
        os.makedirs(self.base_dir, exist_ok=True)
        
        # 統計數據
        self.saved_files_count = 0
        self.saved_records_count = 0
        self.total_bytes_written = 0
        self.failed_operations_count = 0
        
        # 數據庫連接池
        self.db_connections = {}
        
        # 已存儲文件的哈希集合（避免重複存儲）
        self.file_hashes: Set[str] = set()
        
        self.logger.info(f"存儲處理器初始化完成，基礎目錄: {self.base_dir}")
    
    def save_data(
        self, 
        data: Union[Dict[str, Any], List[Dict[str, Any]]],
        filepath: Optional[str] = None,
        subdirectory: str = "",
        prefix: str = "data",
        format: str = StorageFormat.JSON,
        pretty: bool = True,
        metadata: Optional[Dict[str, Any]] = None,
        overwrite: bool = True,
        encoding: str = "utf-8",
        **kwargs
    ) -> str:
        """
        保存數據到文件
        
        Args:
            data: 要保存的數據（字典或字典列表）
            filepath: 完整文件路徑（如果指定則忽略其他路徑相關參數）
            subdirectory: 子目錄名
            prefix: 文件名前綴
            format: 存儲格式
            pretty: 是否格式化JSON輸出
            metadata: 要添加的元數據
            overwrite: 是否覆蓋現有文件
            encoding: 文件編碼
            **kwargs: 其他格式特定的參數
            
        Returns:
            保存的文件路徑
            
        Raises:
            StorageError: 保存失敗時拋出
        """
        try:
            # 檢查數據是否為空
            if data is None:
                self.logger.warning("沒有數據需要保存")
                return ""
            
            # 確保數據是列表形式（方便處理）
            data_list = data if isinstance(data, list) else [data]
            if not data_list:
                self.logger.warning("空列表數據，無需保存")
                return ""
            
            # 添加元數據
            if metadata:
                for item in data_list:
                    if isinstance(item, dict):
                        if "_metadata" not in item:
                            item["_metadata"] = {}
                        item["_metadata"].update(metadata)
            
            # 確定文件路徑
            if not filepath:
                # 構建目標目錄
                target_dir = self.base_dir
                if subdirectory:
                    target_dir = os.path.join(target_dir, subdirectory)
                
                os.makedirs(target_dir, exist_ok=True)
                
                # 生成文件名
                timestamp = datetime.now().strftime(self.date_format)
                filename = f"{prefix}_{timestamp}.{format}"
                filepath = os.path.join(target_dir, filename)
            else:
                # 確保目標目錄存在
                os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
            
            # 檢查文件是否存在（是否覆蓋）
            if os.path.exists(filepath) and not overwrite:
                self.logger.warning(f"文件已存在且未設置覆蓋: {filepath}")
                return self._handle_existing_file(filepath, data_list, format, pretty, encoding, **kwargs)
            
            # 根據格式保存數據
            self._save_by_format(filepath, data_list, format, pretty, encoding, **kwargs)
            
            # 保存成功後進行後續處理
            self.saved_files_count += 1
            self.saved_records_count += len(data_list)
            
            if os.path.exists(filepath):
                file_size = os.path.getsize(filepath)
                self.total_bytes_written += file_size
                
                # 計算文件哈希值（用於去重）
                file_hash = self._get_file_hash(filepath)
                self.file_hashes.add(file_hash)
                
                # 自動備份
                if self.auto_backup:
                    self._backup_file(filepath)
            
            self.logger.info(f"數據已保存到: {filepath}")
            return filepath
            
        except Exception as e:
            self.failed_operations_count += 1
            error_msg = f"保存數據失敗: {str(e)}"
            self.logger.error(error_msg)
            raise StorageError(message=error_msg, filepath=filepath)
    
    def _save_by_format(
        self, 
        filepath: str, 
        data_list: List[Dict[str, Any]],
        format: str, 
        pretty: bool, 
        encoding: str,
        **kwargs
    ) -> None:
        """
        根據格式保存數據
        
        Args:
            filepath: 文件路徑
            data_list: 數據列表
            format: 存儲格式
            pretty: 是否格式化輸出
            encoding: 文件編碼
        """
        # 獲取文件鎖或創建新鎖
        if filepath not in self.file_locks:
            self.file_locks[filepath] = threading.Lock()
        
        # 使用鎖保護文件寫入操作
        with self.file_locks[filepath]:
            # 檢查是否需要壓縮
            compress_file = self.compress and not filepath.endswith('.gz')
            output_path = f"{filepath}.gz" if compress_file else filepath
            
            # 根據格式選擇不同的保存方法
            if format == StorageFormat.JSON:
                self._save_json(output_path, data_list, pretty, encoding, compress_file)
            
            elif format == StorageFormat.JSONL:
                self._save_jsonl(output_path, data_list, encoding, compress_file)
            
            elif format == StorageFormat.CSV:
                self._save_csv(output_path, data_list, encoding, compress_file, **kwargs)
            
            elif format == StorageFormat.EXCEL:
                self._save_excel(output_path, data_list, **kwargs)
            
            elif format == StorageFormat.PICKLE:
                self._save_pickle(output_path, data_list, compress_file)
            
            elif format == StorageFormat.SQLITE:
                self._save_sqlite(output_path, data_list, **kwargs)
            
            elif format == StorageFormat.TEXT:
                self._save_text(output_path, data_list, encoding, compress_file, **kwargs)
            
            elif format == StorageFormat.HTML:
                self._save_html(output_path, data_list, encoding, compress_file, **kwargs)
            
            else:
                raise ValueError(f"不支持的存儲格式: {format}")
    
    def _save_json(
        self, 
        filepath: str, 
        data_list: List[Dict[str, Any]], 
        pretty: bool, 
        encoding: str,
        compress: bool
    ) -> None:
        """保存為JSON格式"""
        indent = 2 if pretty else None
        
        try:
            if compress:
                with gzip.open(filepath, 'wt', encoding=encoding) as f:
                    json.dump(data_list if len(data_list) > 1 else data_list[0], f, ensure_ascii=False, indent=indent)
            else:
                with open(filepath, 'w', encoding=encoding) as f:
                    json.dump(data_list if len(data_list) > 1 else data_list[0], f, ensure_ascii=False, indent=indent)
        except Exception as e:
            raise StorageError(f"保存JSON文件失敗: {str(e)}", filepath=filepath)
    
    def _save_jsonl(
        self, 
        filepath: str, 
        data_list: List[Dict[str, Any]], 
        encoding: str,
        compress: bool
    ) -> None:
        """保存為JSONL格式（每行一個JSON對象）"""
        try:
            if compress:
                with gzip.open(filepath, 'wt', encoding=encoding) as f:
                    for item in data_list:
                        f.write(json.dumps(item, ensure_ascii=False) + '\n')
            else:
                with open(filepath, 'w', encoding=encoding) as f:
                    for item in data_list:
                        f.write(json.dumps(item, ensure_ascii=False) + '\n')
        except Exception as e:
            raise StorageError(f"保存JSONL文件失敗: {str(e)}", filepath=filepath)
    
    def _save_csv(
        self, 
        filepath: str, 
        data_list: List[Dict[str, Any]], 
        encoding: str,
        compress: bool,
        **kwargs
    ) -> None:
        """保存為CSV格式"""
        if not PANDAS_AVAILABLE:
            try:
                import csv
                
                # 先將嵌套字典拍平
                flat_data = []
                for item in data_list:
                    flat_item = self.flatten_dict(item)
                    flat_data.append(flat_item)
                
                # 整理所有字段
                all_fields = set()
                for item in flat_data:
                    all_fields.update(item.keys())
                
                # 寫入CSV
                if compress:
                    with gzip.open(filepath, 'wt', encoding=encoding, newline='') as f:
                        writer = csv.DictWriter(f, fieldnames=sorted(all_fields))
                        writer.writeheader()
                        writer.writerows(flat_data)
                else:
                    with open(filepath, 'w', encoding=encoding, newline='') as f:
                        writer = csv.DictWriter(f, fieldnames=sorted(all_fields))
                        writer.writeheader()
                        writer.writerows(flat_data)
            except Exception as e:
                raise StorageError(f"保存CSV文件失敗: {str(e)}", filepath=filepath)
        else:
            try:
                # 使用pandas保存CSV
                flat_data = [self.flatten_dict(item) for item in data_list]
                df = pd.DataFrame(flat_data)
                
                if compress:
                    df.to_csv(filepath, index=False, encoding=encoding, compression='gzip', **kwargs)
                else:
                    df.to_csv(filepath, index=False, encoding=encoding, **kwargs)
            except Exception as e:
                raise StorageError(f"使用pandas保存CSV文件失敗: {str(e)}", filepath=filepath)
    
    def _save_excel(
        self, 
        filepath: str, 
        data_list: List[Dict[str, Any]], 
        **kwargs
    ) -> None:
        """保存為Excel格式"""
        if not PANDAS_AVAILABLE:
            raise StorageError("保存Excel文件需要安裝pandas庫", filepath=filepath)
        
        try:
            # 拍平數據
            flat_data = [self.flatten_dict(item) for item in data_list]
            df = pd.DataFrame(flat_data)
            
            # 保存為Excel
            sheet_name = kwargs.get('sheet_name', 'Sheet1')
            df.to_excel(filepath, sheet_name=sheet_name, index=False, **kwargs)
        except Exception as e:
            raise StorageError(f"保存Excel文件失敗: {str(e)}", filepath=filepath)
    
    def _save_pickle(
        self, 
        filepath: str, 
        data_list: List[Dict[str, Any]], 
        compress: bool
    ) -> None:
        """保存為Pickle格式"""
        try:
            if compress:
                with gzip.open(filepath, 'wb') as f:
                    pickle.dump(data_list, f)
            else:
                with open(filepath, 'wb') as f:
                    pickle.dump(data_list, f)
        except Exception as e:
            raise StorageError(f"保存Pickle文件失敗: {str(e)}", filepath=filepath)
    
    def _save_sqlite(
        self, 
        filepath: str, 
        data_list: List[Dict[str, Any]], 
        **kwargs
    ) -> None:
        """保存到SQLite數據庫"""
        if not SQLITE_AVAILABLE:
            raise StorageError("SQLite功能不可用", filepath=filepath)
        
        table_name = kwargs.get('table_name', 'data')
        if_exists = kwargs.get('if_exists', 'replace')  # 'replace', 'append', 'fail'
        
        try:
            # 獲取或創建數據庫連接
            if filepath not in self.db_connections:
                self.db_connections[filepath] = sqlite3.connect(filepath)
            
            conn = self.db_connections[filepath]
            
            # 使用pandas將數據轉換成SQL（如果可用）
            if PANDAS_AVAILABLE:
                flat_data = [self.flatten_dict(item) for item in data_list]
                df = pd.DataFrame(flat_data)
                df.to_sql(table_name, conn, if_exists=if_exists, index=False)
            else:
                # 手動使用SQLite API
                flat_data = [self.flatten_dict(item) for item in data_list]
                
                if not flat_data:
                    return
                
                cursor = conn.cursor()
                
                # 檢查表是否存在
                cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
                table_exists = cursor.fetchone() is not None
                
                # 如果表不存在或需要替換，創建新表
                if not table_exists or if_exists == 'replace':
                    if table_exists and if_exists == 'replace':
                        cursor.execute(f"DROP TABLE {table_name}")
                        conn.commit()
                    
                    # 從第一行數據創建表結構
                    columns = list(flat_data[0].keys())
                    columns_str = ', '.join([f'"{column}" TEXT' for column in columns])
                    cursor.execute(f"CREATE TABLE {table_name} ({columns_str})")
                
                # 插入數據
                for item in flat_data:
                    columns = list(item.keys())
                    placeholders = ', '.join(['?'] * len(columns))
                    columns_str = ', '.join([f'"{column}"' for column in columns])
                    
                    query = f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})"
                    values = [str(item.get(column, '')) for column in columns]
                    
                    cursor.execute(query, values)
                
                conn.commit()
                
        except Exception as e:
            raise StorageError(f"保存SQLite數據失敗: {str(e)}", filepath=filepath)
    
    def _save_text(
        self, 
        filepath: str, 
        data_list: List[Dict[str, Any]], 
        encoding: str,
        compress: bool,
        **kwargs
    ) -> None:
        """保存為純文本格式"""
        separator = kwargs.get('separator', '\n\n')
        include_keys = kwargs.get('include_keys', True)
        
        try:
            # 將字典轉換為文本
            text_items = []
            for item in data_list:
                if include_keys:
                    lines = []
                    for key, value in self.flatten_dict(item).items():
                        lines.append(f"{key}: {value}")
                    text_items.append('\n'.join(lines))
                else:
                    text_items.append(str(item))
                    
            text_content = separator.join(text_items)
                
            # 保存文本
            if compress:
                with gzip.open(filepath, 'wt', encoding=encoding) as f:
                    f.write(text_content)
            else:
                with open(filepath, 'w', encoding=encoding) as f:
                    f.write(text_content)
        except Exception as e:
            raise StorageError(f"保存文本文件失敗: {str(e)}", filepath=filepath)
    
    def _save_html(
        self, 
        filepath: str, 
        data_list: List[Dict[str, Any]], 
        encoding: str,
        compress: bool,
        **kwargs
    ) -> None:
        """保存為HTML格式"""
        template = kwargs.get('template', '')
        title = kwargs.get('title', 'Data Report')
        
        try:
            # 如果沒有提供模板，使用默認模板
            if not template:
                template = """
                <!DOCTYPE html>
                <html>
                <head>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <title>{title}</title>
                    <style>
                        body {{ font-family: Arial, sans-serif; margin: 20px; }}
                        table {{ border-collapse: collapse; width: 100%; }}
                        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                        th {{ background-color: #f2f2f2; }}
                        tr:nth-child(even) {{ background-color: #f9f9f9; }}
                        h1 {{ color: #333; }}
                        .timestamp {{ color: gray; font-size: 0.8em; margin-bottom: 20px; }}
                        .container {{ margin-bottom: 30px; }}
                    </style>
                </head>
                <body>
                    <h1>{title}</h1>
                    <div class="timestamp">生成時間: {timestamp}</div>
                    {content}
                </body>
                </html>
                """
            
            # 生成HTML內容
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            content_parts = []
            
            # 將數據轉換為HTML表格
            for i, item in enumerate(data_list):
                flat_item = self.flatten_dict(item)
                
                table_html = '<div class="container">\n<table>\n'
                
                # 添加標題（如果有）
                if "_metadata" in item and "title" in item["_metadata"]:
                    table_html += f'<caption>{item["_metadata"]["title"]}</caption>\n'
                elif i > 0:
                    table_html += f'<caption>Item #{i+1}</caption>\n'
                
                # 添加表格內容
                for key, value in flat_item.items():
                    table_html += f"<tr><th>{key}</th><td>{value}</td></tr>\n"
                
                table_html += '</table>\n</div>'
                content_parts.append(table_html)
            
            # 組合最終HTML
            html_content = template.format(
                title=title,
                timestamp=timestamp,
                content='\n'.join(content_parts)
            )
            
            # 保存HTML
            if compress:
                with gzip.open(filepath, 'wt', encoding=encoding) as f:
                    f.write(html_content)
            else:
                with open(filepath, 'w', encoding=encoding) as f:
                    f.write(html_content)
                    
        except Exception as e:
            raise StorageError(f"保存HTML文件失敗: {str(e)}", filepath=filepath)
    
    def _handle_existing_file(
        self, 
        filepath: str, 
        data_list: List[Dict[str, Any]],
        format: str, 
        pretty: bool, 
        encoding: str,
        **kwargs
    ) -> str:
        """
        處理已存在文件的情況
        
        Args:
            filepath: 已存在的文件路徑
            data_list: 要保存的數據
            format: 文件格式
            pretty: 是否美化輸出
            encoding: 文件編碼
            
        Returns:
            新的文件路徑
        """
        # 生成新文件名
        filename = os.path.basename(filepath)
        name, ext = os.path.splitext(filename)
        
        # 添加數字後綴
        counter = 1
        while True:
            new_filename = f"{name}_{counter}{ext}"
            new_filepath = os.path.join(os.path.dirname(filepath), new_filename)
            
            if not os.path.exists(new_filepath):
                break
                
            counter += 1
        
        # 保存到新文件
        self._save_by_format(new_filepath, data_list, format, pretty, encoding, **kwargs)
        return new_filepath
    
    def _backup_file(self, filepath: str) -> str:
        """
        備份文件
        
        Args:
            filepath: 需要備份的文件路徑
            
        Returns:
            備份文件路徑
        """
        try:
            # 創建備份目錄
            backup_dir = os.path.join(self.base_dir, "backups")
            os.makedirs(backup_dir, exist_ok=True)
            
            # 生成備份文件名
            filename = os.path.basename(filepath)
            timestamp = datetime.now().strftime(self.date_format)
            backup_filename = f"{filename}.{timestamp}.bak"
            backup_filepath = os.path.join(backup_dir, backup_filename)
            
            # 複製文件
            shutil.copy2(filepath, backup_filepath)
            self.logger.debug(f"已創建文件備份: {backup_filepath}")
            
            return backup_filepath
            
        except Exception as e:
            self.logger.warning(f"創建文件備份失敗: {str(e)}")
            return ""
    
    def _get_file_hash(self, filepath: str) -> str:
        """
        計算文件的哈希值
        
        Args:
            filepath: 文件路徑
            
        Returns:
            文件的MD5哈希值
        """
        try:
            hasher = hashlib.md5()
            with open(filepath, 'rb') as f:
                # 讀取文件前8KB用於計算哈希
                chunk = f.read(8192)
                hasher.update(chunk)
            return hasher.hexdigest()
        except Exception as e:
            self.logger.debug(f"計算文件哈希失敗: {str(e)}")
            return ""
    
    def append_to_file(
        self, 
        data: Union[Dict[str, Any], List[Dict[str, Any]]],
        filepath: str,
        format: str = StorageFormat.JSONL,
        encoding: str = "utf-8"
    ) -> bool:
        """
        向已有文件追加數據
        
        Args:
            data: 要追加的數據
            filepath: 目標文件路徑
            format: 文件格式
            encoding: 文件編碼
            
        Returns:
            是否成功追加
        """
        if not os.path.exists(filepath):
            self.logger.warning(f"目標文件不存在: {filepath}")
            return self.save_data(data, filepath, format=format, encoding=encoding) != ""
        
        # 確保數據是列表形式
        data_list = data if isinstance(data, list) else [data]
        if not data_list:
            return True
        
        try:
            # 獲取文件鎖
            if filepath not in self.file_locks:
                self.file_locks[filepath] = threading.Lock()
                
            with self.file_locks[filepath]:
                if format == StorageFormat.JSONL:
                    # JSONL格式 - 每行一個JSON對象，直接追加
                    with open(filepath, 'a', encoding=encoding) as f:
                        for item in data_list:
                            f.write(json.dumps(item, ensure_ascii=False) + '\n')
                
                elif format == StorageFormat.JSON:
                    # JSON格式 - 需要先讀取原內容，合併後重新寫入
                    with open(filepath, 'r', encoding=encoding) as f:
                        try:
                            existing_data = json.load(f)
                            
                            # 確保現有數據是列表
                            if not isinstance(existing_data, list):
                                existing_data = [existing_data]
                                
                            # 合併數據
                            existing_data.extend(data_list)
                            
                            # 重新寫入
                            with open(filepath, 'w', encoding=encoding) as f_write:
                                json.dump(existing_data, f_write, ensure_ascii=False, indent=2)
                                
                        except json.JSONDecodeError:
                            self.logger.error(f"讀取JSON文件失敗: {filepath}")
                            return False
                
                elif format == StorageFormat.CSV:
                    if PANDAS_AVAILABLE:
                        # 使用pandas追加CSV數據
                        flat_data = [self.flatten_dict(item) for item in data_list]
                        df = pd.DataFrame(flat_data)
                        df.to_csv(filepath, mode='a', header=False, index=False, encoding=encoding)
                    else:
                        # 手動追加CSV數據
                        import csv
                        flat_data = [self.flatten_dict(item) for item in data_list]
                        with open(filepath, 'a', newline='', encoding=encoding) as f:
                            writer = csv.DictWriter(f, fieldnames=list(flat_data[0].keys()))
                            writer.writerows(flat_data)
                
                elif format == StorageFormat.SQLITE:
                    # 追加到SQLite
                    self._save_sqlite(filepath, data_list, if_exists='append', table_name='data')
                
                else:
                    self.logger.warning(f"不支持向{format}格式文件追加數據")
                    return False
                
                # 更新統計
                self.saved_records_count += len(data_list)
                
                return True
                
        except Exception as e:
            self.failed_operations_count += 1
            self.logger.error(f"追加數據失敗: {str(e)}")
            return False
    
    def save_in_chunks(
        self,
        data: List[Dict[str, Any]],
        base_path: str,
        chunk_size: int = 1000,
        format: str = StorageFormat.JSON,
        prefix: str = "data_chunk",
        **kwargs
    ) -> List[str]:
        """
        分塊保存大數據集
        
        Args:
            data: 數據列表
            base_path: 基本路徑
            chunk_size: 每個塊的最大記錄數
            format: 存儲格式
            prefix: 文件名前綴
            
        Returns:
            保存的文件路徑列表
        """
        if not data:
            return []
            
        if not isinstance(data, list):
            data = [data]
            
        file_paths = []
        
        try:
            # 計算需要多少塊
            total_records = len(data)
            total_chunks = (total_records + chunk_size - 1) // chunk_size  # 向上取整
            
            # 確保目標目錄存在
            target_dir = os.path.dirname(base_path)
            os.makedirs(target_dir, exist_ok=True)
            
            # 分塊保存
            for i in range(total_chunks):
                chunk_start = i * chunk_size
                chunk_end = min((i + 1) * chunk_size, total_records)
                chunk_data = data[chunk_start:chunk_end]
                
                # 生成分塊文件名
                filename = os.path.basename(base_path)
                name, ext = os.path.splitext(filename)
                chunk_filename = f"{prefix}_{i+1}_of_{total_chunks}{ext}"
                chunk_filepath = os.path.join(target_dir, chunk_filename)
                
                # 保存當前塊
                saved_path = self.save_data(
                    chunk_data, 
                    filepath=chunk_filepath, 
                    format=format, 
                    **kwargs
                )
                
                if saved_path:
                    file_paths.append(saved_path)
            
            # 如果所有塊都成功保存，還可以創建一個索引文件
            if len(file_paths) == total_chunks:
                index_data = {
                    "total_chunks": total_chunks,
                    "total_records": total_records,
                    "chunk_size": chunk_size,
                    "format": format,
                    "files": file_paths,
                    "created_at": datetime.now().isoformat()
                }
                
                index_filepath = os.path.join(target_dir, f"{prefix}_index.json")
                with open(index_filepath, 'w', encoding='utf-8') as f:
                    json.dump(index_data, f, ensure_ascii=False, indent=2)
                
                file_paths.append(index_filepath)
            
            return file_paths
            
        except Exception as e:
            self.failed_operations_count += 1
            self.logger.error(f"分塊保存數據失敗: {str(e)}")
            return file_paths
    
    def merge_files(
        self,
        file_paths: List[str],
        output_path: str,
        format: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        合併多個數據文件
        
        Args:
            file_paths: 要合併的文件路徑列表
            output_path: 輸出文件路徑
            format: 輸出格式（如未指定則從輸出路徑推斷）
            
        Returns:
            合併後的文件路徑
        """
        if not file_paths:
            return ""
            
        # 如果未指定格式，從輸出路徑推斷
        if not format:
            _, ext = os.path.splitext(output_path)
            format = ext[1:] if ext.startswith('.') else ext
            
        try:
            # 讀取所有文件數據
            all_data = []
            
            for filepath in file_paths:
                if not os.path.exists(filepath):
                    self.logger.warning(f"文件不存在: {filepath}")
                    continue
                    
                _, ext = os.path.splitext(filepath)
                file_format = ext[1:] if ext.startswith('.') else ext
                
                # 根據文件格式讀取數據
                data = self.load_data(filepath, file_format)
                if isinstance(data, list):
                    all_data.extend(data)
                else:
                    all_data.append(data)
            
            # 保存合併後的數據
            if all_data:
                return self.save_data(all_data, filepath=output_path, format=format, **kwargs)
            else:
                self.logger.warning("沒有數據需要合併")
                return ""
                
        except Exception as e:
            self.failed_operations_count += 1
            self.logger.error(f"合併文件失敗: {str(e)}")
            return ""
    
    def load_data(
        self, 
        filepath: str, 
        format: Optional[str] = None
    ) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        """
        從文件載入數據
        
        Args:
            filepath: 文件路徑
            format: 文件格式
            
        Returns:
            載入的數據
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"文件不存在: {filepath}")
            
        # 如果未指定格式，從文件路徑推斷
        if not format:
            _, ext = os.path.splitext(filepath)
            format = ext[1:] if ext.startswith('.') else ext
            
        # 檢查是否是壓縮文件
        is_compressed = filepath.endswith('.gz')
        
        try:
            # 根據格式載入數據
            if format in ['json', 'jsonl']:
                # 檢查是否是壓縮的JSON
                if is_compressed:
                    with gzip.open(filepath, 'rt', encoding='utf-8') as f:
                        if format == 'jsonl':
                            return [json.loads(line) for line in f if line.strip()]
                        else:
                            return json.load(f)
                else:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        if format == 'jsonl':
                            return [json.loads(line) for line in f if line.strip()]
                        else:
                            return json.load(f)
                            
            elif format in ['csv']:
                if PANDAS_AVAILABLE:
                    compression = 'gzip' if is_compressed else None
                    df = pd.read_csv(filepath, compression=compression)
                    return df.to_dict(orient='records')
                else:
                    import csv
                    result = []
                    if is_compressed:
                        with gzip.open(filepath, 'rt', encoding='utf-8', newline='') as f:
                            reader = csv.DictReader(f)
                            result = list(reader)
                    else:
                        with open(filepath, 'r', encoding='utf-8', newline='') as f:
                            reader = csv.DictReader(f)
                            result = list(reader)
                    return result
                    
            elif format in ['xlsx', 'xls']:
                if PANDAS_AVAILABLE:
                    df = pd.read_excel(filepath)
                    return df.to_dict(orient='records')
                else:
                    raise ValueError("需要pandas庫來讀取Excel文件")
                    
            elif format in ['pkl', 'pickle']:
                if is_compressed:
                    with gzip.open(filepath, 'rb') as f:
                        return pickle.load(f)
                else:
                    with open(filepath, 'rb') as f:
                        return pickle.load(f)
                        
            elif format in ['db', 'sqlite', 'sqlite3']:
                if SQLITE_AVAILABLE:
                    # 加載SQLite數據
                    conn = sqlite3.connect(filepath)
                    cursor = conn.cursor()
                    
                    # 獲取所有表
                    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                    tables = cursor.fetchall()
                    
                    result = {}
                    for table_name in tables:
                        table_name = table_name[0]
                        cursor.execute(f"SELECT * FROM {table_name}")
                        
                        # 獲取列名
                        columns = [column[0] for column in cursor.description]
                        
                        # 構建字典列表
                        rows = cursor.fetchall()
                        table_data = []
                        for row in rows:
                            table_data.append(dict(zip(columns, row)))
                            
                        result[table_name] = table_data
                        
                    return result
                else:
                    raise ValueError("需要sqlite3庫來讀取SQLite文件")
            else:
                raise ValueError(f"不支持的文件格式: {format}")
                
        except Exception as e:
            self.logger.error(f"載入數據失敗: {str(e)}")
            raise
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        獲取存儲統計數據
        
        Returns:
            包含存儲統計的字典
        """
        return {
            "saved_files_count": self.saved_files_count,
            "saved_records_count": self.saved_records_count,
            "total_bytes_written": self.total_bytes_written,
            "failed_operations_count": self.failed_operations_count,
            "unique_files_count": len(self.file_hashes),
            "database_connections": len(self.db_connections)
        }
    
    def reset_statistics(self) -> None:
        """重置統計計數"""
        self.saved_files_count = 0
        self.saved_records_count = 0
        self.total_bytes_written = 0
        self.failed_operations_count = 0
    
    def close_connections(self) -> None:
        """關閉所有數據庫連接"""
        for filepath, conn in self.db_connections.items():
            try:
                conn.close()
                self.logger.debug(f"關閉數據庫連接: {filepath}")
            except Exception as e:
                self.logger.warning(f"關閉數據庫連接失敗: {filepath}, 錯誤: {str(e)}")
                
        self.db_connections = {}
    
    def cleanup_temp_files(self) -> int:
        """
        清理臨時文件
        
        Returns:
            清理的文件數
        """
        try:
            temp_dir = os.path.join(self.base_dir, "temp")
            if not os.path.exists(temp_dir):
                return 0
                
            count = 0
            for filename in os.listdir(temp_dir):
                filepath = os.path.join(temp_dir, filename)
                try:
                    if os.path.isfile(filepath):
                        os.remove(filepath)
                        count += 1
                except Exception as e:
                    self.logger.warning(f"刪除臨時文件失敗: {filepath}, 錯誤: {str(e)}")
                    
            return count
            
        except Exception as e:
            self.logger.error(f"清理臨時文件失敗: {str(e)}")
            return 0
    
    def upload_to_s3(
        self, 
        filepath: str, 
        bucket: str, 
        object_key: Optional[str] = None,
        credentials: Optional[Dict[str, str]] = None,
        public_read: bool = False,
        metadata: Optional[Dict[str, str]] = None
    ) -> bool:
        """
        上傳文件到S3
        
        Args:
            filepath: 本地文件路徑
            bucket: S3存儲桶名
            object_key: S3對象鍵（如未指定則使用文件名）
            credentials: AWS認證信息
            public_read: 是否設置為公開可讀
            metadata: 文件元數據
            
        Returns:
            是否上傳成功
        """
        if not AWS_AVAILABLE:
            self.logger.error("無法上傳到S3，缺少boto3庫")
            return False
            
        if not os.path.exists(filepath):
            self.logger.error(f"要上傳的文件不存在: {filepath}")
            return False
            
        # 如果未指定對象鍵，使用文件名
        if not object_key:
            object_key = os.path.basename(filepath)
            
        try:
            # 建立S3客戶端
            if credentials:
                s3_client = boto3.client(
                    's3',
                    aws_access_key_id=credentials.get('access_key'),
                    aws_secret_access_key=credentials.get('secret_key'),
                    region_name=credentials.get('region', 'us-east-1')
                )
            else:
                # 使用默認憑證
                s3_client = boto3.client('s3')
                
            # 設置上傳參數
            upload_args = {}
            if metadata:
                upload_args['Metadata'] = metadata
                
            if public_read:
                upload_args['ACL'] = 'public-read'
            
            # 上傳文件
            s3_client.upload_file(
                filepath,
                bucket,
                object_key,
                ExtraArgs=upload_args
            )
            
            self.logger.info(f"文件已上傳到S3: s3://{bucket}/{object_key}")
            return True
            
        except Exception as e:
            self.logger.error(f"上傳文件到S3失敗: {str(e)}")
            return False
    
    @staticmethod
    def flatten_dict(d: Dict[str, Any], parent_key: str = '', sep: str = '.') -> Dict[str, Any]:
        """
        將嵌套字典拍平為單層字典
        
        Args:
            d: 嵌套字典
            parent_key: 父鍵前綴
            sep: 鍵分隔符
            
        Returns:
            拍平後的字典
        """
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            
            if isinstance(v, dict):
                items.extend(StorageHandler.flatten_dict(v, new_key, sep).items())
            elif isinstance(v, list):
                # 處理列表：將列表項合併為字符串或拍平嵌套字典
                if v and isinstance(v[0], dict):
                    # 嵌套字典列表處理
                    for i, item in enumerate(v):
                        list_key = f"{new_key}{sep}{i}"
                        items.extend(StorageHandler.flatten_dict(item, list_key, sep).items())
                else:
                    # 簡單列表轉為字符串
                    items.append((new_key, str(v)))
            else:
                items.append((new_key, v))
        return dict(items)


# 便捷函數
def save_to_file(
    data: Union[Dict[str, Any], List[Dict[str, Any]]],
    filepath: Optional[str] = None,
    format: str = StorageFormat.JSON,
    **kwargs
) -> str:
    """
    快速保存數據到文件的便捷函數
    
    Args:
        data: 要保存的數據
        filepath: 文件路徑
        format: 文件格式
        **kwargs: 其他參數
        
    Returns:
        保存的文件路徑
    """
    storage = StorageHandler()
    return storage.save_data(data, filepath, format=format, **kwargs)


def load_from_file(
    filepath: str, 
    format: Optional[str] = None
) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
    """
    從文件載入數據的便捷函數
    
    Args:
        filepath: 文件路徑
        format: 文件格式（如未指定則從文件後綴推斷）
        
    Returns:
        載入的數據
    """
    storage = StorageHandler()
    return storage.load_data(filepath, format)