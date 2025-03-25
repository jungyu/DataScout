from typing import List, Dict
from ..utils.logger import setup_logger

class DataExtractor:
    """負責數據提取的邏輯"""
    
    def __init__(self, template_crawler):
        self.crawler = template_crawler
        self.logger = setup_logger(__name__)
    
    def extract_page(self, page: int) -> List[Dict]:
        """提取單頁數據"""
        url = self.crawler._build_url(page)
        if not self.crawler._navigate_to_url(url):
            return []
            
        list_items = self.crawler._extract_list_items()
        return self._process_items(list_items)
    
    def _process_items(self, items: List[Dict]) -> List[Dict]:
        """處理列表項"""
        results = []
        
        for item in items:
            detail_link = item.get('detail_link')
            if not detail_link:
                continue
                
            detail_data = self.crawler._extract_detail_data(detail_link)
            combined_data = self.crawler._combine_data(item, detail_data)
            results.append(combined_data)
            
            self.crawler._random_delay('between_items')
            
        return results
