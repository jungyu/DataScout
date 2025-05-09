"""
存儲管理模組

提供瀏覽器會話存儲（cookies、localStorage 等）的管理功能。
"""

import os
import json
import time
from typing import Dict, List, Optional, Any, Union
from datetime import datetime

from playwright_base.utils.logger import setup_logger
from playwright_base.utils.exceptions import StorageException

# 設置日誌
logger = setup_logger(name=__name__)

class StorageManager:
    """
    瀏覽器存儲管理類。
    
    提供 cookies、localStorage 等存儲數據的管理功能。
    """
    
    def __init__(self, storage_dir: str = "data/storage"):
        """
        初始化 StorageManager 實例。
        
        參數:
            storage_dir (str): 存儲文件的目錄路徑。
        """
        self.storage_dir = storage_dir
        
        # 創建存儲目錄
        if not os.path.exists(self.storage_dir):
            try:
                os.makedirs(self.storage_dir)
                logger.info(f"已創建存儲目錄: {self.storage_dir}")
            except Exception as e:
                logger.error(f"創建存儲目錄時發生錯誤: {str(e)}")
    
    def save_storage_state(self, context, name: str = None) -> Optional[str]:
        """
        保存瀏覽器上下文的存儲狀態（cookies、localStorage 等）。
        
        參數:
            context: Playwright 瀏覽器上下文對象。
            name (str): 存儲狀態的名稱，用於後續識別和載入，默認使用時間戳。
            
        返回:
            Optional[str]: 保存的檔案路徑，若保存失敗則返回 None。
        """
        if not context:
            logger.warning("無法保存存儲狀態：瀏覽器上下文為空")
            return None
            
        try:
            # 如果沒有指定名稱，使用時間戳
            if not name:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                name = f"storage_{timestamp}"
                
            # 確保副檔名是 .json
            if not name.endswith(".json"):
                name = f"{name}.json"
                
            file_path = os.path.join(self.storage_dir, name)
            
            # 保存存儲狀態
            context.storage_state(path=file_path)
            
            logger.info(f"已保存瀏覽器存儲狀態到: {file_path}")
            return file_path
        except Exception as e:
            logger.error(f"保存瀏覽器存儲狀態時發生錯誤: {str(e)}")
            return None
    
    def load_storage_state(self, path_or_name: str) -> Optional[Dict[str, Any]]:
        """
        載入瀏覽器存儲狀態。
        
        參數:
            path_or_name (str): 存儲狀態的檔案路徑或名稱。
            
        返回:
            Optional[Dict[str, Any]]: 載入的存儲狀態數據，若載入失敗則返回 None。
        """
        try:
            # 檢查是否為完整路徑
            if os.path.exists(path_or_name):
                file_path = path_or_name
            else:
                # 嘗試作為名稱在存儲目錄中查找
                if not path_or_name.endswith(".json"):
                    path_or_name = f"{path_or_name}.json"
                file_path = os.path.join(self.storage_dir, path_or_name)
                
                if not os.path.exists(file_path):
                    logger.warning(f"存儲狀態檔案不存在: {file_path}")
                    return None
            
            # 讀取存儲狀態
            with open(file_path, "r", encoding="utf-8") as f:
                storage_state = json.load(f)
                
            logger.info(f"已載入存儲狀態: {file_path}")
            return storage_state
        except Exception as e:
            logger.error(f"載入存儲狀態時發生錯誤: {str(e)}")
            return None
    
    def get_cookies_for_domain(self, storage_state: Dict[str, Any], domain: str) -> List[Dict[str, Any]]:
        """
        從存儲狀態中獲取指定網域的 cookies。
        
        參數:
            storage_state (Dict[str, Any]): 存儲狀態數據。
            domain (str): 要過濾的網域名稱。
            
        返回:
            List[Dict[str, Any]]: 指定網域的 cookies 列表。
        """
        if not storage_state or "cookies" not in storage_state:
            logger.warning("存儲狀態無效或不包含 cookies")
            return []
            
        # 過濾指定網域的 cookies
        domain_cookies = []
        for cookie in storage_state["cookies"]:
            cookie_domain = cookie.get("domain", "")
            if domain in cookie_domain or (domain.startswith(".") and domain[1:] in cookie_domain):
                domain_cookies.append(cookie)
                
        logger.info(f"找到 {len(domain_cookies)} 個屬於網域 '{domain}' 的 cookies")
        return domain_cookies
    
    def merge_cookies(self, target_state: Dict[str, Any], source_state: Dict[str, Any]) -> Dict[str, Any]:
        """
        合併兩個存儲狀態中的 cookies。
        
        參數:
            target_state (Dict[str, Any]): 目標存儲狀態，將合併至此。
            source_state (Dict[str, Any]): 源存儲狀態，將被合併的數據來源。
            
        返回:
            Dict[str, Any]: 合併後的存儲狀態。
        """
        if not target_state:
            target_state = {"cookies": [], "origins": []}
            
        if not source_state or "cookies" not in source_state:
            logger.warning("源存儲狀態無效或不包含 cookies")
            return target_state
            
        # 複製目標存儲狀態
        merged_state = {
            "cookies": list(target_state.get("cookies", [])),
            "origins": list(target_state.get("origins", []))
        }
        
        # 記錄現有的 cookie 名稱和網域
        existing_cookies = {(c.get("name", ""), c.get("domain", "")): i 
                           for i, c in enumerate(merged_state["cookies"])}
        
        # 合併 cookies
        for cookie in source_state.get("cookies", []):
            key = (cookie.get("name", ""), cookie.get("domain", ""))
            if key in existing_cookies:
                # 更新現有 cookie
                merged_state["cookies"][existing_cookies[key]] = cookie
            else:
                # 添加新 cookie
                merged_state["cookies"].append(cookie)
                
        # 合併 origins
        for origin in source_state.get("origins", []):
            if origin not in merged_state["origins"]:
                merged_state["origins"].append(origin)
                
        logger.info(f"合併後的存儲狀態包含 {len(merged_state['cookies'])} 個 cookies 和 "
                   f"{len(merged_state['origins'])} 個 origins")
        return merged_state
    
    def save_merged_storage(self, states: List[Dict[str, Any]], name: str = None) -> Optional[str]:
        """
        合併並保存多個存儲狀態。
        
        參數:
            states (List[Dict[str, Any]]): 要合併的存儲狀態列表。
            name (str): 保存的檔案名稱，默認使用時間戳。
            
        返回:
            Optional[str]: 保存的檔案路徑，若保存失敗則返回 None。
        """
        if not states:
            logger.warning("無存儲狀態可合併")
            return None
            
        try:
            # 初始化合併狀態
            merged_state = {}
            
            # 逐個合併
            for state in states:
                merged_state = self.merge_cookies(merged_state, state)
                
            # 如果沒有指定名稱，使用時間戳
            if not name:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                name = f"merged_storage_{timestamp}"
                
            # 確保副檔名是 .json
            if not name.endswith(".json"):
                name = f"{name}.json"
                
            file_path = os.path.join(self.storage_dir, name)
            
            # 保存合併後的存儲狀態
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(merged_state, f, indent=2)
                
            logger.info(f"已保存合併的存儲狀態到: {file_path}")
            return file_path
        except Exception as e:
            logger.error(f"保存合併的存儲狀態時發生錯誤: {str(e)}")
            return None
    
    def list_storage_files(self) -> List[Dict[str, Any]]:
        """
        列出所有可用的存儲狀態文件。
        
        返回:
            List[Dict[str, Any]]: 包含檔案資訊的列表。
        """
        files = []
        
        try:
            if os.path.exists(self.storage_dir):
                for filename in os.listdir(self.storage_dir):
                    if filename.endswith(".json"):
                        file_path = os.path.join(self.storage_dir, filename)
                        file_info = {
                            "name": filename,
                            "path": file_path,
                            "size": os.path.getsize(file_path),
                            "modified": datetime.fromtimestamp(os.path.getmtime(file_path)).strftime(
                                "%Y-%m-%d %H:%M:%S"
                            )
                        }
                        
                        # 嘗試讀取檔案內容以獲取更多資訊
                        try:
                            with open(file_path, "r", encoding="utf-8") as f:
                                data = json.load(f)
                                file_info["cookies_count"] = len(data.get("cookies", []))
                                file_info["origins_count"] = len(data.get("origins", []))
                                
                                # 提取網域資訊
                                domains = set()
                                for cookie in data.get("cookies", []):
                                    if "domain" in cookie:
                                        domains.add(cookie["domain"])
                                file_info["domains"] = list(domains)
                        except Exception:
                            # 讀取失敗時不添加額外資訊
                            pass
                            
                        files.append(file_info)
                        
                # 按修改時間降序排序
                files.sort(key=lambda x: x["modified"], reverse=True)
                
            logger.info(f"找到 {len(files)} 個存儲狀態檔案")
        except Exception as e:
            logger.error(f"列出存儲檔案時發生錯誤: {str(e)}")
            
        return files
    
    def delete_storage_file(self, path_or_name: str) -> bool:
        """
        刪除指定的存儲狀態檔案。
        
        參數:
            path_or_name (str): 存儲狀態的檔案路徑或名稱。
            
        返回:
            bool: 是否成功刪除。
        """
        try:
            # 檢查是否為完整路徑
            if os.path.exists(path_or_name):
                file_path = path_or_name
            else:
                # 嘗試作為名稱在存儲目錄中查找
                if not path_or_name.endswith(".json"):
                    path_or_name = f"{path_or_name}.json"
                file_path = os.path.join(self.storage_dir, path_or_name)
                
                if not os.path.exists(file_path):
                    logger.warning(f"存儲狀態檔案不存在: {file_path}")
                    return False
            
            # 刪除檔案
            os.remove(file_path)
            logger.info(f"已刪除存儲狀態檔案: {file_path}")
            return True
        except Exception as e:
            logger.error(f"刪除存儲狀態檔案時發生錯誤: {str(e)}")
            return False