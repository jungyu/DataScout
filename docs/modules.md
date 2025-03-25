# 爬蟲系統模組說明

## 簡介

本文檔詳細說明了爬蟲系統的各個模組，包括其功能、設計原理、關鍵類別與方法以及使用示例。本系統採用高度模組化設計，各模組之間有清晰的界限和定義良好的接口，便於維護與擴展。

## 核心模組 (src/core/)

核心模組是爬蟲系統的中樞，負責協調各個功能模組的工作。

### template_crawler.py

這是模板化爬蟲的核心類，負責解析爬蟲模板並據此執行爬取流程。

**主要功能**:
- 解析 JSON 格式的爬蟲模板
- 根據模板定義的選擇器和參數執行爬取
- 處理分頁和列表項目的迭代
- 收集並結構化爬取結果

**關鍵類別和方法**:
```python
class TemplateCrawler:
    def __init__(self, template_file, config_file=None, webdriver_manager=None, state_manager=None):
        """
        初始化模板爬蟲
        
        Args:
            template_file: 模板文件路徑
            config_file: 配置文件路徑
            webdriver_manager: WebDriver管理器實例
            state_manager: 狀態管理器實例
        """
        
    def load_template(self, template_file):
        """加載並解析模板文件"""
        
    def crawl(self, max_pages=None, max_items=None):
        """
        執行爬蟲
        
        Args:
            max_pages: 最大爬取頁數
            max_items: 最大爬取項目數
            
        Returns:
            list: 爬取的數據
        """
        
    def resume_crawl(self):
        """從上次中斷點恢復爬取"""
        
    def _process_list_page(self):
        """處理列表頁面"""
        
    def _process_detail_page(self, detail_url, list_item_data):
        """處理詳情頁面"""
        
    def _extract_data(self, element, field_config):
        """根據配置提取數據"""
```

### webdriver_manager.py

WebDriver 管理器負責創建、配置和管理 Selenium WebDriver 實例，並提供反爬蟲防護功能。

**主要功能**:
- 初始化和配置 WebDriver
- 管理 WebDriver 生命週期
- 實現頁面加載和瀏覽控制
- 整合反爬蟲機制

**關鍵類別和方法**:
```python
class WebDriverManager:
    def __init__(self, config=None, anti_detection_manager=None):
        """
        初始化WebDriver管理器
        
        Args:
            config: 配置字典或配置文件路徑
            anti_detection_manager: 反爬蟲管理器實例
        """
        
    def initialize_driver(self):
        """初始化WebDriver"""
        
    def quit_driver(self):
        """關閉WebDriver"""
        
    def get_page(self, url, wait_for=None, timeout=10):
        """
        獲取頁面
        
        Args:
            url: 目標URL
            wait_for: 等待特定元素出現
            timeout: 超時時間(秒)
            
        Returns:
            bool: 是否成功獲取頁面
        """
        
    def wait_for_element(self, selector, by=By.CSS_SELECTOR, timeout=10, condition=EC.presence_of_element_located):
        """
        等待元素出現
        
        Args:
            selector: 元素選擇器
            by: 選擇器類型
            timeout: 超時時間(秒)
            condition: 等待條件
            
        Returns:
            WebElement: 找到的元素，未找到則返回None
        """
        
    def save_cookies(self, file_path=None):
        """保存Cookies到文件"""
        
    def load_cookies(self, file_path=None):
        """從文件加載Cookies"""
```

### crawler_engine.py

爬蟲引擎是系統的主要協調者，負責整合各個組件並執行爬蟲任務。

**主要功能**:
- 協調各組件的工作流程
- 提供高層次的爬蟲操作接口
- 處理異常情況和重試邏輯
- 管理爬蟲任務和結果

**關鍵類別和方法**:
```python
class CrawlerEngine:
    def __init__(self, config_file=None):
        """
        初始化爬蟲引擎
        
        Args:
            config_file: 配置文件路徑
        """
        
    def create_template_crawler(self, template_file):
        """
        創建模板爬蟲實例
        
        Args:
            template_file: 模板文件路徑
            
        Returns:
            TemplateCrawler: 模板爬蟲實例
        """
        
    def run_crawler(self, crawler, **kwargs):
        """
        運行爬蟲
        
        Args:
            crawler: 爬蟲實例
            **kwargs: 其他參數
            
        Returns:
            list: 爬取的數據
        """
        
    def resume_crawler(self, crawler_id=None):
        """
        恢復爬蟲任務
        
        Args:
            crawler_id: 爬蟲任務ID
            
        Returns:
            list: 爬取的數據
        """
        
    def persist_data(self, data, destination="all"):
        """
        持久化數據
        
        Args:
            data: 爬取的數據
            destination: 目標存儲位置
        """
```

## 工具模組 (src/utils/)

工具模組提供各種輔助功能，支援系統的其他部分。

### config_loader.py

配置加載工具負責安全地加載和管理配置文件，處理敏感信息。

