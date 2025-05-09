import configparser
from playwright.sync_api import sync_playwright, TimeoutError
import json
from datetime import datetime, date
import time
from typing import List, Dict, Any
import logging
import os
import random

# 設置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

LISTS_FILE = "nikkei_lists.json"
ARTICLES_FILE = "nikkei_articles.json"
STORAGE_FILE = "nikkei_storage.json"
RESULTS_FILE = "nikkei_results.json"

class NikkeiScraper:
    def __init__(self):
        self.base_url = "https://asia.nikkei.com"
        self.search_url = f"{self.base_url}/search"
        self.results = []
        self.lists = self.load_json(LISTS_FILE)
        self.articles = self.load_json(ARTICLES_FILE)
        # 讀取帳號密碼
        config = configparser.ConfigParser()
        config.read('config.ini')
        self.email = config['login']['email']
        self.password = config['login']['password']

    def load_json(self, filename):
        if os.path.exists(filename):
            with open(filename, "r", encoding="utf-8") as f:
                return json.load(f)
        return []

    def save_json(self, data, filename):
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def login(self, page, context):
        logger.info("自動登入 Nikkei 帳號...")
        page.goto(self.base_url, wait_until="domcontentloaded")
        page.wait_for_selector('button[data-trackable="login-link"]', timeout=20000)
        page.click('button[data-trackable="login-link"]')
        page.wait_for_selector('iframe[src*="auth.asia.nikkei.com/id/"]', timeout=20000)
        iframe_elem = page.query_selector('iframe[src*="auth.asia.nikkei.com/id/"]')
        login_frame = iframe_elem.content_frame()
        login_frame.wait_for_selector('input#email-field', timeout=20000)
        login_frame.fill('input#email-field', self.email)
        login_frame.click('button[type="submit"].btn.prime')
        login_frame.wait_for_selector('input[type="password"]', timeout=20000)
        login_frame.fill('input[type="password"]', self.password)
        login_frame.click('button[type="submit"].btn.prime')
        page.wait_for_load_state("networkidle")
        logger.info("登入完成，儲存 session cookie...")
        context.storage_state(path=STORAGE_FILE)

    def load_results(self):
        today = date.today().isoformat()
        if os.path.exists(RESULTS_FILE):
            with open(RESULTS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            if data.get("fetch_date") == today:
                return data
        # 若無檔案或非今日，重設
        return {"fetch_date": today, "records": []}

    def save_results(self, results):
        with open(RESULTS_FILE, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        logger.info(f"已更新 {RESULTS_FILE}")

    def load_keywords(self):
        with open("keywords.json", "r", encoding="utf-8") as f:
            return json.load(f)

    def scrape_all_keywords(self, max_pages=5):
        keywords_list = self.load_keywords()
        for keywords in keywords_list:
            query = ' '.join(keywords)
            self.scrape_search_results(keywords, max_pages)

    def scrape_search_results(self, keywords, max_pages: int = 5) -> List[Dict[str, Any]]:
        try:
            results_record = self.load_results()
            today = date.today().isoformat()
            with sync_playwright() as p:
                logger.info("啟動瀏覽器...")
                browser = p.chromium.launch(
                    headless=False,
                    channel="chrome",
                    args=['--start-maximized']
                )
                # 優先載入 session
                if os.path.exists(STORAGE_FILE):
                    context = browser.new_context(
                        storage_state=STORAGE_FILE,
                        viewport={'width': 1920, 'height': 1080},
                        user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'
                    )
                    page = context.new_page()
                    logger.info("已載入 session cookie，嘗試免登入...")
                else:
                    context = browser.new_context(
                        viewport={'width': 1920, 'height': 1080},
                        user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'
                    )
                    page = context.new_page()
                    self.login(page, context)
                # 訪問搜尋頁面
                query = ' '.join(keywords)
                search_params = {"query": query}
                search_url = f"{self.search_url}?{self._build_query_string(search_params)}"
                logger.info(f"正在訪問搜尋頁面: {search_url}")
                try:
                    response = page.goto(search_url, wait_until="domcontentloaded", timeout=60000)
                    if response:
                        logger.info(f"頁面狀態碼: {response.status}")
                    page.wait_for_load_state("networkidle", timeout=60000)
                except TimeoutError:
                    logger.warning("頁面加載超時，但繼續執行...")
                current_page = 1
                while current_page <= max_pages:
                    # 比對是否已爬過
                    if any(r["keyword"] == keywords and r["page"] == current_page for r in results_record["records"]):
                        logger.info(f"已爬過 {keywords} 第 {current_page} 頁，略過")
                        current_page += 1
                        # 點下一頁
                        next_button = page.query_selector("li.Pagination_paginationNext__a_qek a")
                        if next_button:
                            next_button.click()
                            page.wait_for_load_state("networkidle", timeout=30000)
                            time.sleep(3)
                        continue
                    logger.info(f"正在爬取第 {current_page} 頁 關鍵字: {keywords}")
                    try:
                        page.wait_for_selector("article.ArticleSearchResult_article__UxvjT", timeout=30000)
                        time.sleep(2)
                        articles = page.query_selector_all("article.ArticleSearchResult_article__UxvjT")
                        logger.info(f"找到 {len(articles)} 篇文章")
                        if not articles:
                            logger.warning("本頁未找到任何文章，可能已到達最後一頁")
                            break
                        for idx, article in enumerate(articles, 1):
                            try:
                                title_element = article.query_selector("h2.ArticleSearchResult_headline__y2pzy a")
                                link_element = title_element
                                if title_element and link_element:
                                    title = title_element.inner_text()
                                    link = link_element.get_attribute("href")
                                    url = self.base_url + link if link.startswith("/") else link
                                    category_element = article.query_selector("h4.ArticleSearchResult_tag__JOai8 a")
                                    category = category_element.inner_text() if category_element else ""
                                    time_element = article.query_selector("span.ArticleSearchResult_articleTimestamp__D1E9L")
                                    publish_time = time_element.inner_text() if time_element else ""
                                    description_element = article.query_selector("p.ArticleSearchResult_description__X28UL")
                                    description = description_element.inner_text() if description_element else ""
                                    now = datetime.now().isoformat()
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
                                        self.save_json(self.lists, LISTS_FILE)
                                    logger.info(f"已儲存列表: {title}")
                            except Exception as e:
                                logger.error(f"處理文章時發生錯誤: {str(e)}")
                        # 記錄本頁已爬取
                        results_record["records"].append({"keyword": keywords, "page": current_page})
                        self.save_results(results_record)
                        next_button = page.query_selector("li.Pagination_paginationNext__a_qek a")
                        if not next_button:
                            logger.info("未找到下一頁按鈕，可能已到達最後一頁")
                            break
                        logger.info("點擊下一頁按鈕")
                        next_button.click()
                        page.wait_for_load_state("networkidle", timeout=30000)
                        time.sleep(3)
                        current_page += 1
                    except Exception as e:
                        logger.error(f"處理頁面時發生錯誤: {str(e)}")
                        break
                logger.info("關閉瀏覽器")
                browser.close()
                return self.lists
        except Exception as e:
            logger.error(f"爬蟲執行過程中發生錯誤: {str(e)}")
            return []

    def scrape_article_content(self, url: str) -> Dict[str, Any]:
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=False,
                channel="chrome",
                args=['--start-maximized']
            )
            context = browser.new_context(
                storage_state=STORAGE_FILE,
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'
            )
            page = context.new_page()
            logger.info(f"正在訪問文章頁面: {url}")
            try:
                response = page.goto(url, wait_until="domcontentloaded", timeout=60000)
                if response:
                    logger.info(f"文章頁面狀態碼: {response.status}")
                page.wait_for_load_state("networkidle", timeout=60000)
            except TimeoutError:
                logger.warning("文章頁面加載超時，但繼續執行...")

            # 新增：自動關閉 paywall/modal 廣告彈窗
            try:
                page.wait_for_selector('button.tp-close', timeout=5000)
                page.click('button.tp-close')
                logger.info("已自動關閉彈窗/廣告")
            except Exception:
                logger.info("未偵測到彈窗/廣告，繼續解析內容")

            page.wait_for_selector("div.NewsArticleWrapper_newsArticleWrapper__5WTIa", timeout=30000)
            time.sleep(2)
            wrapper = page.query_selector("div.NewsArticleWrapper_newsArticleWrapper__5WTIa")
            if not wrapper:
                logger.warning("無法找到文章內容")
                return None
            # 主分類
            category = wrapper.query_selector(".NewsArticleHeader_newsArticleTagContainer__9oA_J a")
            category = category.inner_text() if category else ""
            # 標題
            title = wrapper.query_selector("h1.article-header__title")
            title = title.inner_text() if title else ""
            # 副標
            subtitle = wrapper.query_selector("p.NewsArticleHeader_newsArticleHeaderSubtitle__ZlvPp")
            subtitle = subtitle.inner_text() if subtitle else ""
            # 主圖
            image = wrapper.query_selector('div[data-trackable="image-main"] img')
            image_url = image.get_attribute("src") if image else ""
            # 主圖說明
            image_caption = wrapper.query_selector("p.NewsArticleCaption_newsArticleCaption__fxo8v")
            image_caption = image_caption.inner_text() if image_caption else ""
            # 作者
            author = wrapper.query_selector("div.NewsArticleDetails_newsArticleDetailsByline__VOUu6")
            author = author.inner_text() if author else ""
            # 發佈時間
            publish_time = wrapper.query_selector('div[data-testid="timestamp"].ArticleTimestamp_articleTimestampCreated__WDqHG span')
            publish_time = publish_time.inner_text() if publish_time else ""
            # 更新時間
            update_time = wrapper.query_selector('div[data-testid="timestamp"].ArticleTimestamp_articleTimestampUpdated__3hUKK span')
            update_time = update_time.inner_text() if update_time else ""
            # 內文
            content_paras = wrapper.query_selector_all('div#article-body-preview p')
            content = "\n".join([p.inner_text() for p in content_paras])
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
            # 儲存
            self.articles.append(article_data)
            self.save_json(self.articles, ARTICLES_FILE)
            # 更新 lists 狀態
            for item in self.lists:
                if item['url'] == url:
                    item['content_fetched'] = True
                    item['last_fetch_time'] = datetime.now().isoformat()
            self.save_json(self.lists, LISTS_FILE)
            browser.close()
            logger.info(f"已儲存文章: {title}")
            return article_data

    def _build_query_string(self, params: Dict[str, str]) -> str:
        return "&".join([f"{k}={v}" for k, v in params.items()])

    def scrape_all_articles(self):
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=False,
                channel="chrome",
                args=['--start-maximized']
            )
            context = browser.new_context(
                storage_state=STORAGE_FILE,
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'
            )
            page = context.new_page()
            for item in self.lists:
                if item.get("content_fetched"):
                    continue
                url = item["url"]
                logger.info(f"正在訪問文章頁面: {url}")
                try:
                    response = page.goto(url, wait_until="domcontentloaded", timeout=60000)
                    if response:
                        logger.info(f"文章頁面狀態碼: {response.status}")
                    page.wait_for_load_state("networkidle", timeout=60000)
                except TimeoutError:
                    logger.warning("文章頁面加載超時，但繼續執行...")
                    # 關閉彈窗
                    try:
                        page.wait_for_selector('button.tp-close', timeout=5000)
                        page.click('button.tp-close')
                        logger.info("已自動關閉彈窗/廣告")
                    except Exception:
                        logger.info("未偵測到彈窗/廣告，繼續解析內容")
                    page.wait_for_selector("div.NewsArticleWrapper_newsArticleWrapper__5WTIa", timeout=30000)
                    time.sleep(2)
                    wrapper = page.query_selector("div.NewsArticleWrapper_newsArticleWrapper__5WTIa")
                    if not wrapper:
                        logger.warning("無法找到文章內容")
                        continue
                    # 主分類
                    category = wrapper.query_selector(".NewsArticleHeader_newsArticleTagContainer__9oA_J a")
                    category = category.inner_text() if category else ""
                    # 標題
                    title = wrapper.query_selector("h1.article-header__title")
                    title = title.inner_text() if title else ""
                    # 副標
                    subtitle = wrapper.query_selector("p.NewsArticleHeader_newsArticleHeaderSubtitle__ZlvPp")
                    subtitle = subtitle.inner_text() if subtitle else ""
                    # 主圖
                    image = wrapper.query_selector('div[data-trackable="image-main"] img')
                    image_url = image.get_attribute("src") if image else ""
                    # 主圖說明
                    image_caption = wrapper.query_selector("p.NewsArticleCaption_newsArticleCaption__fxo8v")
                    image_caption = image_caption.inner_text() if image_caption else ""
                    # 作者
                    author = wrapper.query_selector("div.NewsArticleDetails_newsArticleDetailsByline__VOUu6")
                    author = author.inner_text() if author else ""
                    # 發佈時間
                    publish_time = wrapper.query_selector('div[data-testid="timestamp"].ArticleTimestamp_articleTimestampCreated__WDqHG span')
                    publish_time = publish_time.inner_text() if publish_time else ""
                    # 更新時間
                    update_time = wrapper.query_selector('div[data-testid="timestamp"].ArticleTimestamp_articleTimestampUpdated__3hUKK span')
                    update_time = update_time.inner_text() if update_time else ""
                    # 內文
                    content_paras = wrapper.query_selector_all('div#article-body-preview p')
                    content = "\n".join([p.inner_text() for p in content_paras])
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
                    self.articles.append(article_data)
                    self.save_json(self.articles, ARTICLES_FILE)
                    # 立即更新 lists 狀態
                    for l in self.lists:
                        if l['url'] == url:
                            l['content_fetched'] = True
                            l['last_fetch_time'] = datetime.now().isoformat()
                    self.save_json(self.lists, LISTS_FILE)
                    logger.info(f"已儲存文章: {title}")
                    # 隨機等待 5~8 秒
                    sleep_time = random.randint(5, 8)
                    logger.info(f"等待 {sleep_time} 秒後進入下一篇...")
                    time.sleep(sleep_time)
            browser.close()

def main():
    try:
        logger.info("開始執行爬蟲程式")
        scraper = NikkeiScraper()
        scraper.scrape_all_keywords(max_pages=5)
        scraper.scrape_all_articles()
        logger.info("全部完成！")
    except Exception as e:
        logger.error(f"程式執行過程中發生錯誤: {str(e)}")

if __name__ == "__main__":
    main() 