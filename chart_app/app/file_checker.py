#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
文件檢查工具模組。
提供檔案存在性檢查、檔案內容讀取、路徑修復等功能。
"""

import os
import json
import logging
from pathlib import Path
from typing import Tuple, List, Dict, Any, Optional

# 設置基本日誌配置
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("file_checker")

# 設定目錄路徑
BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / "static"
UPLOAD_DIR = STATIC_DIR / "uploads"
UPLOAD_CSV_DIR = UPLOAD_DIR / "csv"
UPLOAD_JSON_DIR = UPLOAD_DIR / "json"
UPLOAD_EXCEL_DIR = UPLOAD_DIR / "excel"
DATA_DIR = Path("/Users/aaron/Projects/DataScout/data")
DATA_CSV_DIR = DATA_DIR / "csv"
DATA_JSON_DIR = DATA_DIR / "json"
DATA_EXCEL_DIR = DATA_DIR / "excel"

# 確保所有目錄存在
for dir_path in [UPLOAD_DIR, UPLOAD_CSV_DIR, UPLOAD_JSON_DIR, UPLOAD_EXCEL_DIR,
                DATA_DIR, DATA_CSV_DIR, DATA_JSON_DIR, DATA_EXCEL_DIR]:
    os.makedirs(dir_path, exist_ok=True)


def fix_file_path(filename: str) -> str:
    """
    修復檔案路徑，嘗試查找正確的檔案路徑
    
    Args:
        filename (str): 原始檔案名或路徑
        
    Returns:
        str: 修復後的檔案路徑
    """
    if not filename:
        return ""
    
    # 檢查是否已包含完整路徑
    if os.path.exists(filename):
        return filename
    
    # 如果只是檔案名，嘗試在不同目錄下尋找
    file_basename = os.path.basename(filename)
    extension = os.path.splitext(file_basename)[1].lower()
    
    # 根據副檔名確定可能的目錄
    possible_dirs = []
    if extension == '.csv':
        possible_dirs = [UPLOAD_CSV_DIR, DATA_CSV_DIR]
    elif extension == '.json':
        possible_dirs = [UPLOAD_JSON_DIR, DATA_JSON_DIR]
    elif extension in ['.xlsx', '.xls']:
        possible_dirs = [UPLOAD_EXCEL_DIR, DATA_EXCEL_DIR]
    else:
        possible_dirs = [UPLOAD_DIR, DATA_DIR]
    
    # 在可能的目錄中尋找檔案
    for directory in possible_dirs:
        full_path = directory / file_basename
        if os.path.exists(full_path):
            logger.info(f"在 {directory} 中找到檔案 {file_basename}")
            return str(full_path)
    
    # 如果找不到檔案，返回原始檔名
    logger.warning(f"無法找到檔案 {filename} 的正確路徑")
    return filename


def check_file_exists(filename: str) -> Tuple[bool, str]:
    """
    檢查檔案是否存在，並返回實際路徑或錯誤訊息
    
    Args:
        filename (str): 檔案名或路徑
        
    Returns:
        Tuple[bool, str]: (存在性, 路徑或錯誤訊息)
    """
    if not filename:
        return False, "未提供檔案名"
    
    # 如果是完整路徑，直接檢查
    if os.path.exists(filename):
        return True, filename
    
    # 嘗試修復路徑
    fixed_path = fix_file_path(filename)
    
    if os.path.exists(fixed_path):
        return True, fixed_path
    
    # 如果仍找不到檔案
    return False, f"找不到檔案: {filename}"


def get_file_content(filepath: str) -> Tuple[bool, Any]:
    """
    讀取檔案內容，主要用於 JSON 檔案
    
    Args:
        filepath (str): 檔案路徑
        
    Returns:
        Tuple[bool, Any]: (成功標誌, 內容或錯誤訊息)
    """
    try:
        # 檢查檔案是否存在
        if not os.path.exists(filepath):
            return False, f"檔案不存在: {filepath}"
        
        # 檢查檔案類型
        extension = os.path.splitext(filepath)[1].lower()
        
        if extension == '.json':
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return True, data
        else:
            return False, f"不支援的檔案類型: {extension}"
    except json.JSONDecodeError as e:
        logger.error(f"JSON 解析錯誤: {e}")
        return False, f"JSON 解析錯誤: {str(e)}"
    except Exception as e:
        logger.error(f"讀取檔案內容時出錯: {e}")
        return False, f"讀取檔案時出錯: {str(e)}"


def list_uploaded_files(file_type: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    列出已上傳的檔案
    
    Args:
        file_type (str, optional): 檔案類型 ('csv', 'json', 'excel')
        
    Returns:
        List[Dict[str, Any]]: 檔案資訊列表
    """
    files = []
    
    # 決定要搜尋的目錄
    dirs_to_check = []
    if file_type == 'csv':
        dirs_to_check = [UPLOAD_CSV_DIR]
    elif file_type == 'json':
        dirs_to_check = [UPLOAD_JSON_DIR]
    elif file_type == 'excel':
        dirs_to_check = [UPLOAD_EXCEL_DIR]
    else:
        dirs_to_check = [UPLOAD_CSV_DIR, UPLOAD_JSON_DIR, UPLOAD_EXCEL_DIR]
    
    # 遍歷目錄
    for directory in dirs_to_check:
        if os.path.exists(directory):
            for file in os.listdir(directory):
                file_path = os.path.join(directory, file)
                if os.path.isfile(file_path):
                    # 決定檔案類型
                    ext = os.path.splitext(file)[1].lower()
                    detected_type = ""
                    
                    if ext == '.csv':
                        detected_type = 'csv'
                    elif ext == '.json':
                        detected_type = 'json'
                    elif ext in ['.xlsx', '.xls']:
                        detected_type = 'excel'
                    
                    # 只有在沒有指定類型或類型匹配時添加
                    if not file_type or detected_type == file_type:
                        files.append({
                            "filename": file,
                            "path": str(file_path),
                            "type": detected_type,
                            "size": os.path.getsize(file_path)
                        })
    
    return files


if __name__ == "__main__":
    # 測試代碼
    print("文件檢查器測試")
    
    # 確保目錄存在
    for dir_path in [UPLOAD_CSV_DIR, UPLOAD_JSON_DIR, UPLOAD_EXCEL_DIR]:
        os.makedirs(dir_path, exist_ok=True)
        
    print("已上傳的檔案:")
    uploaded_files = list_uploaded_files()
    for file_info in uploaded_files:
        print(f"- {file_info['filename']} ({file_info['type']})")