**主要功能**:
- 加載 JSON 配置文件
- 解密和處理敏感信息
- 合併和覆蓋配置選項
- 驗證配置有效性

**關鍵類別和方法**:
```python
class ConfigLoader:
    def __init__(self, config_file=None, config_dict=None):
        """
        初始化配置加載器
        
        Args:
            config_file: 配置文件路徑
            config_dict: 配置字典
        """
        
    def load(self, config_file=None):
        """
        加載配置文件
        
        Args:
            config_file: 配置文件路徑
            
        Returns:
            dict: 加載的配置
        """
        
    def merge(self, override_config):
        """
        合併配置
        
        Args:
            override_config: 覆蓋配置
            
        Returns:
            dict: 合併後的配置
        """
        
    def get(self, key, default=None):
        """
        獲取配置值
        
        Args:
            key: 配置鍵
            default: 默認值
            
        Returns:
            object: 配置值
        """
        
    def save(self, file_path=None):
        """
        保存配置到文件
        
        Args:
            file_path: 文件路徑
        """
```

### cookie_manager.py

Cookie 管理工具負責管理 Cookie 的保存、載入和更新。

**主要功能**:
- 保存和加載 Cookies
- 管理 Cookie 有效期
- 提供 Cookie 操作接口
- 支持多域名 Cookie 管理

**關鍵類別和方法**:
```python
class CookieManager:
    def __init__(self, base_dir="cookies"):
        """
        初始化Cookie管理器
        
        Args:
            base_dir: Cookie保存的基礎目錄
        """
        
    def save_cookies(self, driver, domain=None):
        """
        保存WebDriver的Cookies
        
        Args:
            driver: WebDriver實例
            domain: 網站域名
            
        Returns:
            str: Cookie文件路徑
        """
        
    def load_cookies(self, driver, domain=None):
        """
        載入Cookies到WebDriver
        
        Args:
            driver: WebDriver實例
            domain: 網站域名
            
        Returns:
            bool: 是否成功載入
        """
        
    def get_cookie_file(self, domain):
        """
        獲取Cookie文件路徑
        
        Args:
            domain: 網站域名
            
        Returns:
            str: Cookie文件路徑
        """
        
    def clear_cookies(self, domain=None):
        """
        清除Cookie
        
        Args:
            domain: 網站域名，None表示清除所有
        """
```

### error_handler.py

錯誤處理工具提供統一的錯誤處理機制，包括重試邏輯。

**主要功能**:
- 處理常見爬蟲錯誤
- 實現指數退避重試機制
- 記錄錯誤信息和統計
- 提供異常處理裝飾器

**關鍵類別和方法**:
```python
class ErrorHandler:
    def __init__(self, logger=None):
        """
        初始化錯誤處理器
        
        Args:
            logger: 日誌器實例
        """
        
    def retry(self, func, max_retries=3, retry_exceptions=(Exception,), 
              backoff_factor=2, initial_wait=1, on_retry=None):
        """
        重試執行函數
        
        Args:
            func: 要執行的函數
            max_retries: 最大重試次數
            retry_exceptions: 需要重試的異常類型
            backoff_factor: 退避係數
            initial_wait: 初始等待時間
            on_retry: 重試前調用的函數
            
        Returns:
            object: 函數返回值
        """
        
    def handle_error(self, error, context=None):
        """
        處理錯誤
        
        Args:
            error: 錯誤實例
            context: 錯誤上下文
            
        Returns:
            bool: 是否成功處理了錯誤
        """
```

### logger.py

日誌工具提供統一的日誌記錄功能。

**主要功能**:
- 配置並管理日誌系統
- 提供多級別日誌記錄
- 支持多種輸出目標
- 格式化日誌信息

**關鍵類別和方法**:
```python
class LoggerManager:
    def __init__(self, name="crawler", level="INFO", log_file=None, console_output=True):
        """
        初始化日誌管理器
        
        Args:
            name: 日誌器名稱
            level: 日誌級別
            log_file: 日誌文件路徑
            console_output: 是否輸出到控制台
        """
        
    def get_logger(self):
        """
        獲取日誌器實例
        
        Returns:
            Logger: 日誌器實例
        """
        
    def set_level(self, level):
        """
        設置日誌級別
        
        Args:
            level: 日誌級別
        """
        
    def add_file_handler(self, log_file, level=None):
        """
        添加文件處理器
        
        Args:
            log_file: 日誌文件路徑
            level: 處理器的日誌級別
        """
```

## 反爬蟲模組 (src/anti_detection/)

反爬蟲模組用於檢測和應對各種反爬蟲機制。

### anti_detection_manager.py

反爬蟲管理器是處理反爬蟲策略的核心組件。

**主要功能**:
- 實現反爬蟲防禦策略
- 檢測網站的反爬蟲機制
- 修改 WebDriver 特徵
- 模擬真實用戶行為

