from typing import Any, Dict, List, Optional, Union
import json
import csv
import os
from pathlib import Path
import pandas as pd
from datetime import datetime
from loguru import logger

from ..utils.exceptions import StorageException


class StorageManager:
    def __init__(self, base_dir: str = "data"):
        """
        初始化存儲管理器

        Args:
            base_dir: 基礎存儲目錄
        """
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        
        # 創建子目錄
        self.json_dir = self.base_dir / "json"
        self.csv_dir = self.base_dir / "csv"
        self.excel_dir = self.base_dir / "excel"
        self.raw_dir = self.base_dir / "raw"
        
        for dir_path in [self.json_dir, self.csv_dir, self.excel_dir, self.raw_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)

    def save_json(
        self,
        data: Union[Dict, List],
        filename: str,
        append: bool = False,
        pretty: bool = True,
    ) -> str:
        """
        保存 JSON 數據

        Args:
            data: 要保存的數據
            filename: 文件名
            append: 是否追加到現有文件
            pretty: 是否美化輸出

        Returns:
            str: 保存的文件路徑
        """
        try:
            file_path = self.json_dir / filename
            if not file_path.suffix:
                file_path = file_path.with_suffix(".json")

            if append and file_path.exists():
                with open(file_path, "r", encoding="utf-8") as f:
                    existing_data = json.load(f)
                if isinstance(existing_data, list):
                    if isinstance(data, list):
                        existing_data.extend(data)
                    else:
                        existing_data.append(data)
                    data = existing_data
                else:
                    data = [existing_data, data]

            with open(file_path, "w", encoding="utf-8") as f:
                if pretty:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                else:
                    json.dump(data, f, ensure_ascii=False)

            logger.info(f"JSON 數據已保存到: {file_path}")
            return str(file_path)
        except Exception as e:
            logger.error(f"保存 JSON 數據時發生錯誤: {str(e)}")
            raise StorageException(f"保存 JSON 數據失敗: {str(e)}")

    def save_csv(
        self,
        data: List[Dict],
        filename: str,
        append: bool = False,
        headers: Optional[List[str]] = None,
    ) -> str:
        """
        保存 CSV 數據

        Args:
            data: 要保存的數據
            filename: 文件名
            append: 是否追加到現有文件
            headers: 列標題

        Returns:
            str: 保存的文件路徑
        """
        try:
            file_path = self.csv_dir / filename
            if not file_path.suffix:
                file_path = file_path.with_suffix(".csv")

            if not data:
                raise StorageException("沒有數據可保存")

            if headers is None:
                headers = list(data[0].keys())

            mode = "a" if append and file_path.exists() else "w"
            with open(file_path, mode, newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=headers)
                if mode == "w":
                    writer.writeheader()
                writer.writerows(data)

            logger.info(f"CSV 數據已保存到: {file_path}")
            return str(file_path)
        except Exception as e:
            logger.error(f"保存 CSV 數據時發生錯誤: {str(e)}")
            raise StorageException(f"保存 CSV 數據失敗: {str(e)}")

    def save_excel(
        self,
        data: Union[Dict[str, List[Dict]], List[Dict]],
        filename: str,
        sheet_name: str = "Sheet1",
    ) -> str:
        """
        保存 Excel 數據

        Args:
            data: 要保存的數據
            filename: 文件名
            sheet_name: 工作表名稱

        Returns:
            str: 保存的文件路徑
        """
        try:
            file_path = self.excel_dir / filename
            if not file_path.suffix:
                file_path = file_path.with_suffix(".xlsx")

            if isinstance(data, list):
                df = pd.DataFrame(data)
                with pd.ExcelWriter(file_path, engine="openpyxl") as writer:
                    df.to_excel(writer, sheet_name=sheet_name, index=False)
            else:
                with pd.ExcelWriter(file_path, engine="openpyxl") as writer:
                    for sheet_name, sheet_data in data.items():
                        df = pd.DataFrame(sheet_data)
                        df.to_excel(writer, sheet_name=sheet_name, index=False)

            logger.info(f"Excel 數據已保存到: {file_path}")
            return str(file_path)
        except Exception as e:
            logger.error(f"保存 Excel 數據時發生錯誤: {str(e)}")
            raise StorageException(f"保存 Excel 數據失敗: {str(e)}")

    def save_raw(
        self,
        data: Union[str, bytes],
        filename: str,
        encoding: str = "utf-8",
    ) -> str:
        """
        保存原始數據

        Args:
            data: 要保存的數據
            filename: 文件名
            encoding: 文件編碼

        Returns:
            str: 保存的文件路徑
        """
        try:
            file_path = self.raw_dir / filename
            
            if isinstance(data, str):
                with open(file_path, "w", encoding=encoding) as f:
                    f.write(data)
            else:
                with open(file_path, "wb") as f:
                    f.write(data)

            logger.info(f"原始數據已保存到: {file_path}")
            return str(file_path)
        except Exception as e:
            logger.error(f"保存原始數據時發生錯誤: {str(e)}")
            raise StorageException(f"保存原始數據失敗: {str(e)}")

    def load_json(self, filename: str) -> Union[Dict, List]:
        """
        加載 JSON 數據

        Args:
            filename: 文件名

        Returns:
            Union[Dict, List]: 加載的數據
        """
        try:
            file_path = self.json_dir / filename
            if not file_path.suffix:
                file_path = file_path.with_suffix(".json")

            if not file_path.exists():
                raise StorageException(f"文件不存在: {file_path}")

            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            logger.info(f"已從 {file_path} 加載 JSON 數據")
            return data
        except Exception as e:
            logger.error(f"加載 JSON 數據時發生錯誤: {str(e)}")
            raise StorageException(f"加載 JSON 數據失敗: {str(e)}")

    def load_csv(self, filename: str) -> List[Dict]:
        """
        加載 CSV 數據

        Args:
            filename: 文件名

        Returns:
            List[Dict]: 加載的數據
        """
        try:
            file_path = self.csv_dir / filename
            if not file_path.suffix:
                file_path = file_path.with_suffix(".csv")

            if not file_path.exists():
                raise StorageException(f"文件不存在: {file_path}")

            with open(file_path, "r", encoding="utf-8", newline="") as f:
                reader = csv.DictReader(f)
                data = list(reader)

            logger.info(f"已從 {file_path} 加載 CSV 數據")
            return data
        except Exception as e:
            logger.error(f"加載 CSV 數據時發生錯誤: {str(e)}")
            raise StorageException(f"加載 CSV 數據失敗: {str(e)}")

    def load_excel(self, filename: str, sheet_name: Optional[str] = None) -> Union[Dict[str, List[Dict]], List[Dict]]:
        """
        加載 Excel 數據

        Args:
            filename: 文件名
            sheet_name: 工作表名稱

        Returns:
            Union[Dict[str, List[Dict]], List[Dict]]: 加載的數據
        """
        try:
            file_path = self.excel_dir / filename
            if not file_path.suffix:
                file_path = file_path.with_suffix(".xlsx")

            if not file_path.exists():
                raise StorageException(f"文件不存在: {file_path}")

            if sheet_name:
                df = pd.read_excel(file_path, sheet_name=sheet_name)
                data = df.to_dict("records")
            else:
                data = {}
                xls = pd.ExcelFile(file_path)
                for sheet in xls.sheet_names:
                    df = pd.read_excel(file_path, sheet_name=sheet)
                    data[sheet] = df.to_dict("records")

            logger.info(f"已從 {file_path} 加載 Excel 數據")
            return data
        except Exception as e:
            logger.error(f"加載 Excel 數據時發生錯誤: {str(e)}")
            raise StorageException(f"加載 Excel 數據失敗: {str(e)}")

    def load_raw(self, filename: str, encoding: str = "utf-8") -> Union[str, bytes]:
        """
        加載原始數據

        Args:
            filename: 文件名
            encoding: 文件編碼

        Returns:
            Union[str, bytes]: 加載的數據
        """
        try:
            file_path = self.raw_dir / filename

            if not file_path.exists():
                raise StorageException(f"文件不存在: {file_path}")

            # 嘗試以文本方式讀取
            try:
                with open(file_path, "r", encoding=encoding) as f:
                    data = f.read()
            except UnicodeDecodeError:
                # 如果解碼失敗，則以二進制方式讀取
                with open(file_path, "rb") as f:
                    data = f.read()

            logger.info(f"已從 {file_path} 加載原始數據")
            return data
        except Exception as e:
            logger.error(f"加載原始數據時發生錯誤: {str(e)}")
            raise StorageException(f"加載原始數據失敗: {str(e)}")

    def get_latest_file(self, directory: Path, pattern: str = "*") -> Optional[Path]:
        """
        獲取目錄中最新的文件

        Args:
            directory: 目錄路徑
            pattern: 文件匹配模式

        Returns:
            Optional[Path]: 最新文件的路徑
        """
        try:
            files = list(directory.glob(pattern))
            if not files:
                return None
            return max(files, key=lambda x: x.stat().st_mtime)
        except Exception as e:
            logger.error(f"獲取最新文件時發生錯誤: {str(e)}")
            return None 