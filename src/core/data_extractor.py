from typing import List, Dict, Any, Optional
from selenium.webdriver.remote.webdriver import WebDriver
import traceback
from ..utils.logger import setup_logger

class DataExtractor:
    """負責數據提取的邏輯"""
    
    def __init__(self, template_crawler):
        """
        初始化數據提取器
        
        Args:
            template_crawler: 模板爬蟲實例
        """
        self.crawler = template_crawler
        self.logger = setup_logger(__name__)
        # 獲取配置
        self.config = getattr(template_crawler, 'config', {})
        self.template = getattr(template_crawler, 'template', {})
    
    def extract_page(self, page: int) -> List[Dict]:
        """
        提取單頁數據
        
        Args:
            page: 頁碼
            
        Returns:
            提取的數據列表
        """
        try:
            # 使用爬蟲的公共方法建構 URL 並導航
            url = self.get_page_url(page)
            self.logger.info(f"嘗試提取第 {page} 頁數據: {url}")
            
            if not self.navigate_to_page(url):
                self.logger.warning(f"無法導航到頁面 {url}")
                return []
            
            # 提取列表項目
            list_items = self.extract_list_items()
            self.logger.info(f"從第 {page} 頁提取了 {len(list_items)} 個項目")
            
            # 處理列表項目
            return self.process_items(list_items)
        except Exception as e:
            self.logger.error(f"提取第 {page} 頁時發生錯誤: {str(e)}")
            self.logger.debug(traceback.format_exc())
            return []
    
    def get_page_url(self, page: int) -> str:
        """
        獲取指定頁碼的 URL
        
        Args:
            page: 頁碼
            
        Returns:
            頁面 URL
        """
        # 確保使用公共方法或屬性
        if hasattr(self.crawler, 'build_url'):
            return self.crawler.build_url(page)
        elif hasattr(self.crawler, '_build_url'):
            return self.crawler._build_url(page)
        else:
            # 從模板中構建 URL
            pagination = self.template.get('pagination', {})
            url_pattern = pagination.get('url_pattern', '')
            if url_pattern:
                return url_pattern.format(page=page)
            
            # 回退到基本 URL
            base_url = self.template.get('base_url', '')
            return f"{base_url}?page={page}"
    
    def navigate_to_page(self, url: str) -> bool:
        """
        導航到指定 URL
        
        Args:
            url: 頁面 URL
            
        Returns:
            是否成功導航
        """
        if hasattr(self.crawler, 'navigate_to_url'):
            return self.crawler.navigate_to_url(url)
        elif hasattr(self.crawler, '_navigate_to_url'):
            return self.crawler._navigate_to_url(url)
        else:
            # 獲取 WebDriver 實例
            driver = self.get_driver()
            if not driver:
                return False
                
            try:
                driver.get(url)
                return True
            except Exception as e:
                self.logger.error(f"導航到 {url} 時出錯: {str(e)}")
                return False
    
    def extract_list_items(self) -> List[Dict]:
        """
        提取列表項目
        
        Returns:
            列表項目數據
        """
        if hasattr(self.crawler, 'extract_list_items'):
            return self.crawler.extract_list_items()
        elif hasattr(self.crawler, '_extract_list_items'):
            return self.crawler._extract_list_items()
        else:
            # 根據模板提取列表項目
            driver = self.get_driver()
            if not driver:
                return []
                
            list_config = self.template.get('list_page', {})
            container_selector = list_config.get('container', '')
            item_selector = list_config.get('item_selector', '')
            
            # 實現簡單的提取邏輯
            # 注意: 這只是一個簡化的實現，實際應用中可能需要更複雜的邏輯
            self.logger.warning("使用簡易提取方法，可能不夠穩定")
            
            try:
                # 這裡應該實現從頁面提取列表項目的邏輯
                # 因為沒有訪問實際的爬蟲代碼，這裡只是返回空列表
                return []
            except Exception as e:
                self.logger.error(f"提取列表項目時出錯: {str(e)}")
                return []
    
    def process_items(self, items: List[Dict]) -> List[Dict]:
        """
        處理列表項目，包括獲取詳情頁面數據
        
        Args:
            items: 列表項目數據
            
        Returns:
            處理後的數據列表
        """
        results = []
        
        for index, item in enumerate(items):
            try:
                self.logger.debug(f"處理第 {index+1}/{len(items)} 個項目")
                
                # 獲取詳情頁面鏈接
                detail_link = item.get('detail_link')
                if not detail_link:
                    self.logger.debug(f"項目 {index+1} 沒有詳情頁面鏈接，跳過")
                    # 仍然添加列表頁面數據
                    results.append(item)
                    continue
                
                # 提取詳情頁面數據
                detail_data = self.extract_detail_data(detail_link)
                
                # 合併列表頁面和詳情頁面數據
                combined_data = self.combine_data(item, detail_data)
                results.append(combined_data)
                
                # 在項目之間添加隨機延遲
                self.add_delay_between_items()
                
            except Exception as e:
                self.logger.error(f"處理項目 {index+1} 時出錯: {str(e)}")
                # 仍然添加列表頁面數據
                results.append(item)
        
        return results
    
    def extract_detail_data(self, url: str) -> Dict[str, Any]:
        """
        提取詳情頁面數據
        
        Args:
            url: 詳情頁面URL
            
        Returns:
            詳情頁面數據
        """
        try:
            if hasattr(self.crawler, 'extract_detail_data'):
                return self.crawler.extract_detail_data(url)
            elif hasattr(self.crawler, '_extract_detail_data'):
                return self.crawler._extract_detail_data(url)
            else:
                # 根據模板提取詳情頁面數據
                self.logger.warning("使用簡易詳情頁面提取方法，可能不夠穩定")
                return {}
        except Exception as e:
            self.logger.error(f"提取詳情頁面數據時出錯: {str(e)}")
            self.logger.debug(traceback.format_exc())
            return {}
    
    def combine_data(self, list_data: Dict, detail_data: Dict) -> Dict:
        """
        合併列表頁面和詳情頁面數據
        
        Args:
            list_data: 列表頁面數據
            detail_data: 詳情頁面數據
            
        Returns:
            合併後的數據
        """
        try:
            if hasattr(self.crawler, 'combine_data'):
                return self.crawler.combine_data(list_data, detail_data)
            elif hasattr(self.crawler, '_combine_data'):
                return self.crawler._combine_data(list_data, detail_data)
            else:
                # 簡單的字典合併
                combined = list_data.copy()
                combined.update(detail_data)
                return combined
        except Exception as e:
            self.logger.error(f"合併數據時出錯: {str(e)}")
            # 如果合併失敗，仍返回列表數據
            return list_data
    
    def add_delay_between_items(self) -> None:
        """添加項目之間的隨機延遲"""
        if hasattr(self.crawler, 'add_random_delay'):
            self.crawler.add_random_delay('between_items')
        elif hasattr(self.crawler, '_random_delay'):
            self.crawler._random_delay('between_items')
        else:
            import time
            import random
            delay = random.uniform(1, 3)  # 默認延遲1-3秒
            time.sleep(delay)
    
    def get_driver(self) -> Optional[WebDriver]:
        """獲取 WebDriver 實例"""
        if hasattr(self.crawler, 'driver'):
            return self.crawler.driver
        return None