**關鍵類別和方法**:
```python
class AntiDetectionManager:
    def __init__(self, config_file=None, config_dict=None):
        """
        初始化反爬蟲管理器
        
        Args:
            config_file: 配置文件路徑
            config_dict: 配置字典
        """
        
    def setup_webdriver(self, driver):
        """
        配置WebDriver的反爬蟲功能
        
        Args:
            driver: WebDriver實例
            
        Returns:
            WebDriver: 配置好的WebDriver
        """
        
    def modify_webdriver_properties(self, driver):
        """修改WebDriver的特徵屬性"""
        
    def randomize_user_agent(self):
        """
        隨機生成User-Agent
        
        Returns:
            str: User-Agent字串
        """
        
    def get_proxy(self):
        """
        獲取代理伺服器
        
        Returns:
            str: 代理伺服器地址
        """
        
    def detect_anti_crawling(self, driver):
        """
        檢測網站是否啟用了反爬蟲機制
        
        Args:
            driver: WebDriver實例
            
        Returns:
            bool: 是否檢測到反爬蟲
        """
        
    def simulate_human_behavior(self, driver, action_count=3):
        """
        模擬人類行為
        
        Args:
            driver: WebDriver實例
            action_count: 模擬動作次數
        """
```

### stealth_scripts/browser_fp.js

瀏覽器指紋修改腳本，用於隱藏爬蟲的特徵。

**主要功能**:
- 修改 Navigator 屬性
- 覆蓋 WebDriver 檢測函數
- 修改 Canvas/WebGL 指紋
- 修改硬件指紋信息

**使用示例**:
```python
from src.anti_detection.anti_detection_manager import AntiDetectionManager
from selenium import webdriver

# 初始化管理器和WebDriver
anti_detection = AntiDetectionManager()
driver = webdriver.Chrome()

# 註入指紋修改腳本
with open("src/anti_detection/stealth_scripts/browser_fp.js", "r") as f:
    js_script = f.read()
    driver.execute_script(js_script)

# 或者使用管理器的方法自動應用
anti_detection.setup_webdriver(driver)
```

## 驗證碼處理模組 (src/captcha/)

驗證碼處理模組用於處理各種類型的驗證碼。

### captcha_manager.py

驗證碼管理器協調各類驗證碼解決器的工作。

**主要功能**:
- 檢測頁面上的驗證碼類型
- 協調不同的驗證碼解決器
- 管理驗證碼解決的重試機制
- 記錄解決結果和統計信息

**關鍵類別和方法**:
```python
class CaptchaManager:
    def __init__(self, driver, config_path=None):
        """
        初始化驗證碼管理器
        
        Args:
            driver: WebDriver實例
            config_path: 配置文件路徑
        """
        
    def detect_and_solve(self):
        """
        檢測並解決頁面上的驗證碼
        
        Returns:
            bool: 是否成功解決
        """
        
    def solve_specific(self, captcha_type):
        """
        解決特定類型的驗證碼
        
        Args:
            captcha_type: 驗證碼類型
            
        Returns:
            bool: 是否成功解決
        """
```

### solvers/base_solver.py

基礎驗證碼解決器抽象類，定義了所有驗證碼解決器的通用介面。

**主要功能**:
- 提供標準化的驗證碼解決介面
- 處理通用的驗證碼處理邏輯
- 提供統計和記錄功能

**關鍵類別和方法**:
```python
class BaseCaptchaSolver(ABC):
    def __init__(self, driver, config=None):
        """
        初始化解決器
        
        Args:
            driver: WebDriver實例
            config: 配置選項
        """
        
    @abstractmethod
    def detect(self):
        """
        檢測頁面上是否存在此類型的驗證碼
        
        Returns:
            bool: 是否檢測到驗證碼
        """
        
    @abstractmethod
    def solve(self):
        """
        解決驗證碼
        
        Returns:
            bool: 驗證碼是否成功解決
        """
        
    def report_result(self, success):
        """
        報告驗證碼解決結果
        
        Args:
            success: 是否成功解決
        """
        
    def save_sample(self, data, success=False):
        """
        保存驗證碼樣本
        
        Args:
            data: 驗證碼數據
            success: 是否為成功解決的樣本
        """
```

### solvers/text_solver.py, slider_solver.py, etc.

各類驗證碼解決器，繼承自基礎解決器，實現特定類型驗證碼的解決策略。

**關鍵類別和方法**:
```python
class TextCaptchaSolver(BaseCaptchaSolver):
    """文字驗證碼解決器"""
    
    def detect(self):
        """檢測文字驗證碼"""
        
    def solve(self):
        """解決文字驗證碼"""

class SliderCaptchaSolver(BaseCaptchaSolver):
    """滑塊驗證碼解決器"""
    
    def detect(self):
        """檢測滑塊驗證碼"""
        
    def solve(self):
        """解決滑塊驗證碼"""
        
    def _calculate_slide_distance(self):
        """計算滑動距離"""
        
    def _perform_slide(self, slider_button, distance):
        """執行滑動操作"""
```

## 狀態管理模組 (src/state/)

狀態管理模組負責管理爬蟲的狀態，支持任務的中斷和恢復。

