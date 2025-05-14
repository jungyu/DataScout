"""
圖表應用程式單元測試
"""
import os
import sys
import unittest
import json
import pandas as pd
from pathlib import Path
import pytest
import requests
from fastapi import FastAPI
import uvicorn
import threading
import time

# 添加應用目錄到 Python 路徑
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.main import app

# 啟動一個測試伺服器
SERVER_HOST = "127.0.0.1"
SERVER_PORT = 8888
SERVER_URL = f"http://{SERVER_HOST}:{SERVER_PORT}"

def run_server():
    """在獨立線程中運行測試伺服器"""
    uvicorn.run(app, host=SERVER_HOST, port=SERVER_PORT, log_level="error")

# 啟動測試伺服器線程
server_thread = threading.Thread(target=run_server, daemon=True)
server_thread.start()

# 等待伺服器啟動
time.sleep(2)

class ChartAppTest(unittest.TestCase):
    """圖表應用程式測試類"""
    
    def setUp(self):
        """設置測試環境"""
        # 使用 requests 庫作為測試客戶端
        self.base_url = SERVER_URL
        self.sample_csv_path = "/Users/aaron/Projects/DataScout/data/csv/sample_data.csv"
        self.sample_json_path = "/Users/aaron/Projects/DataScout/data/json/sample_data.json"
        self.sample_excel_path = "/Users/aaron/Projects/DataScout/data/excel/sample_data.xlsx"
        
        # 確保測試數據存在
        self._ensure_test_data_exists()
    
    def _ensure_test_data_exists(self):
        """確保測試數據檔案存在"""
        # 如果測試數據不存在，則創建
        if not os.path.exists(self.sample_csv_path):
            df = pd.DataFrame({
                'date': ['2024-01-01', '2024-01-02', '2024-01-03'],
                'category': ['Electronics', 'Clothing', 'Home Goods'],
                'sales': [1500, 1200, 950],
                'profit': [450, 320, 280]
            })
            df.to_csv(self.sample_csv_path, index=False)
            
        if not os.path.exists(self.sample_json_path):
            data = [
                {"date": "2024-01-01", "category": "Electronics", "sales": 1500, "profit": 450},
                {"date": "2024-01-02", "category": "Clothing", "sales": 1200, "profit": 320},
                {"date": "2024-01-03", "category": "Home Goods", "sales": 950, "profit": 280}
            ]
            with open(self.sample_json_path, 'w') as f:
                json.dump(data, f)
                
        if not os.path.exists(self.sample_excel_path):
            df = pd.DataFrame({
                'date': ['2024-01-01', '2024-01-02', '2024-01-03'],
                'category': ['Electronics', 'Clothing', 'Home Goods'],
                'sales': [1500, 1200, 950],
                'profit': [450, 320, 280]
            })
            df.to_excel(self.sample_excel_path, index=False)
    
    def test_home_page(self):
        """測試主頁面響應"""
        response = requests.get(f"{self.base_url}/")
        self.assertEqual(response.status_code, 200)
        
    def test_api_data_files(self):
        """測試獲取數據文件列表API"""
        response = requests.get(f"{self.base_url}/api/data-files/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("data_files", data)
        self.assertIsInstance(data["data_files"], dict)
        
    def test_api_file_data(self):
        """測試獲取CSV檔案數據API"""
        response = requests.get(f"{self.base_url}/api/file-data/?filename=sample_data.csv&file_type=csv")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("datasets", data)
        self.assertIn("labels", data)
        
    def test_api_file_structure(self):
        """測試獲取檔案結構API"""
        response = requests.get(f"{self.base_url}/api/file-structure/?filename=sample_data.csv&file_type=csv")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("columns", data)
        # 實際 API 回傳欄位詳細資訊放在 columns 裡面，沒有單獨的 dtypes 欄位
        self.assertIn("filename", data)
        
    def test_olap_operation(self):
        """測試OLAP操作API"""
        payload = {
            "filename": "sample_data.csv",
            "file_type": "csv",
            "operation": "groupby",
            "group_columns": "category",
            "value_column": "sales",
            "agg_function": "sum"
        }
        response = requests.post(f"{self.base_url}/api/olap-operation/", data=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("datasets", data)
        self.assertIn("labels", data)

if __name__ == "__main__":
    unittest.main()
