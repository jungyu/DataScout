import os
import json
from typing import Any, Dict, Optional
import pandas as pd

class LocalStorage:
    def __init__(self, base_path: str = "data"):
        """初始化 LocalStorage

        Args:
            base_path (str): 基礎儲存路徑
        """
        self.base_path = base_path
        os.makedirs(base_path, exist_ok=True)

    def save_json(self, data: Dict[str, Any], filename: str) -> None:
        """將資料儲存為 JSON 檔案

        Args:
            data: 要儲存的資料
            filename: 檔案名稱
        """
        filepath = os.path.join(self.base_path, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def load_json(self, filename: str) -> Optional[Dict[str, Any]]:
        """讀取 JSON 檔案

        Args:
            filename: 檔案名稱

        Returns:
            讀取的資料，如果檔案不存在則返回 None
        """
        filepath = os.path.join(self.base_path, filename)
        if not os.path.exists(filepath):
            return None
        
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)

    def save_csv(self, data: pd.DataFrame, filename: str) -> None:
        """將 DataFrame 儲存為 CSV 檔案

        Args:
            data: DataFrame 資料
            filename: 檔案名稱
        """
        filepath = os.path.join(self.base_path, filename)
        data.to_csv(filepath, index=False, encoding='utf-8')

    def load_csv(self, filename: str) -> Optional[pd.DataFrame]:
        """讀取 CSV 檔案

        Args:
            filename: 檔案名稱

        Returns:
            DataFrame 資料，如果檔案不存在則返回 None
        """
        filepath = os.path.join(self.base_path, filename)
        if not os.path.exists(filepath):
            return None
        
        return pd.read_csv(filepath)

    def file_exists(self, filename: str) -> bool:
        """檢查檔案是否存在

        Args:
            filename: 檔案名稱

        Returns:
            檔案是否存在
        """
        return os.path.exists(os.path.join(self.base_path, filename))