### crawler_state_manager.py

爬蟲狀態管理器負責記錄和管理爬蟲任務的狀態。

**主要功能**:
- 保存爬蟲運行狀態
- 恢復中斷的爬蟲任務
- 管理爬蟲的中斷點
- 處理狀態持久化

**關鍵類別和方法**:
```python
class CrawlerStateManager:
    def __init__(self, storage_manager=None, base_dir="states"):
        """
        初始化爬蟲狀態管理器
        
        Args:
            storage_manager: 儲存管理器實例
            base_dir: 狀態文件基礎目錄
        """
        
    def save_state(self, crawler_id, state_data):
        """
        保存爬蟲狀態
        
        Args:
            crawler_id: 爬蟲ID
            state_data: 狀態數據
            
        Returns:
            bool: 是否成功保存
        """
        
    def load_state(self, crawler_id):
        """
        加載爬蟲狀態
        
        Args:
            crawler_id: 爬蟲ID
            
        Returns:
            dict: 狀態數據
        """
        
    def clear_state(self, crawler_id):
        """
        清除爬蟲狀態
        
        Args:
            crawler_id: 爬蟲ID
        """
        
    def backup_state(self, crawler_id):
        """
        備份爬蟲狀態
        
        Args:
            crawler_id: 爬蟲ID
            
        Returns:
            str: 備份文件路徑
        """
```

### multi_storage.py

多重儲存機制用於提高狀態儲存的可靠性，支持多種儲存方式。

**主要功能**:
- 支持多種儲存方式
- 實現冗餘儲存提高可靠性
- 同步多個儲存位置的數據
- 處理儲存衝突和恢復

**使用示例**:

以下是一個簡單的使用範例，展示如何使用 MultiStorageManager：

1. 首先初始化管理器
2. 添加不同的儲存實例（例如本地儲存和MongoDB）
3. 使用管理器進行數據的保存和讀取
4. 需要時可以同步不同儲存位置的數據

詳細的實作方式請參考 `src/state/multi_storage.py` 文件。

## 數據持久化模組 (src/persistence/)

數據持久化模組負責將爬取的數據持久化到各種存儲位置。

### data_persistence_manager.py

數據持久化管理器負責協調各種數據存儲方式。

**主要功能**:
- 管理多種數據存儲方式
- 提供統一的數據操作介面
- 處理數據格式轉換
- 支持數據同步和備份

**關鍵類別和方法**:
```python
class DataPersistenceManager:
    def __init__(self, config=None):
        """
        初始化數據持久化管理器
        
        Args:
            config: 配置字典或配置文件路徑
        """
        
    def add_handler(self, handler, name=None):
        """
        添加持久化處理器
        
        Args:
            handler: 處理器實例
            name: 處理器名稱
        """
        
    def save_data(self, data, handler_name=None):
        """
        保存數據
        
        Args:
            data: 要保存的數據
            handler_name: 處理器名稱（None表示所有處理器）
            
        Returns:
            bool: 是否成功保存
        """
        
    def load_data(self, query, handler_name=None):
        """
        加載數據
        
        Args:
            query: 查詢條件
            handler_name: 處理器名稱
            
        Returns:
            list: 加載的數據
        """
        
    def update_data(self, query, update_data, handler_name=None):
        """
        更新數據
        
        Args:
            query: 查詢條件
            update_data: 更新的數據
            handler_name: 處理器名稱
            
        Returns:
            bool: 是否成功更新
        """
        
    def delete_data(self, query, handler_name=None):
        """
        刪除數據
        
        Args:
            query: 查詢條件
            handler_name: 處理器名稱
            
        Returns:
            bool: 是否成功刪除
        """
        
    def sync_data(self, source_handler, target_handler, query=None):
        """
        同步數據
        
        Args:
            source_handler: 源處理器
            target_handler: 目標處理器
            query: 同步的數據範圍
            
        Returns:
            int: 同步的數據數量
        """
```

## 整合與使用

各模組之間的協作可以通過以下方式進行整合：

### main.py

系統主入口，整合各個模組並執行爬蟲任務。

