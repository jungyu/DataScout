#!/usr/bin/env python3
"""
Bloomberg 爬蟲程式 - 使用 playwright_base 框架

這是一個使用 playwright_base 框架開發的爬蟲程式，用於爬取 Bloomberg 網站的新聞內容。
基於 DataScout 專案的 Nikkei 爬蟲架構進行調整。
"""

import os
import json
import time
import random
import configparser
from datetime import datetime, date
from typing import List, Dict, Any, Optional
from pathlib import Path

# 導入 playwright_base 框架
from playwright_base import (
    PlaywrightBase, 
    setup_logger, 
    check_and_handle_popup,  # 加入彈窗處理功能
)

# 進行條件性導入，失敗時不會中斷程式
try:
    from playwright_base.config.settings import ConfigManager
except ImportError:
    ConfigManager = None

try:
    from playwright_base.storage.storage_manager import StorageManager
except ImportError:
    # 簡易 StorageManager 實現
    class StorageManager:
        def __init__(self, base_dir):
            self.base_dir = base_dir
        
        def save_json(self, data, filename, **kwargs):
            import json
            import os
            filepath = os.path.join(self.base_dir, filename)
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, **kwargs)
            return filepath

try:
    from playwright_base.anti_detection.human_like import HumanLikeBehavior
except ImportError:
    # 簡易版本的 HumanLikeBehavior 
    class HumanLikeBehavior:
        def random_delay(self, min_delay=1.0, max_delay=3.0):
            import random
            import time
            delay = random.uniform(min_delay, max_delay)
            time.sleep(delay)
            return delay
        
        def scroll_page(self, page):
            # 簡單模擬頁面滾動
            page.evaluate("""
                () => {
                    window.scrollTo(0, 300);
                    setTimeout(() => { window.scrollTo(0, 700); }, 500);
                    setTimeout(() => { window.scrollTo(0, 1000); }, 1000);
                }
            """)

# 設置日誌
logger = setup_logger(
    name="bloomberg_scraper",
    log_file=f"logs/bloomberg_scraper_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
)

# 獲取當前腳本所在目錄
SCRIPT_DIR = Path(__file__).parent.absolute()
CONFIG_DIR = SCRIPT_DIR / "config"
STORAGE_DIR = SCRIPT_DIR / "storage"

# 確保必要的目錄存在
STORAGE_DIR.mkdir(exist_ok=True)
(SCRIPT_DIR / "logs").mkdir(exist_ok=True)
CONFIG_DIR.mkdir(exist_ok=True)

