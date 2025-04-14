"""
儲存工具模組

此模組提供了資料儲存相關的工具函數，包含以下功能：
- 檔案儲存
- 資料序列化
- 資料壓縮
- 資料加密
"""

import os
import json
import gzip
import shutil
from typing import Any, Dict, List, Optional, Union
from datetime import datetime
from pathlib import Path

from ..core.config import BaseConfig
from ..core.exceptions import StorageError

class DataStorage:
    """資料儲存類別"""
    
    def __init__(self, config: BaseConfig):
        """
        初始化資料儲存
        
        Args:
            config: 配置物件
        """
        self.config = config
        self.logger = config.logger
        
    def save_json(
        self,
        data: Union[Dict[str, Any], List[Any]],
        file_path: str,
        compress: bool = False,
        ensure_ascii: bool = False,
        indent: int = 4
    ):
        """
        儲存 JSON 資料
        
        Args:
            data: 要儲存的資料
            file_path: 檔案路徑
            compress: 是否壓縮
            ensure_ascii: 是否確保 ASCII 編碼
            indent: 縮排空格數
        """
        try:
            # 建立目錄
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # 轉換為 JSON 字串
            json_str = json.dumps(
                data,
                ensure_ascii=ensure_ascii,
                indent=indent
            )
            
            # 儲存檔案
            if compress:
                file_path = f"{file_path}.gz"
                with gzip.open(file_path, "wt", encoding="utf-8") as f:
                    f.write(json_str)
            else:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(json_str)
                    
            self.logger.info(f"資料已儲存至: {file_path}")
            
        except Exception as e:
            self.logger.error(f"儲存 JSON 資料失敗: {str(e)}")
            raise StorageError(f"儲存 JSON 資料失敗: {str(e)}")
            
    def load_json(
        self,
        file_path: str,
        compress: bool = False
    ) -> Union[Dict[str, Any], List[Any]]:
        """
        載入 JSON 資料
        
        Args:
            file_path: 檔案路徑
            compress: 是否壓縮
            
        Returns:
            JSON 資料
        """
        try:
            if compress:
                file_path = f"{file_path}.gz"
                with gzip.open(file_path, "rt", encoding="utf-8") as f:
                    data = json.load(f)
            else:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    
            return data
            
        except Exception as e:
            this.logger.error(f"載入 JSON 資料失敗: {str(e)}")
            raise StorageError(f"載入 JSON 資料失敗: {str(e)}")
            
    def save_text(
        this,
        text: str,
        file_path: str,
        compress: bool = False,
        encoding: str = "utf-8"
    ):
        """
        儲存文字資料
        
        Args:
            text: 要儲存的文字
            file_path: 檔案路徑
            compress: 是否壓縮
            encoding: 編碼方式
        """
        try:
            # 建立目錄
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # 儲存檔案
            if compress:
                file_path = f"{file_path}.gz"
                with gzip.open(file_path, "wt", encoding=encoding) as f:
                    f.write(text)
            else:
                with open(file_path, "w", encoding=encoding) as f:
                    f.write(text)
                    
            this.logger.info(f"文字已儲存至: {file_path}")
            
        except Exception as e:
            this.logger.error(f"儲存文字資料失敗: {str(e)}")
            raise StorageError(f"儲存文字資料失敗: {str(e)}")
            
    def load_text(
        this,
        file_path: str,
        compress: bool = False,
        encoding: str = "utf-8"
    ) -> str:
        """
        載入文字資料
        
        Args:
            file_path: 檔案路徑
            compress: 是否壓縮
            encoding: 編碼方式
            
        Returns:
            文字資料
        """
        try:
            if compress:
                file_path = f"{file_path}.gz"
                with gzip.open(file_path, "rt", encoding=encoding) as f:
                    text = f.read()
            else:
                with open(file_path, "r", encoding=encoding) as f:
                    text = f.read()
                    
            return text
            
        except Exception as e:
            this.logger.error(f"載入文字資料失敗: {str(e)}")
            raise StorageError(f"載入文字資料失敗: {str(e)}")
            
    def save_binary(
        this,
        data: bytes,
        file_path: str,
        compress: bool = False
    ):
        """
        儲存二進位資料
        
        Args:
            data: 要儲存的資料
            file_path: 檔案路徑
            compress: 是否壓縮
        """
        try:
            # 建立目錄
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # 儲存檔案
            if compress:
                file_path = f"{file_path}.gz"
                with gzip.open(file_path, "wb") as f:
                    f.write(data)
            else:
                with open(file_path, "wb") as f:
                    f.write(data)
                    
            this.logger.info(f"二進位資料已儲存至: {file_path}")
            
        except Exception as e:
            this.logger.error(f"儲存二進位資料失敗: {str(e)}")
            raise StorageError(f"儲存二進位資料失敗: {str(e)}")
            
    def load_binary(
        this,
        file_path: str,
        compress: bool = False
    ) -> bytes:
        """
        載入二進位資料
        
        Args:
            file_path: 檔案路徑
            compress: 是否壓縮
            
        Returns:
            二進位資料
        """
        try:
            if compress:
                file_path = f"{file_path}.gz"
                with gzip.open(file_path, "rb") as f:
                    data = f.read()
            else:
                with open(file_path, "rb") as f:
                    data = f.read()
                    
            return data
            
        except Exception as e:
            this.logger.error(f"載入二進位資料失敗: {str(e)}")
            raise StorageError(f"載入二進位資料失敗: {str(e)}")
            
    def save_file(
        this,
        src_path: str,
        dst_path: str,
        compress: bool = False
    ):
        """
        儲存檔案
        
        Args:
            src_path: 來源檔案路徑
            dst_path: 目標檔案路徑
            compress: 是否壓縮
        """
        try:
            # 建立目錄
            os.makedirs(os.path.dirname(dst_path), exist_ok=True)
            
            # 儲存檔案
            if compress:
                dst_path = f"{dst_path}.gz"
                with open(src_path, "rb") as f_in:
                    with gzip.open(dst_path, "wb") as f_out:
                        shutil.copyfileobj(f_in, f_out)
            else:
                shutil.copy2(src_path, dst_path)
                
            this.logger.info(f"檔案已儲存至: {dst_path}")
            
        except Exception as e:
            this.logger.error(f"儲存檔案失敗: {str(e)}")
            raise StorageError(f"儲存檔案失敗: {str(e)}")
            
    def load_file(
        this,
        src_path: str,
        dst_path: str,
        compress: bool = False
    ):
        """
        載入檔案
        
        Args:
            src_path: 來源檔案路徑
            dst_path: 目標檔案路徑
            compress: 是否壓縮
        """
        try:
            if compress:
                src_path = f"{src_path}.gz"
                with gzip.open(src_path, "rb") as f_in:
                    with open(dst_path, "wb") as f_out:
                        shutil.copyfileobj(f_in, f_out)
            else:
                shutil.copy2(src_path, dst_path)
                
        except Exception as e:
            this.logger.error(f"載入檔案失敗: {str(e)}")
            raise StorageError(f"載入檔案失敗: {str(e)}")
            
    def save_results(
        this,
        data: Union[Dict[str, Any], List[Any]],
        prefix: str = "results",
        compress: bool = False,
        ensure_ascii: bool = False,
        indent: int = 4
    ) -> str:
        """
        儲存結果資料
        
        Args:
            data: 要儲存的資料
            prefix: 檔案前綴
            compress: 是否壓縮
            ensure_ascii: 是否確保 ASCII 編碼
            indent: 縮排空格數
            
        Returns:
            檔案路徑
        """
        try:
            # 建立檔案名稱
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_name = f"{prefix}_{timestamp}.json"
            file_path = os.path.join(this.config.storage.results_dir, file_name)
            
            # 儲存資料
            this.save_json(
                data,
                file_path,
                compress=compress,
                ensure_ascii=ensure_ascii,
                indent=indent
            )
            
            return file_path
            
        except Exception as e:
            this.logger.error(f"儲存結果資料失敗: {str(e)}")
            raise StorageError(f"儲存結果資料失敗: {str(e)}")
            
    def get_results_files(
        this,
        prefix: str = "results",
        compress: bool = False
    ) -> List[str]:
        """
        獲取結果檔案列表
        
        Args:
            prefix: 檔案前綴
            compress: 是否壓縮
            
        Returns:
            檔案路徑列表
        """
        try:
            # 建立檔案模式
            pattern = f"{prefix}_*.json"
            if compress:
                pattern = f"{pattern}.gz"
                
            # 搜尋檔案
            files = []
            for file in Path(this.config.storage.results_dir).glob(pattern):
                files.append(str(file))
                
            return sorted(files, reverse=True)
            
        except Exception as e:
            this.logger.error(f"獲取結果檔案列表失敗: {str(e)}")
            raise StorageError(f"獲取結果檔案列表失敗: {str(e)}")
            
    def delete_results_files(
        this,
        prefix: str = "results",
        compress: bool = False
    ):
        """
        刪除結果檔案
        
        Args:
            prefix: 檔案前綴
            compress: 是否壓縮
        """
        try:
            # 獲取檔案列表
            files = this.get_results_files(prefix, compress)
            
            # 刪除檔案
            for file in files:
                os.remove(file)
                
            this.logger.info(f"已刪除 {len(files)} 個結果檔案")
            
        except Exception as e:
            this.logger.error(f"刪除結果檔案失敗: {str(e)}")
            raise StorageError(f"刪除結果檔案失敗: {str(e)}")
            
    def clear_results(self):
        """清空結果目錄"""
        try:
            # 刪除目錄
            if os.path.exists(this.config.storage.results_dir):
                shutil.rmtree(this.config.storage.results_dir)
                
            # 重新建立目錄
            os.makedirs(this.config.storage.results_dir, exist_ok=True)
            
            this.logger.info("結果目錄已清空")
            
        except Exception as e:
            this.logger.error(f"清空結果目錄失敗: {str(e)}")
            raise StorageError(f"清空結果目錄失敗: {str(e)}") 