```python
import os
import argparse
import json
from datetime import datetime

from src.core.crawler_engine import CrawlerEngine
from src.utils.logger import LoggerManager
from src.utils.config_loader import ConfigLoader

def main():
    # 解析命令行參數
    parser = argparse.ArgumentParser(description="網站爬蟲工具")
    parser.add_argument("-t", "--template", required=True, help="爬蟲模板文件路徑")
    parser.add_argument("-c", "--config", default="config/config.json", help="配置文件路徑")
    parser.add_argument("-p", "--pages", type=int, help="最大爬取頁數")
    parser.add_argument("-i", "--items", type=int, help="最大爬取項目數")
    parser.add_argument("-r", "--resume", action="store_true", help="從中斷點恢復爬取")
    parser.add_argument("-o", "--output", help="輸出文件路徑")
    args = parser.parse_args()
    
    # 初始化日誌管理器
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, f"crawler_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
    logger_manager = LoggerManager(name="crawler", level="INFO", log_file=log_file)
    logger = logger_manager.get_logger()
    
    # 加載配置
    config = ConfigLoader(args.config)
    
    # 創建爬蟲引擎
    engine = CrawlerEngine(args.config)
    
    try:
        # 決定是否從中斷點恢復
        if args.resume:
            logger.info(f"從中斷點恢復爬取: {args.template}")
            crawler_id = os.path.basename(args.template).split('.')[0]
            data = engine.resume_crawler(crawler_id)
        else:
            logger.info(f"開始爬取: {args.template}")
            crawler = engine.create_template_crawler(args.template)
            data = engine.run_crawler(
                crawler, 
                max_pages=args.pages, 
                max_items=args.items
            )
        
        # 持久化數據
        if data:
            logger.info(f"爬取完成，共獲取 {len(data)} 筆資料")
            
            # 保存到指定輸出文件
            if args.output:
                output_dir = os.path.dirname(args.output)
                if output_dir and not os.path.exists(output_dir):
                    os.makedirs(output_dir, exist_ok=True)
                    
                with open(args.output, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                logger.info(f"數據已保存到: {args.output}")
            
            # 使用持久化管理器保存
            engine.persist_data(data)
            
    except Exception as e:
        logger.error(f"爬蟲執行錯誤: {str(e)}", exc_info=True)
        raise  # 向上層拋出異常，確保錯誤被正確處理
    
    finally:
        # 清理資源
        try:
            webdriver_manager.quit_driver()
        except Exception as cleanup_error:
            logger.error(f"清理資源時發生錯誤: {str(cleanup_error)}")
        
    return 0

if __name__ == "__main__":
    exit(main())
```

### 模板集成示例

以下是一個完整的爬蟲任務示例，展示了如何將各個模組集成起來使用：

```python
# 導入所需模組
from src.core.webdriver_manager import WebDriverManager
from src.anti_detection.anti_detection_manager import AntiDetectionManager
from src.captcha.captcha_manager import CaptchaManager
from src.core.template_crawler import TemplateCrawler
from src.state.crawler_state_manager import CrawlerStateManager
from src.persistence.data_persistence_manager import DataPersistenceManager
from src.utils.logger import LoggerManager

# 初始化日誌
logger_manager = LoggerManager(name="crawler_example", log_file="logs/example.log")
logger = logger_manager.get_logger()

try:
    # 初始化反爬蟲管理器
    anti_detection = AntiDetectionManager("config/anti_detection_config.json")
    
    # 初始化WebDriver管理器
    webdriver_manager = WebDriverManager(
        config="config/config.json",
        anti_detection_manager=anti_detection
    )
    
    # 獲取WebDriver實例
    driver = webdriver_manager.initialize_driver()
    
    # 初始化驗證碼管理器
    captcha_manager = CaptchaManager(driver, "config/captcha_config.json")
    
    # 初始化狀態管理器
    state_manager = CrawlerStateManager()
    
    # 初始化模板爬蟲
    crawler = TemplateCrawler(
        template_file="templates/gov_procurement.json",
        config_file="config/config.json",
        webdriver_manager=webdriver_manager,
        state_manager=state_manager
    )
    
    # 初始化數據持久化管理器
    persistence_manager = DataPersistenceManager("config/persistence_config.json")
    
    # 執行爬蟲任務
    data = crawler.crawl(max_pages=5)
    
    # 持久化數據
    persistence_manager.save_data(data)
    
    logger.info(f"爬蟲任務完成，共獲取 {len(data)} 筆資料")
    
except Exception as e:
    logger.error(f"爬蟲執行錯誤: {str(e)}", exc_info=True)
    raise  # 向上層拋出異常，確保錯誤被正確處理
    
finally:
    # 清理資源
    try:
        webdriver_manager.quit_driver()
    except Exception as cleanup_error:
        logger.error(f"清理資源時發生錯誤: {str(cleanup_error)}")
```

## 配置文件說明

系統使用 JSON 格式的配置文件來管理各模組的設置。

### config.json

主配置文件，包含爬蟲的基本配置。

```json
{
    "base_url": "https://web.pcc.gov.tw/prkms/tender/common/basic/readTenderBasic",
    "query_params": {
        "pageSize": 100,
        "firstSearch": "true",
        "searchType": "basic",
        "isBinding": "N",
        "isLogIn": "N",
        "level_1": "on",
        "orgName": "",
        "orgId": "3.10.3",
        "tenderName": "",
        "tenderId": "",
        "tenderType": "TENDER_DECLARATION",
        "tenderWay": "TENDER_WAY_ALL_DECLARATION",
        "dateType": "isDate",
        "tenderStartDate": "2023/09/01",
        "tenderEndDate": "2023/09/30",
        "radProctrgCate": "",
        "policyAdvocacy": ""
    },
    "webdriver": {
        "browser": "chrome",
        "headless": true,
        "window_size": {
            "width": 1920,
            "height": 1080
        },
        "page_load_timeout": 30,
        "implicit_wait": 10
    },
    "crawling": {
        "max_pages": 10,
        "max_items": 200,
        "delay": {
            "page_load": {"min": 2, "max": 5},
            "between_pages": {"min": 3, "max": 8},
            "between_items": {"min": 1, "max": 3}
        }
    },
    "persistence": {
        "enabled": true,
        "default_handler": "mongodb",
        "save_local": true,
        "local_format": "json"
    },
        """
        刪除數據
        
        Args:
            key: 數據鍵
            
        Returns:
            bool: 是否成功刪除
        """
        
    def sync_all(self):
        """
        同步所有儲存位置的數據
        
        Returns:
            int: 同步的數據項數
        """
```

