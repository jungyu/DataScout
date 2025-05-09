#!/usr/bin/env python3
"""
Nikkei Asia 爬蟲程式 - 使用 playwright_base 框架

這是一個使用 playwright_base 框架開發的爬蟲程式，用於爬取 Nikkei Asia 網站的新聞內容。
"""

import os
import json
import time
import random
import configparser
from datetime import datetime, date
from typing import List, Dict, Any, Optional
import logging
from pathlib import Path

# 導入 playwright_base 框架
from playwright_base import PlaywrightBase, setup_logger
from playwright_base.storage.storage_manager import StorageManager
from playwright_base.anti_detection.human_like import HumanLikeBehavior

# 設置日誌
logger = setup_logger(
    name="nikkei_scraper",
    log_file=f"logs/nikkei_scraper_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
)

# 獲取當前腳本所在目錄
SCRIPT_DIR = Path(__file__).parent.absolute()
CONFIG_DIR = SCRIPT_DIR / "config"
STORAGE_DIR = SCRIPT_DIR / "storage"

# 確保必要的目錄存在
STORAGE_DIR.mkdir(exist_ok=True)
(SCRIPT_DIR / "logs").mkdir(exist_ok=True)

class NikkeiScraper:
    """
    Nikkei Asia 爬蟲類
    基於 playwright_base 框架實現的爬蟲，用於爬取 Nikkei Asia 網站的新聞內容。
    """

    def __init__(self, config_file: str = "nikkei_config.json", credential_file: str = "credentials.ini"):
        """
        初始化 Nikkei 爬蟲

        參數:
            config_file: 配置檔案路徑
            credential_file: 登入憑證檔案路徑
        """
        # 載入配置
        config_path = CONFIG_DIR / config_file
        with open(config_path, "r", encoding="utf-8") as f:
            self.config = json.load(f)
        
        # 設置基本 URL
        self.base_url = self.config["site"]["base_url"]
        self.search_url = self.config["site"]["search_url"]

        # 初始化儲存路徑
        self.lists_file = STORAGE_DIR / Path(self.config["storage"]["lists_file"]).name
        self.articles_file = STORAGE_DIR / Path(self.config["storage"]["articles_file"]).name
        self.storage_file = STORAGE_DIR / Path(self.config["storage"]["storage_file"]).name
        self.results_file = STORAGE_DIR / Path(self.config["storage"]["results_file"]).name

        # 載入已存在的數據
        self.lists = self._load_json(self.lists_file)
        self.articles = self._load_json(self.articles_file)
        
        # 讀取帳號密碼
        credential_path = CONFIG_DIR / credential_file
        config_parser = configparser.ConfigParser()
        config_parser.read(credential_path)
        self.email = config_parser['login']['email']
        self.password = config_parser['login']['password']

        # 初始化爬蟲引擎
        self.crawler = None
        self.human_like = HumanLikeBehavior()
        self.storage_manager = StorageManager(str(STORAGE_DIR))

    def _load_json(self, filepath: Path) -> List[Dict[str, Any]]:
        """從 JSON 檔案加載數據"""
        if filepath.exists():
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        return []

    def _save_json(self, data: Any, filepath: Path) -> None:
        """保存數據到 JSON 檔案"""
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logger.info(f"已儲存數據至 {filepath}")

    def _build_query_string(self, params: Dict[str, str]) -> str:
        """構建查詢字符串"""
        return "&".join([f"{k}={v}" for k, v in params.items()])

    def init_crawler(self) -> None:
        """初始化爬蟲實例並處理登入"""
        browser_config = self.config["browser"]
        
        # 創建爬蟲實例
        self.crawler = PlaywrightBase(
            headless=browser_config["headless"],
            browser_type=browser_config["browser_type"],
            user_agent=browser_config["user_agent"],
            viewport=browser_config["viewport"],
            storage_state=str(self.storage_file) if self.storage_file.exists() else None
        )
        
        # 啟動瀏覽器
        self.crawler.start()
        
        # 啟用隱身模式
        self.crawler.enable_stealth_mode()
        
        # 如果不存在 storage_file，則需要登入
        if not self.storage_file.exists():
            self.login()

    def login(self) -> None:
        """登入 Nikkei 網站"""
        logger.info("自動登入 Nikkei 帳號...")
        
        # 訪問首頁
        self.crawler.goto(self.base_url, wait_until="domcontentloaded")
        
        # 點擊登入按鈕
        self.crawler.page.wait_for_selector('button[data-trackable="login-link"]', timeout=20000)
        self.crawler.page.click('button[data-trackable="login-link"]')
        
        # 切換到登入 iframe
        self.crawler.page.wait_for_selector('iframe[src*="auth.asia.nikkei.com/id/"]', timeout=20000)
        iframe_elem = self.crawler.page.query_selector('iframe[src*="auth.asia.nikkei.com/id/"]')
        login_frame = iframe_elem.content_frame()
        
        # 輸入郵箱
        login_frame.wait_for_selector('input#email-field', timeout=20000)
        login_frame.fill('input#email-field', self.email)
        login_frame.click('button[type="submit"].btn.prime')
        
        # 輸入密碼
        login_frame.wait_for_selector('input[type="password"]', timeout=20000)
        login_frame.fill('input[type="password"]', self.password)
        login_frame.click('button[type="submit"].btn.prime')
        
        # 等待頁面加載完成
        self.crawler.wait_for_load_state("networkidle")
        
        # 儲存 session
        logger.info("登入完成，儲存 session cookie...")
        self.crawler.save_storage(str(self.storage_file))

    def load_results(self) -> Dict[str, Any]:
        """載入已爬取的結果記錄"""
        today = date.today().isoformat()
        if self.results_file.exists():
            with open(self.results_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            if data.get("fetch_date") == today:
                return data
        # 若無檔案或非今日，重設
        return {"fetch_date": today, "records": []}

    def load_keywords(self) -> List[List[str]]:
        """載入關鍵詞列表"""
        keywords_path = CONFIG_DIR / "keywords.json"
        with open(keywords_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def scrape_all_keywords(self, max_pages: int = None) -> None:
        """爬取所有關鍵詞的搜尋結果"""
        if max_pages is None:
            max_pages = self.config["scraping"]["max_pages"]
        
        keywords_list = self.load_keywords()
        logger.info(f"開始爬取 {len(keywords_list)} 組關鍵詞")
        
        try:
            self.init_crawler()
            
            for keywords in keywords_list:
                query = ' '.join(keywords)
                logger.info(f"處理關鍵詞: {query}")
                self.scrape_search_results(keywords, max_pages)
                
                # 隨機延遲，避免頻繁搜尋
                delay = random.uniform(3, 6)
                logger.info(f"等待 {delay:.1f} 秒後處理下一組關鍵詞...")
                time.sleep(delay)
                
        finally:
            if self.crawler:
                self.crawler.close()

    def scrape_search_results(self, keywords: List[str], max_pages: int = 5) -> List[Dict[str, Any]]:
        """
        爬取關鍵詞搜尋結果
        
        參數:
            keywords: 關鍵詞列表
            max_pages: 最大爬取頁數
            
        返回:
            爬取的文章列表
        """
        if not self.crawler:
            self.init_crawler()
            
        results_record = self.load_results()
        selectors = self.config["selectors"]["search_results"]
        query = ' '.join(keywords)
        
        try:
            # 訪問搜尋頁面
            search_params = {"query": query}
            search_url = f"{self.search_url}?{self._build_query_string(search_params)}"
            logger.info(f"正在訪問搜尋頁面: {search_url}")
            
            self.crawler.goto(search_url, wait_until="domcontentloaded")
            self.crawler.wait_for_load_state("networkidle")
            
            current_page = 1
            while current_page <= max_pages:
                # 比對是否已爬過
                if any(r["keyword"] == keywords and r["page"] == current_page for r in results_record["records"]):
                    logger.info(f"已爬過 {query} 第 {current_page} 頁，略過")
                    current_page += 1
                    
                    # 點下一頁
                    next_button = self.crawler.page.query_selector(selectors["next_page"])
                    if next_button:
                        next_button.click()
                        self.crawler.wait_for_load_state("networkidle")
                        time.sleep(self.config["scraping"]["delay_between_pages"])
                    continue
                
                logger.info(f"正在爬取第 {current_page} 頁 關鍵字: {query}")
                
                # 模擬人類行為
                self.human_like.random_delay(1, 2)
                
                # 等待文章載入
                self.crawler.page.wait_for_selector(selectors["article"], timeout=30000)
                
                # 模擬人類滾動頁面
                self.human_like.scroll_page(self.crawler.page)
                
                # 獲取所有文章
                articles = self.crawler.page.query_selector_all(selectors["article"])
                logger.info(f"找到 {len(articles)} 篇文章")
                
                if not articles:
                    logger.warning("本頁未找到任何文章，可能已到達最後一頁")
                    break
                
                # 處理每一篇文章
                for idx, article in enumerate(articles, 1):
                    try:
                        title_element = article.query_selector(selectors["title"])
                        if title_element:
                            title = title_element.inner_text()
                            link = title_element.get_attribute("href")
                            url = self.base_url + link if link.startswith("/") else link
                            
                            category_element = article.query_selector(selectors["category"])
                            category = category_element.inner_text() if category_element else ""
                            
                            time_element = article.query_selector(selectors["publish_time"])
                            publish_time = time_element.inner_text() if time_element else ""
                            
                            description_element = article.query_selector(selectors["description"])
                            description = description_element.inner_text() if description_element else ""
                            
                            # 檢查是否已存在
                            exist = next((item for item in self.lists if item['url'] == url), None)
                            if not exist:
                                list_item = {
                                    "url": url,
                                    "title": title,
                                    "category": category,
                                    "publish_time": publish_time,
                                    "description": description,
                                    "content_fetched": False,
                                    "last_fetch_time": None
                                }
                                self.lists.append(list_item)
                                self._save_json(self.lists, self.lists_file)
                                logger.info(f"已儲存列表: {title}")
                    except Exception as e:
                        logger.error(f"處理文章時發生錯誤: {str(e)}")
                
                # 記錄本頁已爬取
                results_record["records"].append({"keyword": keywords, "page": current_page})
                self._save_json(results_record, self.results_file)
                
                # 檢查是否有下一頁
                next_button = self.crawler.page.query_selector(selectors["next_page"])
                if not next_button:
                    logger.info("未找到下一頁按鈕，可能已到達最後一頁")
                    break
                
                logger.info("點擊下一頁按鈕")
                next_button.click()
                self.crawler.wait_for_load_state("networkidle")
                time.sleep(self.config["scraping"]["delay_between_pages"])
                current_page += 1
                
            return self.lists
            
        except Exception as e:
            logger.error(f"爬取搜尋結果時發生錯誤: {str(e)}")
            return []

    def scrape_article_content(self, url: str) -> Optional[Dict[str, Any]]:
        """
        爬取單篇文章的內容
        
        參數:
            url: 文章URL
            
        返回:
            文章內容數據，若失敗則返回 None
        """
        if not self.crawler:
            self.init_crawler()
            
        selectors = self.config["selectors"]["article_detail"]
        
        try:
            # 訪問文章頁面
            logger.info(f"正在訪問文章頁面: {url}")
            self.crawler.goto(url, wait_until="domcontentloaded")
            
            # 嘗試等待頁面加載完成
            try:
                self.crawler.wait_for_load_state("networkidle")
            except Exception:
                logger.warning("頁面加載超時，但繼續執行...")
            
            # 自動關閉彈窗
            if self.config["scraping"]["auto_close_popups"]:
                try:
                    self.crawler.page.wait_for_selector(selectors["popup_close"], timeout=5000)
                    self.crawler.page.click(selectors["popup_close"])
                    logger.info("已自動關閉彈窗/廣告")
                except Exception:
                    logger.info("未偵測到彈窗/廣告，繼續解析內容")
            
            # 模擬人類滾動和閱讀行為
            self.human_like.scroll_page(self.crawler.page)
            
            # 等待文章內容載入
            self.crawler.page.wait_for_selector(selectors["wrapper"], timeout=30000)
            time.sleep(1)
            
            wrapper = self.crawler.page.query_selector(selectors["wrapper"])
            if not wrapper:
                logger.warning("無法找到文章內容")
                return None
            
            # 提取文章內容
            category_elem = wrapper.query_selector(selectors["category"])
            category = category_elem.inner_text() if category_elem else ""
            
            title_elem = wrapper.query_selector(selectors["title"])
            title = title_elem.inner_text() if title_elem else ""
            
            subtitle_elem = wrapper.query_selector(selectors["subtitle"])
            subtitle = subtitle_elem.inner_text() if subtitle_elem else ""
            
            image_elem = wrapper.query_selector(selectors["image"])
            image_url = image_elem.get_attribute("src") if image_elem else ""
            
            image_caption_elem = wrapper.query_selector(selectors["image_caption"])
            image_caption = image_caption_elem.inner_text() if image_caption_elem else ""
            
            author_elem = wrapper.query_selector(selectors["author"])
            author = author_elem.inner_text() if author_elem else ""
            
            publish_time_elem = wrapper.query_selector(selectors["publish_time"])
            publish_time = publish_time_elem.inner_text() if publish_time_elem else ""
            
            update_time_elem = wrapper.query_selector(selectors["update_time"])
            update_time = update_time_elem.inner_text() if update_time_elem else ""
            
            # 提取正文內容
            content_paras = wrapper.query_selector_all(selectors["content"])
            content = "\n".join([p.inner_text() for p in content_paras])
            
            # 建立文章數據
            article_data = {
                "url": url,
                "category": category,
                "title": title,
                "subtitle": subtitle,
                "image_url": image_url,
                "image_caption": image_caption,
                "author": author,
                "publish_time": publish_time,
                "update_time": update_time,
                "content": content,
                "scraped_at": datetime.now().isoformat()
            }
            
            # 儲存到文章列表
            self.articles.append(article_data)
            self._save_json(self.articles, self.articles_file)
            
            # 更新列表狀態
            for item in self.lists:
                if item['url'] == url:
                    item['content_fetched'] = True
                    item['last_fetch_time'] = datetime.now().isoformat()
            
            self._save_json(self.lists, self.lists_file)
            logger.info(f"已儲存文章: {title}")
            
            # 截圖保存
            screenshot_dir = STORAGE_DIR / "screenshots"
            screenshot_dir.mkdir(exist_ok=True)
            filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{url.split('/')[-1]}.png"
            self.crawler.screenshot(path=str(screenshot_dir / filename))
            
            return article_data
            
        except Exception as e:
            logger.error(f"爬取文章內容時發生錯誤: {str(e)}")
            return None

    def scrape_all_articles(self) -> None:
        """爬取所有未爬取的文章內容"""
        if not self.crawler:
            self.init_crawler()
        
        # 篩選未爬取的文章
        pending_articles = [item for item in self.lists if not item.get("content_fetched")]
        logger.info(f"找到 {len(pending_articles)} 篇待爬取文章")
        
        delay_range = self.config["scraping"]["delay_between_articles"]
        
        for idx, item in enumerate(pending_articles, 1):
            url = item["url"]
            logger.info(f"[{idx}/{len(pending_articles)}] 正在爬取文章: {item['title']}")
            
            self.scrape_article_content(url)
            
            # 隨機延遲
            if idx < len(pending_articles):
                sleep_time = random.randint(delay_range["min"], delay_range["max"])
                logger.info(f"等待 {sleep_time} 秒後進入下一篇...")
                time.sleep(sleep_time)

    def close(self) -> None:
        """關閉爬蟲實例"""
        if self.crawler:
            self.crawler.close()
            self.crawler = None


def main():
    """主函數"""
    try:
        logger.info("=== 開始執行 Nikkei Asia 爬蟲程式 ===")
        
        # 建立爬蟲實例
        scraper = NikkeiScraper()
        
        # 爬取搜尋結果
        try:
            logger.info("開始爬取搜尋結果...")
            scraper.scrape_all_keywords()
        except Exception as e:
            logger.error(f"爬取搜尋結果時發生錯誤: {str(e)}")
        
        # 爬取文章內容
        try:
            logger.info("開始爬取文章內容...")
            scraper.scrape_all_articles()
        except Exception as e:
            logger.error(f"爬取文章內容時發生錯誤: {str(e)}")
            
        logger.info("=== Nikkei Asia 爬蟲程式執行完成 ===")
        
    except Exception as e:
        logger.error(f"程式執行過程中發生錯誤: {str(e)}")
    finally:
        if scraper and hasattr(scraper, 'close'):
            scraper.close()


if __name__ == "__main__":
    main()