class BloombergScraper:
    """
    Bloomberg 爬蟲類
    基於 playwright_base 框架實現的爬蟲，用於爬取 Bloomberg 網站的新聞內容。
    """

    def __init__(self, config_file: str = "bloomberg_config.json", credential_file: str = "credentials.ini"):
        """
        初始化 Bloomberg 爬蟲

        參數:
            config_file: 配置檔案路徑
            credential_file: 登入憑證檔案路徑（若需要）
        """
        # 載入配置
        config_path = CONFIG_DIR / config_file
        if not config_path.exists():
            # 建立預設配置
            self._create_default_config(config_path)
            logger.info(f"已創建預設配置檔案: {config_path}")
        
        # 載入配置
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
        
        # 初始化爬蟲引擎 (保持為 None 直到需要時才創建)
        self.crawler = None
        self.human_like = HumanLikeBehavior()
        self.storage_manager = StorageManager(str(STORAGE_DIR))
        
        # 檢查是否需要登入
        self.need_login = False
        try:
            if credential_file and (CONFIG_DIR / credential_file).exists():
                credential_path = CONFIG_DIR / credential_file
                config_parser = configparser.ConfigParser()
                config_parser.read(credential_path)
                self.email = config_parser['login']['email']
                self.password = config_parser['login']['password']
                self.need_login = True
                logger.info("已加載登入憑證")
        except Exception as e:
            logger.warning(f"無法加載登入憑證，將以訪客模式訪問: {str(e)}")
            self.need_login = False

    def _create_default_config(self, config_path: Path) -> None:
        """創建默認配置文件"""
        default_config = {
            "site": {
                "base_url": "https://www.bloomberg.com",
                "search_url": "https://www.bloomberg.com/search"
            },
            "browser": {
                "headless": False,
                "browser_type": "chromium",
                "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
                "viewport": {"width": 1280, "height": 800}
            },
            "storage": {
                "lists_file": "bloomberg_articles_list.json",
                "articles_file": "bloomberg_articles_content.json", 
                "storage_file": "bloomberg_session.json",
                "results_file": "bloomberg_search_results.json"
            },
            "scraping": {
                "max_load_more_clicks": 5,
                "delay_between_articles": {"min": 2, "max": 5},
                "delay_between_load_more": 3,
                "auto_close_popups": True
            },
            "selectors": {
                "search_results": {
                    "article": "div.storyItem__aaf871c1c5",
                    "title": "a.headline__3a97424275",
                    "category": "div.eyebrow__e77dd63365",
                    "publish_time": "div.publishedAt__dc9dff8db4",
                    "description": "a.summary__a759320e4a",
                    "load_more_button": "button.button__f6b7ccfb8d[title='Load More Results']"
                },
                "article_detail": {
                    "wrapper": "div.gridLayout_centerContent__XTM8S",
                    "category": "div.media-ui-Eyebrow_eyebrow-KO8LpxCW2xI-",
                    "title": "h1.media-ui-HedAndDek_headline-D19MOidHYLI-",
                    "subtitle": ".media-ui-HedAndDek_dek-iDJMnzi5pZ4-",
                    "image": "figure img.ui-image",
                    "image_caption": "span.media-ui-Caption_caption-KKcpFT8qLQg-",
                    "author": "div.media-ui-Byline_bylineAuthors-Ts-ifi4q-HY- a",
                    "publish_time": "div.media-ui-Timestamp_timestampWrapper-w-YevWapP-k- time",
                    "update_time": "div.media-ui-Timestamp_timestampWrapper-w-YevWapP-k- time[data-type='updated']",
                    "content": "p.media-ui-Paragraph_text-SqIsdNjh0t0-",
                    "popup_close": ".close-button, .btn-close, button[aria-label='Close']"
                }
            }
        }
        
        # 確保配置目錄存在
        config_path.parent.mkdir(exist_ok=True)
        
        # 寫入配置檔案
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(default_config, f, ensure_ascii=False, indent=2)

    def _load_json(self, filepath: Path) -> List[Dict[str, Any]]:
        """從 JSON 檔案加載數據"""
        if filepath.exists():
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read().strip()
                    if content:  # 檢查檔案是否為空
                        return json.loads(content)
                    else:
                        logger.warning(f"檔案 {filepath} 為空，返回空列表")
                        return []
            except json.JSONDecodeError as e:
                logger.error(f"解析 JSON 檔案 {filepath} 時出現錯誤: {str(e)}，返回空列表")
                # 備份損壞的檔案
                try:
                    import shutil
                    backup_file = str(filepath) + f".bak.{int(time.time())}"
                    shutil.copy2(filepath, backup_file)
                    logger.info(f"已備份損壞的 JSON 檔案到: {backup_file}")
                except Exception as backup_error:
                    logger.warning(f"備份損壞的 JSON 檔案時出錯: {str(backup_error)}")
                return []
            except Exception as e:
                logger.error(f"讀取檔案 {filepath} 時出現未知錯誤: {str(e)}，返回空列表")
                return []
        return []

    def _save_json(self, data: Any, filepath: Path) -> None:
        """保存數據到 JSON 檔案"""
        try:
            # 確保父目錄存在
            filepath.parent.mkdir(exist_ok=True)
            
            # 先寫入臨時文件
            temp_file = str(filepath) + ".tmp"
            with open(temp_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            # 如果成功寫入，則替換原文件
            import os
            if os.path.exists(filepath):
                os.replace(temp_file, filepath)
            else:
                os.rename(temp_file, filepath)
                
            logger.info(f"已儲存數據至 {filepath}")
        except Exception as e:
            logger.error(f"儲存數據到 {filepath} 時出現錯誤: {str(e)}")
            # 如果臨時文件存在，嘗試刪除
            try:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
            except:
                pass

    def _build_query_string(self, params: Dict[str, str]) -> str:
        """構建查詢字符串"""
        return "&".join([f"{k}={v}" for k, v in params.items()])

    def _is_duplicate_url(self, url: str) -> bool:
        """
        檢查 URL 是否已存在於列表中
        
        參數:
            url: 要檢查的文章 URL
            
        返回:
            如果 URL 已存在於列表中，則返回 True，否則返回 False
        """
        return any(item['url'] == url for item in self.lists)

    def init_crawler(self) -> None:
        """初始化爬蟲實例並處理登入"""
        browser_config = self.config["browser"]
        
        # 增強型 User-Agent 隨機化
        self._setup_enhanced_user_agent(browser_config)
        
        # 檢查 storage_state 檔案
        storage_state = None
        if self.storage_file.exists():
            try:
                # 嘗試讀取檔案並驗證是有效的 JSON
                with open(self.storage_file, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    if content:
                        import json
                        storage_state = json.loads(content)
                        logger.info(f"已載入儲存狀態檔案: {self.storage_file}")
                    else:
                        logger.warning(f"儲存狀態檔案 {self.storage_file} 是空的，將重新登入")
            except json.JSONDecodeError as e:
                logger.warning(f"儲存狀態檔案 {self.storage_file} 格式錯誤: {str(e)}，將重新登入")
                # 備份並刪除無效檔案
                backup_file = str(self.storage_file) + '.bak'
                import shutil
                shutil.copy2(self.storage_file, backup_file)
                logger.info(f"已備份無效的儲存狀態檔案到: {backup_file}")
                os.remove(self.storage_file)
            except Exception as e:
                logger.warning(f"讀取儲存狀態檔案時發生錯誤: {str(e)}，將重新登入")
        
        # 針對 Bloomberg 調整瀏覽器啟動參數
        special_args = [
            '--disable-blink-features=AutomationControlled',  # 隱藏自動化特徵
            '--disable-features=IsolateOrigins,site-per-process',  # 處理某些防爬蟲機制
            '--disable-web-security',  # 避免某些 CORS 問題
            '--disable-site-isolation-trials',  # 更好的跨域處理
        ]
        
        if not browser_config.get("args"):
            browser_config["args"] = []
        browser_config["args"].extend(special_args)
        
        # 創建爬蟲實例
        self.crawler = PlaywrightBase(
            headless=browser_config["headless"],
            browser_type=browser_config["browser_type"],
            user_agent=browser_config["user_agent"],
            viewport=browser_config["viewport"],
            storage_state=storage_state,  # 直接傳入狀態對象而非檔案路徑
            args=browser_config["args"]   # 傳入增強的啟動參數
        )
        
        # 啟動瀏覽器
        self.crawler.start()
        
        # 不啟用隱身模式，避免被檢測
        # 直接使用增強型反檢測
        self._apply_enhanced_anti_detection()
        
        # 註冊頁面事件處理器 - 使用安全調用以防止方法不存在
        try:
            if hasattr(self.crawler, 'register_page_event_handlers'):
                self.crawler.register_page_event_handlers()
                logger.info("已註冊頁面事件處理器")
        except Exception as e:
            logger.warning(f"註冊頁面事件處理器時出錯: {str(e)}")
        
        # 如果需要登入且不存在 storage_file，則進行登入
        if self.need_login and not self.storage_file.exists():
            self.login()

    def _setup_enhanced_user_agent(self, browser_config):
        """設置增強型 User-Agent
        
        為避免被檢測為爬蟲，使用更真實的 User-Agent
        """
        # 常用瀏覽器的 User-Agent
        common_user_agents = [
            # MacOS - Chrome
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            # MacOS - Safari
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3 Safari/605.1.15",
            # Windows - Chrome
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            # Windows - Edge
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 Edg/122.0.2365.52",
            # iOS - Safari (iPhone)
            "Mozilla/5.0 (iPhone; CPU iPhone OS 17_3_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3 Mobile/15E148 Safari/604.1"
        ]
        
        # 使用配置中的 User-Agent 或隨機選擇一個
        if browser_config.get("randomize_user_agent", False):
            browser_config["user_agent"] = random.choice(common_user_agents)
            logger.info(f"隨機選擇 User-Agent: {browser_config['user_agent']}")
    
    def _apply_enhanced_anti_detection(self):
        """應用增強型反檢測措施，但不使用隱身模式"""
        try:
            # 修改 WebGL 指紋
            self.crawler.page.evaluate("""
                () => {
                    // 修改 WebGL 指紋
                    const getParameter = WebGLRenderingContext.prototype.getParameter;
                    WebGLRenderingContext.prototype.getParameter = function(parameter) {
                        // 干擾 UNMASKED_VENDOR_WEBGL 和 UNMASKED_RENDERER_WEBGL
                        if (parameter === 37445) {
                            return 'Intel Inc.'; // UNMASKED_VENDOR_WEBGL
                        }
                        if (parameter === 37446) {
                            return 'Intel Iris Pro Graphics'; // UNMASKED_RENDERER_WEBGL
                        }
                        return getParameter.call(this, parameter);
                    };
                    
                    // 移除 navigator.webdriver 標記
                    Object.defineProperty(navigator, 'webdriver', { get: () => false });
                    
                    // 刪除 playwright 標記
                    if (window.navigator.userAgent.includes('HeadlessChrome')) {
                        Object.defineProperty(navigator, 'userAgent', {
                            get: function() {
                                return navigator.userAgent.replace('HeadlessChrome', 'Chrome');
                            }
                        });
                    }
                    
                    // 偽裝 Chrome 特性
                    window.chrome = {
                        app: {
                            isInstalled: true,
                            InstallState: {
                                DISABLED: 'disabled',
                                INSTALLED: 'installed',
                                NOT_INSTALLED: 'not_installed'
                            },
                            RunningState: {
                                CANNOT_RUN: 'cannot_run',
                                READY_TO_RUN: 'ready_to_run',
                                RUNNING: 'running'
                            }
                        },
                        runtime: {
                            OnInstalledReason: {
                                INSTALL: 'install',
                                UPDATE: 'update',
                                CHROME_UPDATE: 'chrome_update',
                                SHARED_MODULE_UPDATE: 'shared_module_update'
                            },
                            OnRestartRequiredReason: {
                                APP_UPDATE: 'app_update',
                                OS_UPDATE: 'os_update',
                                PERIODIC: 'periodic'
                            },
                            PlatformArch: {
                                ARM: 'arm',
                                ARM64: 'arm64',
                                MIPS: 'mips',
                                MIPS64: 'mips64',
                                X86_32: 'x86-32',
                                X86_64: 'x86-64'
                            },
                            PlatformNaclArch: {
                                ARM: 'arm',
                                MIPS: 'mips',
                                MIPS64: 'mips64',
                                X86_32: 'x86-32',
                                X86_64: 'x86-64'
                            },
                            PlatformOs: {
                                ANDROID: 'android',
                                CROS: 'cros',
                                LINUX: 'linux',
                                MAC: 'mac',
                                OPENBSD: 'openbsd',
                                WIN: 'win'
                            },
                            RequestUpdateCheckStatus: {
                                THROTTLED: 'throttled',
                                NO_UPDATE: 'no_update',
                                UPDATE_AVAILABLE: 'update_available'
                            }
                        }
                    };
                }
            """)
            
            # 模擬真實瀏覽器的 languages 和 plugins
            self.crawler.page.evaluate("""
                () => {
                    // 修改 navigator.languages
                    Object.defineProperty(navigator, 'languages', {
                        get: function() { return ['en-US', 'en', 'zh-TW']; }
                    });
                    
                    // 修復 plugins
                    const makeFakePluginArray = () => {
                        const plugins = [
                            {
                                name: 'Chrome PDF Plugin',
                                filename: 'internal-pdf-viewer',
                                description: 'Portable Document Format'
                            },
                            {
                                name: 'Chrome PDF Viewer',
                                filename: 'mhjfbmdgcfjbbpaeojofohoefgiehjai',
                                description: ''
                            },
                            {
                                name: 'Native Client',
                                filename: 'internal-nacl-plugin',
                                description: ''
                            }
                        ];
                        
                        const fakePlugins = [];
                        for (let i = 0; i < plugins.length; i++) {
                            const plugin = plugins[i];
                            
                            const fakePlugin = {
                                name: plugin.name,
                                filename: plugin.filename,
                                description: plugin.description,
                                length: 1
                            };
                            
                            // Add a fake mime type
                            fakePlugin[0] = {
                                type: 'application/x-nacl',
                                suffixes: '',
                                description: plugin.description,
                                enabledPlugin: fakePlugin
                            };
                            
                            Object.defineProperty(fakePlugin, '0', {
                                enumerable: true
                            });
                            
                            Object.setPrototypeOf(fakePlugin, Plugin.prototype);
                            fakePlugins.push(fakePlugin);
                        }
                        
                        return fakePlugins;
                    };
                    
                    const fakePlugins = makeFakePluginArray();
                    
                    // 使用代理來模擬 PluginArray
                    const fakePluginArray = Object.create(PluginArray.prototype);
                    
                    // 實現基本方法
                    fakePluginArray.length = fakePlugins.length;
                    fakePluginArray.item = index => fakePlugins[index];
                    fakePluginArray.namedItem = name => fakePlugins.find(p => p.name === name);
                    fakePluginArray.refresh = () => {};
                    
                    // 添加數字索引屬性
                    for (let i = 0; i < fakePlugins.length; i++) {
                        fakePluginArray[i] = fakePlugins[i];
                        Object.defineProperty(fakePluginArray, i, {
                            enumerable: true
                        });
                    }
                    
                    // 添加命名屬性
                    fakePlugins.forEach(plugin => {
                        fakePluginArray[plugin.name] = plugin;
                    });
                    
                    // 替換 navigator.plugins
                    Object.defineProperty(navigator, 'plugins', {
                        get: () => fakePluginArray,
                        enumerable: true,
                        configurable: true
                    });
                }
            """)
            
            logger.info("已應用增強型反檢測措施")
        except Exception as e:
            logger.warning(f"應用增強型反檢測時出錯: {str(e)}")

    def login(self) -> None:
        """登入 Bloomberg 網站"""
        if not self.need_login or not hasattr(self, 'email') or not hasattr(self, 'password'):
            logger.info("無法進行登入，缺少必要的登入資訊")
            return
            
        try:
            logger.info("開始執行 Bloomberg 登入流程...")
            
            # 訪問首頁
            self.crawler.goto(self.base_url, wait_until="networkidle")
            
            # 等待頁面載入並尋找登入按鈕
            logger.info("尋找登入按鈕...")
            # 嘗試使用不同的選擇器找到登入按鈕
            sign_in_selectors = [
                "button[data-testid='sign-in-button']",  # 主要匹配目標
                "button.media-ui-LogoBar_signInButton-9yr-B7jjuE0-",  # 新增的精確 class 選擇器
                "button[aria-label='Sign In']",
                "button.media-ui-LogoBarMobile_signInButton-NjOyFCGDTLw-",
                "button:has-text('Sign In')",  # 使用文本內容尋找按鈕
                "a.ticker-strip__sign-in"
            ]
            
            sign_in_button = None
            for selector in sign_in_selectors:
                try:
                    sign_in_button = self.crawler.page.query_selector(selector)
                    if sign_in_button:
                        logger.info(f"找到登入按鈕，使用選擇器: {selector}")
                        break
                except Exception as e:
                    logger.debug(f"搜尋選擇器 {selector} 時出現錯誤: {str(e)}")
            
            if not sign_in_button:
                logger.warning("無法找到登入按鈕，略過登入")
                return
                
            # 點擊登入按鈕
            sign_in_button.click()
            logger.info("已點擊登入按鈕")
            
            # 等待登入對話框出現
            logger.info("等待登入對話框出現...")
            self.crawler.page.wait_for_selector("input#email-form-input", timeout=10000)
            
            # 輸入電子郵件
            logger.info("輸入電子郵件...")
            email_input = self.crawler.page.query_selector("input#email-form-input")
            if not email_input:
                logger.warning("無法找到電子郵件輸入框，略過登入")
                return
                
            # 清空輸入框並輸入電子郵件
            email_input.fill("")
            self.crawler.page.wait_for_timeout(500)  # 短暫延遲，模擬人工輸入
            email_input.type(self.email, delay=100)  # 模擬人類輸入速度
            
            # 等待 "Continue" 按鈕可點擊
            logger.info("等待 Continue 按鈕可點擊...")
            continue_button = self.crawler.page.query_selector("button[type='submit']:not([disabled])")
            
            # 如果無法直接找到啟用的按鈕，等待一段時間後再嘗試
            if not continue_button:
                self.crawler.page.wait_for_timeout(2000)
                continue_button = self.crawler.page.query_selector("button[type='submit']:not([disabled])")
                
            if not continue_button:
                logger.warning("無法找到可點擊的 Continue 按鈕，略過登入")
                return
                
            # 點擊 "Continue" 按鈕
            logger.info("點擊 Continue 按鈕...")
            continue_button.click()
            
            # 等待密碼輸入框出現
            logger.info("等待密碼輸入框出現...")
            try:
                self.crawler.page.wait_for_selector("input[type='password']", timeout=10000)
            except Exception as e:
                logger.warning(f"等待密碼輸入框超時: {str(e)}")
                return
                
            # 輸入密碼
            logger.info("輸入密碼...")
            password_input = self.crawler.page.query_selector("input[type='password']")
            if not password_input:
                logger.warning("無法找到密碼輸入框，略過登入")
                return
                
            # 清空輸入框並輸入密碼
            password_input.fill("")
            self.crawler.page.wait_for_timeout(500)  # 短暫延遲，模擬人工輸入
            password_input.type(self.password, delay=100)  # 模擬人類輸入速度
            
            # 等待 "Continue" 按鈕可點擊
            logger.info("等待密碼頁面的 Continue 按鈕可點擊...")
            self.crawler.page.wait_for_timeout(1000)  # 等待按鈕啟用
            continue_button = self.crawler.page.query_selector("button[type='submit']:not([disabled])")
            
            if not continue_button:
                logger.warning("無法找到密碼頁面的 Continue 按鈕，略過登入")
                return
                
            # 點擊 "Continue" 按鈕
            logger.info("點擊密碼頁面的 Continue 按鈕...")
            continue_button.click()
            
            # 等待登入完成
            logger.info("等待登入完成...")
            try:
                # 等待登入後的頁面載入（假設登入後會重定向回主頁）
                self.crawler.wait_for_load_state("networkidle")
                
                # 檢查是否登入成功（尋找登入後才會出現的元素）
                logger.info("檢查登入狀態...")
                
                # 可以根據實際情況調整以下檢查邏輯
                try:
                    # 等待頁面上某個只有登入後才會出現的元素
                    # 例如：用戶頭像或登出按鈕
                    self.crawler.page.wait_for_selector("button[aria-label='Account']", timeout=5000)
                    login_successful = True
                except Exception:
                    # 如果找不到用戶頭像，再嘗試其他登入成功的標誌
                    try:
                        self.crawler.page.wait_for_selector(".profile-button", timeout=3000)
                        login_successful = True
                    except Exception:
                        login_successful = False
                
                if login_successful:
                    logger.info("登入成功！")
                    # 登入成功後保存 session
                    self.crawler.save_storage(str(self.storage_file))
                    logger.info(f"已儲存登入狀態到 {self.storage_file}")
                else:
                    logger.warning("可能登入失敗，找不到登入後的用戶元素")
            except Exception as e:
                logger.error(f"等待登入完成時出現錯誤: {str(e)}")
                
        except Exception as e:
            logger.error(f"登入過程中發生錯誤: {str(e)}")

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

    def scrape_search_results(self, keyword: str, max_load_more: int = None) -> List[Dict[str, Any]]:
        """
        爬取關鍵詞搜尋結果
        
        參數:
            keyword: 搜尋關鍵詞
            max_load_more: 最大加載更多次數，默認從配置中讀取
            
        返回:
            爬取的文章列表
        """
        if not self.crawler:
            self.init_crawler()
            
        if max_load_more is None:
            max_load_more = self.config["scraping"]["max_load_more_clicks"]
            
        results_record = self.load_results()
        selectors = self.config["selectors"]["search_results"]
        
        try:
            # 檢查是否已爬過
            if any(r["keyword"] == keyword for r in results_record["records"]):
                logger.info(f"已爬過關鍵詞 {keyword}，略過")
                return self.lists
            
            # 訪問搜尋頁面
            search_params = {"query": keyword.replace(" ", "%20")}
            search_url = f"{self.search_url}?{self._build_query_string(search_params)}"
            
            # 使用新的重試機制訪問 URL
            if not self.goto_url_with_retry(search_url, max_retries=3):
                logger.error(f"無法成功訪問搜尋頁面: {search_url}")
                return self.lists  # 返回現有列表，不繼續處理
            
            # 抓取初始頁面文章
            articles = self.crawler.page.query_selector_all(selectors["article"])
            logger.info(f"初始頁面找到 {len(articles)} 篇文章")
            
            # 模擬人類滾動頁面
            self.human_like.scroll_page(self.crawler.page)
            
            # 提取文章資訊
            page_new_articles = self._extract_articles_info(articles)
            total_articles = page_new_articles
            load_more_count = 0
            duplicate_count = 0
            
            # 點擊「加載更多」按鈕
            while load_more_count < max_load_more:
                # 尋找加載更多按鈕
                load_more_button = self.crawler.page.query_selector(selectors["load_more_button"])
                
                if not load_more_button:
                    logger.info("未找到加載更多按鈕，可能已到達最後一頁")
                    break
                
                logger.info(f"點擊加載更多按鈕 ({load_more_count + 1}/{max_load_more})")
                load_more_button.scroll_into_view_if_needed()
                self.human_like.random_delay(1, 2)
                load_more_button.click()
                
                # 等待更多內容加載
                self.crawler.wait_for_load_state("networkidle")
                time.sleep(self.config["scraping"]["delay_between_load_more"])
                
                # 模擬人類滾動頁面
                self.human_like.scroll_page(self.crawler.page)
                
                # 獲取所有文章
                articles = self.crawler.page.query_selector_all(selectors["article"])
                logger.info(f"第 {load_more_count + 1} 次加載後，頁面共有 {len(articles)} 篇文章")
                
                # 提取文章資訊
                page_new_articles = self._extract_articles_info(articles)
                total_articles += page_new_articles
                
                load_more_count += 1
                
                if duplicate_count > 10:  # 如果連續出現多個重複，可能已經沒有新內容
                    logger.info(f"發現大量重複文章，已停止加載更多")
                    break
            
            # 儲存搜尋結果記錄
            results_record["records"].append({"keyword": keyword, "count": total_articles})
            self._save_json(results_record, self.results_file)
            
            logger.info(f"完成搜尋關鍵詞 {keyword}，共找到 {total_articles} 篇文章")
            return self.lists
            
        except Exception as e:
            logger.error(f"爬取搜尋結果時發生錯誤: {str(e)}")
            return []

    def _extract_articles_info(self, articles) -> int:
        """從搜尋結果頁面提取文章信息"""
        selectors = self.config["selectors"]["search_results"]
        page_new_articles = 0
        duplicate_count = 0
        
        for idx, article in enumerate(articles, 1):
            try:
                # 提取標題和鏈接
                title_element = article.query_selector(selectors["title"])
                if not title_element:
                    logger.warning(f"無法找到文章標題元素，跳過")
                    continue
                    
                title = title_element.inner_text()
                url = title_element.get_attribute("href")
                
                # 確保 URL 是完整的
                if not url.startswith("http"):
                    if url.startswith("/"):
                        url = f"{self.base_url}{url}"
                    else:
                        url = f"{self.base_url}/{url}"
                
                # 檢查 URL 是否重複
                if self._is_duplicate_url(url):
                    logger.debug(f"發現重複文章: {title} - {url}")
                    duplicate_count += 1
                    continue
                
                # 提取分類
                category_element = article.query_selector(selectors["category"])
                category = category_element.inner_text() if category_element else ""
                
                # 提取發布時間
                time_element = article.query_selector(selectors["publish_time"])
                publish_time = time_element.inner_text() if time_element else ""
                
                # 提取描述
                description_element = article.query_selector(selectors["description"])
                description = description_element.inner_text() if description_element else ""
                
                # 建立並保存新文章
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
                page_new_articles += 1
                logger.info(f"已新增文章: {title}")
            except Exception as e:
                logger.error(f"處理文章時發生錯誤: {str(e)}")
        
        # 儲存整批新增項目
        if page_new_articles > 0:
            self._save_json(self.lists, self.lists_file)
            logger.info(f"已儲存 {page_new_articles} 篇新文章到列表")
        
        return page_new_articles

    def _handle_popups(self) -> bool:
        """處理彈窗，避免使用含有 :contains 的選擇器"""
        # 先檢查是否遇到 Bloomberg 的人機驗證頁面
        if self._handle_hold_button_verification():
            logger.info("已處理 Bloomberg 按住不放驗證")
            return True

        if self.config["scraping"]["auto_close_popups"]:
            try:
                # 使用標準的 CSS 選擇器，避免使用不支援的選擇器語法
                popup_selectors = {
                    'popup': ['.modal', '.popup', '[id*="popup"]', '[class*="popup"]', '.overlay', '.dialog'],
                    'paywall': ['.paywall', '.require-subscription', '.subscription-banner'],
                    'cookie': ['.cookie-banner', '.cookie-policy', '[class*="cookie"]', '.cookie-consent', '.cookie-notice'],
                    'newsletter': ['.newsletter-signup', '.subscription-form'],
                    'close': [
                        '.close', '.dismiss', '.close-button', '[aria-label="Close"]',
                        '.modal-close', '.btn-close', 'button[data-dismiss="modal"]',
                        'button.media-ui-IconButton_wrapper-ZtMlyZ3p34k-[aria-label="Close"]'
                    ],
                    'accept': [
                        '.accept-cookies', '.accept-button', '.agree-button',
                        'button.accept', 'button.ok', 'button.confirm',
                        'button[value="Accept"]', 'button.allow'
                    ],
                    # 針對 XPath 的按鈕處理（不含 :contains 操作）
                    'xpath_buttons': [
                        "//button[text()='OK']",
                        "//button[text()='Accept']",
                        "//button[text()='Close']",
                        "//button[text()='Allow']",
                        "//button[text()='I Agree']"
                    ]
                }
                
                # 先嘗試標準 CSS 選擇器
                popups_handled = check_and_handle_popup(self.crawler.page, popup_selectors)
                
                # 如果沒有成功處理，嘗試使用 XPath 選擇器手動處理
                if not popups_handled:
                    logger.debug("嘗試使用 XPath 處理彈窗")
                    for xpath in popup_selectors['xpath_buttons']:
                        try:
                            # 檢查是否存在匹配的按鈕
                            button = self.crawler.page.query_selector(f"xpath={xpath}")
                            if button:
                                logger.info(f"找到彈窗按鈕: {xpath}")
                                button.click()
                                self.human_like.random_delay(0.5, 1.0)
                                popups_handled = True
                                break
                        except Exception as e:
                            logger.debug(f"XPath 按鈕點擊失敗: {xpath}, 錯誤: {str(e)}")
                
                if popups_handled:
                    logger.info("已自動關閉彈窗/廣告")
                    return True
                    
            except Exception as e:
                # 特別處理可能的 :contains 選擇器錯誤
                error_str = str(e)
                if "querySelectorAll" in error_str and ":contains" in error_str:
                    logger.error(
                        "偵測到不合法的 CSS selector ':contains'，"
                        "請檢查 popup handler 的選擇器設定，移除所有 :contains 用法"
                    )
                else:
                    logger.warning(f"處理彈窗時出錯: {error_str}")
        
        return False

    def _handle_hold_button_verification(self) -> bool:
        """處理 Bloomberg 特殊的按住不放驗證
        
        Bloomberg 網站有時會顯示「We've detected unusual activity」頁面，
        要求使用者按住「按住不放」按鈕一段時間才能通過驗證。
        
        返回:
            bool: 如果檢測到並處理了驗證頁面則返回 True，否則返回 False
        """
        try:
            # 首先保存完整頁面截圖和源碼到指定日誌目錄，方便診斷問題
            try:
                logs_dir = Path("logs")
                logs_dir.mkdir(exist_ok=True)
                timestamp = int(time.time())
                
                # 保存截圖
                screenshot_path = f"logs/page_capture_{timestamp}.png"
                self.crawler.screenshot(path=screenshot_path)
                
                # 保存頁面源碼
                html_path = f"logs/page_html_{timestamp}.html"
                html_content = self.crawler.page.content()
                with open(html_path, "w", encoding="utf-8") as f:
                    f.write(html_content)
                    
                logger.info(f"已保存頁面截圖至 {screenshot_path} 和源碼至 {html_path}")
            except Exception as e:
                logger.debug(f"保存頁面診斷信息出錯: {str(e)}")
            
            # 檢測是否是403頁面
            try:
                http_status_code = 0
                # 嘗試從頁面標題解析狀態碼
                title = self.crawler.page.title()
                if "403" in title or "Forbidden" in title:
                    logger.info("從標題檢測到403頁面")
                    return self._handle_403_error()
                    
                # 從頁面內容檢測是否為403錯誤
                content = self.crawler.page.content()
                if "403 Forbidden" in content or "Access Denied" in content:
                    logger.info("從內容檢測到403頁面")
                    return self._handle_403_error()
            except Exception:
                pass
            
            # 檢查是否存在驗證頁面特徵
            verification_detected = False
            
            # 檢查頁面上是否有明確的反爬蟲驗證提示
            try:
                page_text = self.crawler.page.inner_text('body')
                verification_phrases = [
                    "We've detected unusual activity",
                    "我們檢測到不尋常的活動",
                    "按住不放",
                    "Hold to continue",
                    "Please hold the button",
                    "Press and hold",
                    "Verify you're not a robot"
                ]
                
                for phrase in verification_phrases:
                    if phrase in page_text:
                        verification_detected = True
                        logger.info(f"檢測到驗證頁面關鍵詞: '{phrase}'")
                        break
            except Exception:
                pass

            # 如果沒有檢測到驗證頁面，嘗試查找驗證按鈕
            if not verification_detected:
                # 嘗試直接查找驗證按鈕的存在
                button_texts = ["按住不放", "Hold", "Hold And Release", "Press"]
                for text in button_texts:
                    try:
                        button = self.crawler.page.get_by_text(text, exact=False)
                        if button.count() > 0 and button.first.is_visible():
                            verification_detected = True
                            logger.info(f"找到可能的驗證按鈕: '{text}'")
                            break
                    except Exception:
                        pass
                        
            # 最後嘗試通過頁面 URL 來判斷
            try:
                url = self.crawler.page.url
                if "captcha" in url or "verification" in url or "challenge" in url:
                    verification_detected = True
                    logger.info(f"從 URL 檢測到潛在的驗證頁面: {url}")
            except Exception:
                pass

            # 如果沒有檢測到驗證頁面，返回 False
            if not verification_detected:
                logger.info("沒有檢測到驗證頁面")
                return False
                
            # 直接打印頁面上所有按鈕的文字，用於診斷
            try:
                logger.info("頁面上的所有按鈕:")
                buttons = self.crawler.page.query_selector_all("button")
                for i, button in enumerate(buttons):
                    try:
                        text = button.inner_text()
                        is_visible = button.is_visible()
                        logger.info(f"按鈕 {i+1}: '{text}' (可見: {is_visible})")
                    except:
                        pass
            except Exception as e:
                logger.debug(f"列出按鈕時出錯: {str(e)}")
            
            logger.info("嘗試處理 Bloomberg 驗證...")
            
            # 使用更靈活的方法查找和處理驗證按鈕
            verification_button = None
            
            # 1. 嘗試通過內容查找
            try:
                content_matches = [
                    self.crawler.page.get_by_text("按住不放"),
                    self.crawler.page.get_by_text("Hold"),
                    self.crawler.page.get_by_text("Press and hold"),
                    self.crawler.page.get_by_role("button", name="Hold"),
                    self.crawler.page.get_by_role("button", name="按住不放")
                ]
                
                for match in content_matches:
                    try:
                        if match.count() > 0:
                            verification_button = match.first
                            if verification_button.is_visible():
                                logger.info("找到驗證按鈕通過文本內容")
                                break
                            verification_button = None
                    except Exception:
                        pass
            except Exception as e:
                logger.debug(f"通過內容查找按鈕時出錯: {str(e)}")
                
            # 2. 如果找不到明確的按鈕，嘗試模糊匹配
            if not verification_button:
                try:
                    # 獲取所有可見按鈕
                    buttons = self.crawler.page.query_selector_all("button")
                    
                    for button in buttons:
                        try:
                            # 檢查按鈕是否可見
                            if not button.is_visible():
                                continue
                                
                            # 檢查按鈕文本
                            text = button.inner_text().strip().lower()
                            if any(keyword in text for keyword in ["按住", "按住不放", "hold", "press"]):
                                verification_button = button
                                logger.info(f"找到驗證按鈕通過模糊匹配: '{text}'")
                                break
                        except Exception:
                            continue
                except Exception as e:
                    logger.debug(f"模糊匹配按鈕時出錯: {str(e)}")
            
            # 3. 如果仍然找不到按鈕，嘗試針對具體頁面結構查找
            if not verification_button:
                try:
                    # 常見容器中的按鈕
                    containers = [
                        ".captcha-container button",
                        ".verification-container button",
                        ".challenge-container button",
                        ".modal-body button",
                        ".main-container button",
                        ".container button"
                    ]
                    
                    for container in containers:
                        try:
                            buttons = self.crawler.page.query_selector_all(container)
                            if buttons and len(buttons) > 0:
                                for button in buttons:
                                    if button.is_visible():
                                        verification_button = button
                                        logger.info(f"找到驗證按鈕通過容器選擇器: '{container}'")
                                        break
                                if verification_button:
                                    break
                        except Exception:
                            continue
                except Exception as e:
                    logger.debug(f"通過容器查找按鈕時出錯: {str(e)}")
            
            # 如果無法找到按鈕，則嘗試直接操作頁面中央位置
            if not verification_button:
                logger.warning("無法找到具體的驗證按鈕，嘗試點擊頁面中央")
                try:
                    # 獲取頁面尺寸
                    viewport = self.crawler.page.viewport_size
                    center_x = viewport["width"] // 2
                    center_y = viewport["height"] // 2
                    
                    # 模擬在頁面中央按住滑鼠
                    self.crawler.page.mouse.move(center_x, center_y)
                    self.crawler.page.wait_for_timeout(1000)
                    self.crawler.page.mouse.down()
                    
                    # 保持按住 8 秒
                    logger.info("在頁面中央按住滑鼠 8 秒...")
                    self.crawler.page.wait_for_timeout(8000)
                    
                    # 釋放滑鼠
                    self.crawler.page.mouse.up()
                    logger.info("已釋放滑鼠")
                    
                    # 等待頁面可能的變化
                    self.crawler.page.wait_for_timeout(3000)
                    
                    # 檢查頁面是否變化
                    current_url = self.crawler.page.url
                    if "captcha" not in current_url and "verification" not in current_url:
                        logger.info("頁面已變化，可能驗證成功")
                        return True
                    
                    return False
                except Exception as e:
                    logger.error(f"嘗試點擊頁面中央時出錯: {str(e)}")
                    return False
            
            # 執行按住操作
            try:
                # 確保按鈕在視窗內
                verification_button.scroll_into_view_if_needed()
                self.crawler.page.wait_for_timeout(1000)
                
                # 獲取按鈕位置
                box = verification_button.bounding_box()
                if not box:
                    logger.error("無法獲取按鈕位置")
                    return False
                
                center_x = box["x"] + box["width"] / 2
                center_y = box["y"] + box["height"] / 2
                
                # 先嘗試點擊按鈕（有時需要先點擊激活）
                self.crawler.page.mouse.click(center_x, center_y)
                self.crawler.page.wait_for_timeout(1000)
                
                # 移動到按鈕上方
                self.crawler.page.mouse.move(center_x, center_y)
                self.crawler.page.wait_for_timeout(500)
                
                # 按下滑鼠
                logger.info("開始按住按鈕...")
                self.crawler.page.mouse.down()
                
                # 隨機生成較長的按住時間 (8-10秒)，增加成功率
                hold_time = random.uniform(8000, 10000)
                logger.info(f"按住滑鼠 {hold_time/1000:.1f} 秒...")
                self.crawler.page.wait_for_timeout(int(hold_time))
                
                # 釋放滑鼠按鍵
                self.crawler.page.mouse.up()
                logger.info("已釋放滑鼠按鈕")
                
                # 等待頁面可能的跳轉或變化
                logger.info("等待頁面變化...")
                self.crawler.page.wait_for_timeout(5000)
                
                # 檢查頁面是否變化
                try:
                    current_url = self.crawler.page.url
                    page_text = self.crawler.page.inner_text('body')
                    
                    # 檢查是否還有驗證相關文字
                    verification_still_present = any(phrase in page_text for phrase in verification_phrases)
                    
                    if not verification_still_present:
                        logger.info("驗證成功，頁面已變化!")
                        return True
                    else:
                        logger.warning("驗證可能未成功，頁面仍顯示驗證內容")
                        return False
                except Exception as e:
                    logger.error(f"檢查驗證結果時出錯: {str(e)}")
                    return False
                
            except Exception as e:
                logger.error(f"執行按住操作時出錯: {str(e)}")
                return False
                
        except Exception as e:
            logger.error(f"處理 Bloomberg 驗證頁面時出錯: {str(e)}")
            return False

    def _handle_403_error(self) -> bool:
        """處理 403 Forbidden 錯誤
        
        Bloomberg 網站經常返回 403 錯誤來阻止爬蟲。
        此方法嘗試通過各種方式來繞過這個限制。
        
        返回:
            bool: 如果成功處理了 403 錯誤則返回 True，否則返回 False
        """
        try:
            # 檢查頁面內容是否包含 403 或 "Access Denied" 相關文字
            page_content = self.crawler.page.content().lower()
            page_text = self.crawler.page.inner_text('body').lower()
            
            is_403_page = (
                "403" in page_text or
                "forbidden" in page_text or 
                "access denied" in page_text or
                "403" in page_content or
                "forbidden" in page_content or
                "access denied" in page_content
            )
            
            if not is_403_page:
                return False
            
            logger.warning("檢測到 403 錯誤頁面，嘗試繞過...")
            
            # 保存錯誤頁面截圖
            try:
                timestamp = int(time.time())
                self.crawler.screenshot(path=f"logs/error403_{timestamp}.png")
            except Exception:
                pass
            
            # 方法 1: 清除所有 cookies 並重新載入
            try:
                self.crawler.context.clear_cookies()
                logger.info("已清除所有 cookies")
                self.crawler.page.reload(wait_until="domcontentloaded")
                self.crawler.wait_for_load_state("networkidle")
                
                # 檢查是否仍然有 403 錯誤
                if "403" not in self.crawler.page.content() and "access denied" not in self.crawler.page.content().lower():
                    logger.info("清除 cookies 後成功繞過 403 錯誤")
                    return True
            except Exception as e:
                logger.debug(f"清除 cookies 方法失敗: {str(e)}")
            
            # 方法 2: 修改 User-Agent 並重新載入
            try:
                current_url = self.crawler.page.url
                # 選擇一個非常普通的 Chrome/Firefox User-Agent
                new_user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
                
                # 通過 JavaScript 修改 User-Agent
                self.crawler.page.evaluate(f"""
                    () => {{
                        Object.defineProperty(navigator, 'userAgent', {{
                            get: function() {{ return '{new_user_agent}'; }}
                        }});
                    }}
                """)
                
                logger.info(f"已修改 User-Agent")
                self.crawler.page.reload(wait_until="domcontentloaded")
                
                # 檢查是否仍然有 403 錯誤
                if "403" not in self.crawler.page.content() and "access denied" not in self.crawler.page.content().lower():
                    logger.info("修改 User-Agent 後成功繞過 403 錯誤")
                    return True
            except Exception as e:
                logger.debug(f"修改 User-Agent 方法失敗: {str(e)}")
                
            # 方法 3: 等待後再次嘗試
            logger.info("等待 5 秒後再嘗試...")
            self.crawler.page.wait_for_timeout(5000)
            self.crawler.page.reload(wait_until="domcontentloaded")
            
            # 檢查是否仍然有 403 錯誤
            if "403" not in self.crawler.page.content() and "access denied" not in self.crawler.page.content().lower():
                logger.info("等待後重試成功繞過 403 錯誤")
                return True
                
            # 方法 4: 使用 JS fetch API 嘗試繞過
            try:
                logger.info("使用 fetch API 嘗試繞過 403 錯誤...")
                
                # 使用自定義標頭進行 fetch 請求
                html_content = self.crawler.page.evaluate("""
                    async (url) => {
                        try {
                            const response = await fetch(url, {
                                method: 'GET',
                                headers: {
                                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/122.0.0.0',
                                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                                    'Accept-Language': 'en-US,en;q=0.9',
                                    'Referer': 'https://www.google.com/',
                                    'DNT': '1',
                                    'Connection': 'keep-alive',
                                    'Upgrade-Insecure-Requests': '1'
                                },
                                credentials: 'include'
                            });
                            
                            if (!response.ok) {
                                return null;
                            }
                            
                            return await response.text();
                        } catch(e) {
                            return null;
                        }
                    }
                """, current_url)
                
                if html_content:
                    # 如果成功獲取內容，將其設置為當前頁面內容
                    self.crawler.page.set_content(html_content)
                    logger.info("成功使用 fetch API 繞過 403 錯誤")
                    return True
            except Exception as e:
                logger.debug(f"使用 fetch API 方法失敗: {str(e)}")
            
            logger.warning("所有嘗試繞過 403 錯誤的方法都失敗了")
            return False
            
        except Exception as e:
            logger.debug(f"處理 403 錯誤時出現問題: {str(e)}")
            return False

    def goto_url_with_retry(self, url: str, max_retries: int = 3, wait_time: int = 3) -> bool:
        """訪問 URL 並處理可能的阻礙
        
        參數:
            url: 要訪問的 URL
            max_retries: 最大重試次數
            wait_time: 重試間隔時間（秒）
            
        返回:
            bool: 如果成功訪問則返回 True，否則返回 False
        """
        for attempt in range(max_retries):
            try:
                logger.info(f"正在訪問: {url} (嘗試 {attempt + 1}/{max_retries})")
                
                # 訪問頁面前先清除 cookies 嘗試解決 403 問題
                if attempt > 0:
                    try:
                        self.crawler.context.clear_cookies()
                        logger.info("已清除 cookies 嘗試避免 403 錯誤")
                    except Exception:
                        pass
                
                # 訪問頁面
                response = self.crawler.goto(url, wait_until="domcontentloaded", timeout=60000)
                
                # 檢查狀態碼
                status_code = response.status if response else 0
                if status_code == 403:
                    logger.warning("收到 403 Forbidden 響應，嘗試處理")
                    if self._handle_403_error():
                        logger.info("已成功處理 403 錯誤")
                    else:
                        logger.warning("處理 403 錯誤失敗")
                        
                # 優先檢查是否需要驗證
                if self._handle_hold_button_verification():
                    logger.info("已處理驗證頁面")
                    return True
                
                # 等待頁面載入
                try:
                    self.crawler.wait_for_load_state("networkidle", timeout=30000)
                except Exception as e:
                    logger.warning(f"等待頁面載入時出錯: {str(e)}，但繼續執行")
                
                # 檢查頁面是否為 403 錯誤頁面
                if self._handle_403_error():
                    logger.info("處理了 403 錯誤頁面")
                
                # 處理彈窗
                if self._handle_popups():
                    logger.info("處理了彈窗")
                
                # 再次檢查驗證
                if self._handle_hold_button_verification():
                    logger.info("處理了延遲出現的驗證頁面")
                    return True
                
                # 確認頁面是否可訪問（不是錯誤頁面或驗證頁面）
                page_text = self.crawler.page.inner_text('body').lower()
                error_phrases = [
                    "403 forbidden", 
                    "access denied",
                    "unusual activity",
                    "we've detected unusual",
                    "不尋常的活動"
                ]
                
                if not any(phrase in page_text for phrase in error_phrases):
                    logger.info(f"成功訪問 URL: {url}")
                    return True
                else:
                    logger.warning("頁面似乎仍有錯誤或需要驗證")
                    # 保存頁面截圖和源碼用於診斷
                    try:
                        timestamp = int(time.time())
                        self.crawler.screenshot(path=f"logs/error_page_{timestamp}.png")
                        with open(f"logs/error_html_{timestamp}.html", "w", encoding="utf-8") as f:
                            f.write(self.crawler.page.content())
                        logger.info(f"已保存錯誤頁面診斷信息")
                    except Exception:
                        pass
                    
                    # 如果是最後一次嘗試，返回 False
                    if attempt == max_retries - 1:
                        return False
                
            except Exception as e:
                logger.error(f"訪問 {url} 時出錯: {str(e)}")
                
            # 如果不是最後一次嘗試，等待後重試
            if attempt < max_retries - 1:
                wait_seconds = wait_time * (attempt + 1)  # 漸進式增加等待時間
                logger.info(f"等待 {wait_seconds} 秒後重試...")
                time.sleep(wait_seconds)
        
        logger.error(f"多次嘗試後仍無法成功訪問 {url}")
        return False

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
            # 使用重試機制訪問文章頁面
            logger.info(f"正在訪問文章頁面: {url}")
            if not self.goto_url_with_retry(url, max_retries=3):
                logger.error(f"無法成功訪問文章頁面: {url}")
                return None
            
            # 模擬人類滾動和閱讀行為
            self.human_like.scroll_page(self.crawler.page)
            self.human_like.random_delay(1.5, 3)
            self.human_like.scroll_page(self.crawler.page)
            
            # 等待文章內容載入
            self.crawler.page.wait_for_selector(selectors["wrapper"], timeout=30000)
            time.sleep(1)
            
            # 獲取文章包裝元素
            wrapper = self.crawler.page.query_selector(selectors["wrapper"])
            if not wrapper:
                logger.warning("無法找到文章內容")
                return None
                
            # 提取文章內容
            category_elem = self.crawler.page.query_selector(selectors["category"])
            category = category_elem.inner_text() if category_elem else ""
            
            title_elem = self.crawler.page.query_selector(selectors["title"])
            title = title_elem.inner_text() if title_elem else ""
            
            subtitle_elem = self.crawler.page.query_selector(selectors["subtitle"])
            subtitle = subtitle_elem.inner_text() if subtitle_elem else ""
            
            image_elem = self.crawler.page.query_selector(selectors["image"])
            image_url = image_elem.get_attribute("src") if image_elem else ""
            
            image_caption_elem = self.crawler.page.query_selector(selectors["image_caption"])
            image_caption = image_caption_elem.inner_text() if image_caption_elem else ""
            
            # 處理多個作者
            author_elems = self.crawler.page.query_selector_all(selectors["author"])
            authors = [author.inner_text() for author in author_elems] if author_elems else []
            author = ", ".join(authors)
            
            publish_time_elem = self.crawler.page.query_selector(selectors["publish_time"])
            publish_time = publish_time_elem.get_attribute("datetime") if publish_time_elem else ""
            
            update_time_elem = self.crawler.page.query_selector(selectors["update_time"])
            update_time = update_time_elem.get_attribute("datetime") if update_time_elem else ""
            
            # 提取正文內容
            content_paras = self.crawler.page.query_selector_all(selectors["content"])
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
            # 特別處理可能的 :contains 選擇器錯誤
            error_str = str(e)
            if "querySelectorAll" in error_str and ":contains" in error_str:
                logger.error(
                    "偵測到不合法的 CSS selector ':contains'，"
                    "請檢查 popup handler 的選擇器設定，移除所有 :contains 用法"
                    f"（如 button:contains('Allow')、button:contains('OK') 等）。錯誤信息: {error_str}"
                )
            else:
                logger.error(f"爬取文章內容時發生錯誤: {error_str}")
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
            try:
                # 保存最終的 session 狀態
                if hasattr(self, 'storage_file'):
                    try:
                        self.crawler.save_storage(str(self.storage_file))
                        logger.info(f"已儲存 session 狀態到 {self.storage_file}")
                    except Exception as e:
                        logger.warning(f"儲存 session 狀態時發生錯誤: {str(e)}")
                
                # 使用標準的 close 方法，PlaywrightBase 應該會處理所有清理工作
                try:
                    self.crawler.close()
                    logger.info("爬蟲已正常關閉")
                except AttributeError:
                    logger.warning("使用備用方法關閉爬蟲...")
                    if hasattr(self.crawler, '_browser') and self.crawler._browser:
                        self.crawler._browser.close()
                        logger.info("已關閉瀏覽器")
                    if hasattr(self.crawler, '_playwright') and self.crawler._playwright:
                        self.crawler._playwright.stop()
                        logger.info("已停止 Playwright")
            except Exception as e:
                logger.error(f"關閉爬蟲時發生錯誤: {str(e)}")
            finally:
                self.crawler = None
        logger.info("爬蟲資源已釋放")

def main():
    """主函數"""
    try:
        logger.info("=== 開始執行 Bloomberg 爬蟲程式 ===")
        
        # 建立爬蟲實例
        scraper = BloombergScraper()
        scraper.init_crawler()  # 確保爬蟲被初始化
        
        if scraper.need_login:
            logger.info("檢查登入憑證是否已設定...")
            if hasattr(scraper, 'email') and hasattr(scraper, 'password'):
                logger.info(f"已設定登入憑證，電子信箱: {scraper.email[:3]}...{scraper.email.split('@')[1]}")
                # 強制執行登入
                scraper.login()
            else:
                logger.warning("未設定登入憑證，將以訪客模式進行爬取")
        
        # 使用標準的 try-finally 確保資源釋放
        try:
            # 爬取搜尋結果
            try:
                logger.info("開始爬取搜尋結果...")
                keyword = "gold usd"
                scraper.scrape_search_results(keyword)
            except Exception as e:
                logger.error(f"爬取搜尋結果時發生錯誤: {str(e)}")
            
            # 爬取文章內容
            try:
                logger.info("開始爬取文章內容...")
                scraper.scrape_all_articles()
            except Exception as e:
                logger.error(f"爬取文章內容時發生錯誤: {str(e)}")
            
            logger.info("=== Bloomberg 爬蟲程式執行完成 ===")
            
        except Exception as e:
            logger.error(f"程式執行過程中發生錯誤: {str(e)}")
        finally:
            # 確保資源被釋放，即使出現了未處理的異常
            if hasattr(scraper, 'close'):
                scraper.close()
                
    except Exception as e:
        logger.critical(f"程式初始化過程中發生致命錯誤: {str(e)}")

if __name__ == "__main__":
    main()