**使用示例**:
```python
from src.state.multi_storage import MultiStorageManager
from src.persistence.local_storage import LocalStorage
from src.persistence.mongodb_handler import MongoDBHandler

# 初始化多重儲存管理器
storage_manager = MultiStorageManager()

# 添加不同的儲存實例
storage_manager.add_storage(LocalStorage("states"), priority=0)  # 主要儲存
storage_manager.add_storage(MongoDBHandler(), priority=1)  # 備份儲存

# 保存數據
data = {"status": "running", "progress": 45, "items": [1, 2, 3]}
storage_manager.save("crawler_state_001", data)

# 加載數據（會從優先級最高的可用儲存中加載）
saved_data = storage_manager.load("crawler_state_001")

# 同步所有儲存位置的數據
sync_count = storage_manager.sync_all()
print(f"已同步 {sync_count} 個數據項")
```

## 數據持久化模組 (src/persistence/)

數據持久化模組負責將爬取的數據持久化到各種存儲位置。

### data_persistence_manager.py

數據持久化管理器負責協調各種數據存儲方式。

**主要功能**:
- 管理多種數據存儲方式
- 提供統一的數據操作介面
- 處理數據格式轉換
- 支持數據同步和備份

**關鍵類別和方法**:
```python
class DataPersistenceManager:
    def __init__(self, config=None):
        """
        初始化數據持久化管理器
        
        Args:
            config: 配置字典或配置文件路徑
        """
        
    def add_handler(self, handler, name=None):
        """
        添加持久化處理器
        
        Args:
            handler: 處理器實例
            name: 處理器名稱
        """
        
    def save_data(self, data, handler_name=None):
        """
        保存數據
        
        Args:
            data: 要保存的數據
            handler_name: 處理器名稱（None表示所有處理器）
            
        Returns:
            bool: 是否成功保存
        """
        
    def load_data(self, query, handler_name=None):
        """
        加載數據
        
        Args:
            query: 查詢條件
            handler_name: 處理器名稱
            
        Returns:
            list: 加載的數據
        """
        
    def update_data(self, query, update_data, handler_name=None):
        """
        更新數據
        
        Args:
            query: 查詢條件
            update_data: 更新的數據
            handler_name: 處理器名稱
            
        Returns:
            bool: 是否成功更新
        """
        
    def delete_data(self, query, handler_name=None):
        """
        刪除數據
        
        Args:
            query: 查詢條件
            handler_name: 處理器名稱
            
        Returns:
            bool: 是否成功刪除
        """
        
    def sync_data(self, source_handler, target_handler, query=None):
        """
        同步數據
        
        Args:
            source_handler: 源處理器
            target_handler: 目標處理器
            query: 同步的數據範圍
            
        Returns:
            int: 同步的數據數量
        """
```

**使用示例**:
```python
from src.persistence.data_persistence_manager import DataPersistenceManager
from src.persistence.mongodb_handler import MongoDBHandler
from src.persistence.local_storage import LocalStorage
from src.persistence.notion_handler import NotionHandler

# 初始化數據持久化管理器
persistence_manager = DataPersistenceManager("config/persistence_config.json")

# 添加不同的持久化處理器
persistence_manager.add_handler(LocalStorage("data/json"), "local")
persistence_manager.add_handler(MongoDBHandler(), "mongodb")
persistence_manager.add_handler(NotionHandler(), "notion")

# 保存數據到所有處理器
data = [
    {"id": "item001", "title": "測試項目1", "price": 100},
    {"id": "item002", "title": "測試項目2", "price": 200}
]
persistence_manager.save_data(data)

# 只保存到特定處理器
persistence_manager.save_data(data, handler_name="mongodb")

# 從MongoDB加載數據
items = persistence_manager.load_data({"price": {"$gt": 150}}, handler_name="mongodb")

# 更新數據
persistence_manager.update_data(
    {"id": "item001"},
    {"$set": {"price": 150}},
    handler_name="mongodb"
)

# 同步數據
sync_count = persistence_manager.sync_data("mongodb", "notion")
print(f"已同步 {sync_count} 條記錄到Notion")
```

### mongodb_handler.py, notion_handler.py, local_storage.py

各種數據持久化處理器，用於將數據存儲到不同的位置。

