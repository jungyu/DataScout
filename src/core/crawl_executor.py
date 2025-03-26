from typing import List, Dict, Optional
from .data_extractor import DataExtractor
from ..utils.logger import setup_logger

class CrawlExecutor:
    """負責執行爬蟲的核心邏輯"""
    
    def __init__(self, template_crawler):
        self.crawler = template_crawler
        self.logger = setup_logger(__name__)
        self.data_extractor = DataExtractor(template_crawler)
    
    def execute(self, strategy: str, **kwargs) -> List[Dict]:
        """執行爬蟲策略"""
        strategies = {
            'normal': self._normal_crawl,
            'resume': self._resume_crawl,
            'position': self._position_crawl
        }
        
        return strategies.get(strategy, self._normal_crawl)(**kwargs)
    
    def _normal_crawl(self, max_pages: Optional[int] = None, max_items: Optional[int] = None) -> List[Dict]:
        """正常爬取流程"""
        all_data = []
        page = 1
        
        try:
            if not self.crawler._init_webdriver():
                return all_data
                
            while (max_pages is None or page <= max_pages) and (max_items is None or len(all_data) < max_items):
                data = self.data_extractor.extract_page(page)
                all_data.extend(data)
                
                if not self.crawler._has_next_page():
                    break
                    
                page += 1
                self.logger.info(f"已爬取第 {page-1} 頁，目前資料量: {len(all_data)}")
                
        finally:
            self.crawler._close_webdriver()
            
        return all_data
    
    def _resume_crawl(self, **kwargs):
        """從中斷處恢復爬取"""
        last_state = self.crawler.state_manager.get_state()
        if not last_state:
            return self._normal_crawl(**kwargs)
            
        return self._position_crawl(
            start_page=last_state.get('current_page', 1),
            start_item_index=last_state.get('current_item_index', 0),
            **kwargs
        )
    
    def _position_crawl(self, start_page: int, start_item_index: int, **kwargs):
        """從指定位置開始爬取"""
        # ...類似實現...