**關鍵類別和方法**:
```python
class MongoDBHandler:
    """MongoDB數據持久化處理器"""
    
    def __init__(self, config=None):
        """初始化MongoDB處理器"""
        
    def save(self, data):
        """保存數據到MongoDB"""
        
    def load(self, query):
        """從MongoDB加載數據"""
        
    def update(self, query, update_data):
        """更新MongoDB中的數據"""
        
    def delete(self, query):
        """從MongoDB刪除數據"""

class NotionHandler:
    """Notion數據持久化處理器"""
    
    def __init__(self, config=None):
        """初始化Notion處理器"""
        
    def save(self, data):
        """保存數據到Notion"""
        
    def load(self, query):
        """從Notion加載數據"""
        
    def update(self, query, update_data):
        """更新Notion中的數據"""
        
    def delete(self, query):
        """從Notion刪除數據"""

class LocalStorage:
    """本地文件系統數據持久化處理器"""
    
    def __init__(self, base_dir="data", format="json"):
        """初始化本地存儲處理器"""
        
    def save(self, data, filename=None):
        """保存數據到本地文件"""
        
    def load(self, query=None, filename=None):
        """從本地文件加載數據"""
        
    def update(self, query, update_data, filename=None):
        """更新本地文件中的數據"""
        
    def delete(self, query, filename=None):
        """從本地文件刪除數據"""
```

## 整合與使用

各模組之間的協作可以通過以下方式進行整合：

### main.py

系統主入口，整合各個模組並執行爬蟲任務。

```python
import os
import argparse
import json
from datetime import datetime

from src.core.crawler_engine import CrawlerEngine
from src.utils.logger import LoggerManager
from src.utils.config_loader import ConfigLoader

def main():
    # 解析命令行參數
    parser = argparse.ArgumentParser(description="網站爬蟲工具")
    parser.add_argument("-t", "--template", required=True, help="爬蟲模板文件路徑")
    parser.add_argument("-c", "--config", default="config/config.json", help="配置文件路徑")
    parser.add_argument("-p", "--pages", type=int, help="最大爬取頁數")
    parser.add_argument("-i", "--items", type=int, help="最大爬取項目數")
    parser.add_argument("-r", "--resume", action="store_true", help="從中斷點恢復爬取")
    parser.add_argument("-o", "--output", help="輸出文件路徑")
    args = parser.parse_args()
    
    # 初始化日誌管理器
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, f"crawler_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
    logger_manager = LoggerManager(name="crawler", level="INFO", log_file=log_file)
    logger = logger_manager.get_logger()
    
    # 加載配置
    config = ConfigLoader(args.config)
    
    # 創建爬蟲引擎
    engine = CrawlerEngine(args.config)
    
    try:
        # 決定是否從中斷點恢復
        if args.resume:
            logger.info(f"從中斷點恢復爬取: {args.template}")
            crawler_id = os.path.basename(args.template).split('.')[0]
            data = engine.resume_crawler(crawler_id)
        else:
            logger.info(f"開始爬取: {args.template}")
            crawler = engine.create_template_crawler(args.template)
            data = engine.run_crawler(
                crawler, 
                max_pages=args.pages, 
                max_items=args.items
            )
        
        # 持久化數據
        if data:
            logger.info(f"爬取完成，共獲取 {len(data)} 筆資料")
            
            # 保存到指定輸出文件
            if args.output:
                output_dir = os.path.dirname(args.output)
                if output_dir and not os.path.exists(output_dir):
                    os.makedirs(output_dir, exist_ok=True)
                    
                with open(args.output, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                logger.info(f"數據已保存到: {args.output}")
            
            # 使用持久化管理器保存
            engine.persist_data(data)
            
    except Exception as e:
        logger.error(f"爬蟲執行錯誤: {str(e)}", exc_info=True)
        raise  # 向上層拋出異常，確保錯誤被正確處理
    
    finally:
        # 清理資源
        try:
            webdriver_manager.quit_driver()
        except Exception as cleanup_error:
            logger.error(f"清理資源時發生錯誤: {str(cleanup_error)}")
        
    return 0

if __name__ == "__main__":
    exit(main())
```

### 模板集成示例

以下是一個完整的爬蟲任務示例，展示了如何將各個模組集成起來使用：

```python
# 導入所需模組
from src.core.webdriver_manager import WebDriverManager
from src.anti_detection.anti_detection_manager import AntiDetectionManager
from src.captcha.captcha_manager import CaptchaManager
from src.core.template_crawler import TemplateCrawler
from src.state.crawler_state_manager import CrawlerStateManager
from src.persistence.data_persistence_manager import DataPersistenceManager
from src.utils.logger import LoggerManager

# 初始化日誌
logger_manager = LoggerManager(name="crawler_example", log_file="logs/example.log")
logger = logger_manager.get_logger()

try:
    # 初始化反爬蟲管理器
    anti_detection = AntiDetectionManager("config/anti_detection_config.json")
    
    # 初始化WebDriver管理器
    webdriver_manager = WebDriverManager(
        config="config/config.json",
        anti_detection_manager=anti_detection
    )
    
    # 獲取WebDriver實例
    driver = webdriver_manager.initialize_driver()
    
    # 初始化驗證碼管理器
    captcha_manager = CaptchaManager(driver, "config/captcha_config.json")
    
    # 初始化狀態管理器
    state_manager = CrawlerStateManager()
    
    # 初始化模板爬蟲
    crawler = TemplateCrawler(
        template_file="templates/gov_procurement.json",
        config_file="config/config.json",
        webdriver_manager=webdriver_manager,
        state_manager=state_manager
    )
    
    # 初始化數據持久化管理器
    persistence_manager = DataPersistenceManager("config/persistence_config.json")
    
    # 執行爬蟲任務
    data = crawler.crawl(max_pages=5)
    
    # 持久化數據
    persistence_manager.save_data(data)
    
    logger.info(f"爬蟲任務完成，共獲取 {len(data)} 筆資料")
    
except Exception as e:
    logger.error(f"爬蟲執行錯誤: {str(e)}", exc_info=True)
    raise  # 向上層拋出異常，確保錯誤被正確處理
    
finally:
    # 清理資源
    try:
        webdriver_manager.quit_driver()
    except Exception as cleanup_error:
        logger.error(f"清理資源時發生錯誤: {str(cleanup_error)}")
```

## 配置文件說明

系統使用 JSON 格式的配置文件來管理各模組的設置。

### config.json

主配置文件，包含爬蟲的基本配置。

```json
{
    "base_url": "https://web.pcc.gov.tw/prkms/tender/common/basic/readTenderBasic",
    "query_params": {
        "pageSize": 100,
        "firstSearch": "true",
        "searchType": "basic",
        "isBinding": "N",
        "isLogIn": "N",
        "level_1": "on",
        "orgName": "",
        "orgId": "3.10.3",
        "tenderName": "",
        "tenderId": "",
        "tenderType": "TENDER_DECLARATION",
        "tenderWay": "TENDER_WAY_ALL_DECLARATION",
        "dateType": "isDate",
        "tenderStartDate": "2023/09/01",
        "tenderEndDate": "2023/09/30",
        "radProctrgCate": "",
        "policyAdvocacy": ""
    },
    "webdriver": {
        "browser": "chrome",
        "headless": true,
        "window_size": {
            "width": 1920,
            "height": 1080
        },
        "page_load_timeout": 30,
        "implicit_wait": 10
    },
    "crawling": {
        "max_pages": 10,
        "max_items": 200,
        "delay": {
            "page_load": {"min": 2, "max": 5},
            "between_pages": {"min": 3, "max": 8},
            "between_items": {"min": 1, "max": 3}
        }
    },
    "persistence": {
        "enabled": true,
        "default_handler": "mongodb",
        "save_local": true,
        "local_format": "json"
    },
    "logging": {
        "level": "INFO",
        "console_output": true,
        "file_output": true,
        "log_dir": "logs"
    }
}
```

### field_mappings.json

字段映射配置，用於定義爬取數據與存儲字段之間的映射關係。

```json
{
    "mongodb": {
        "tender_case_no": "case_id",
        "tender_name": "title",
        "organization_name": "org_name",
        "tender_start_date": "start_date",
        "tender_end_date": "end_date",
        "tender_amount": "amount"
    },
    "notion": {
        "tender_case_no": "案號",
        "tender_name": "標案名稱",
        "organization_name": "機關名稱",
        "tender_start_date": "公告日期",
        "tender_end_date": "截止日期",
        "tender_amount": "預算金額"
    }
}
```

## 擴展指南

### 添加新的爬蟲模板

要添加新的爬蟲模板，只需在 `templates` 目錄下創建新的 JSON 模板文件：

1. 分析目標網站結構
2. 確定列表頁和詳情頁的 XPath 選擇器
3. 定義分頁和項目選擇器
4. 設置適當的延遲和請求參數

### 添加新的驗證碼解決器

要支持新類型的驗證碼，可以擴展驗證碼處理模組：

1. 在 `src/captcha/solvers/` 目錄下創建新的解決器類
2. 繼承 `BaseCaptchaSolver` 類
3. 實現 `detect()` 和 `solve()` 方法
4. 在 `CaptchaManager` 中註冊新的解決器

### 添加新的數據存儲處理器

要支持新的數據存儲方式，可以擴展數據持久化模組：

1. 創建新的處理器類，實現必要的介面方法
2. 在 `DataPersistenceManager` 中註冊新的處理器
3. 更新配置文件以支持新的存儲方式

## 總結

本文檔詳細說明了爬蟲系統的各個模組，包括其功能、設計原理、關鍵類別與方法以及使用示例。系統採用高度模組化設計，各模組之間有清晰的界限和定義良好的接口，便於維護與擴展。通過本文檔，開發者可以快速了解系統各部分的功能和使用方法，以便更好地開發和維護爬蟲系統。