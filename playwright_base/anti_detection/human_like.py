"""
模擬人類行為模組

提供模擬人類瀏覽行為的功能，例如滾動頁面、移動滑鼠、隨機延遲等。
"""

import random
import time
from typing import Dict, Any, Optional
from playwright.sync_api import Page

from playwright_base.utils.logger import setup_logger

# 設置日誌
logger = setup_logger(name=__name__)

class HumanLikeBehavior:
    """
    模擬人類瀏覽行為的類。
    提供各種方法來模擬真人使用瀏覽器的行為模式。
    """
    
    def __init__(self):
        """初始化 HumanLikeBehavior 實例"""
        self.default_config = {
            "scroll": {
                "min_scroll_times": 3,
                "max_scroll_times": 8,
                "min_scroll_distance": 300,
                "max_scroll_distance": 800,
                "min_delay": 0.5,
                "max_delay": 2.0
            },
            "mouse": {
                "min_moves": 3,
                "max_moves": 10,
                "min_delay": 0.1,
                "max_delay": 0.5
            },
            "keyboard": {
                "min_delay": 0.05,
                "max_delay": 0.2,
                "mistake_probability": 0.05
            }
        }
    
    def random_delay(self, min_delay: float = 1.0, max_delay: float = 3.0, delay_type: str = None) -> float:
        """
        隨機延遲一段時間。

        參數:
            min_delay (float): 最小延遲時間（秒）。
            max_delay (float): 最大延遲時間（秒）。
            delay_type (str): 延遲類型描述，用於日誌記錄。
            
        返回:
            float: 實際延遲時間（秒）。
        """
        delay = random.uniform(min_delay, max_delay)
        if delay_type:
            logger.debug(f"隨機延遲 {delay:.2f} 秒 ({delay_type})")
        else:
            logger.debug(f"隨機延遲 {delay:.2f} 秒")
        time.sleep(delay)
        return delay
    
    def scroll_page(self, page: Page, **kwargs) -> None:
        """
        模擬人類滾動頁面行為。

        參數:
            page (Page): Playwright 頁面對象。
            **kwargs: 可選配置參數，用於覆蓋默認配置。
        """
        # 合併配置參數
        config = self.default_config["scroll"].copy()
        config.update(kwargs)
        
        try:
            # 獲取頁面高度
            page_height = page.evaluate("""
                () => document.body.scrollHeight
            """)
            
            # 隨機滾動次數
            scroll_times = random.randint(config["min_scroll_times"], config["max_scroll_times"])
            
            logger.info(f"開始模擬人類滾動頁面，計劃滾動 {scroll_times} 次")
            
            for i in range(scroll_times):
                # 隨機滾動距離
                scroll_distance = random.randint(config["min_scroll_distance"], config["max_scroll_distance"])
                current_position = page.evaluate("() => window.pageYOffset")
                target_position = min(current_position + scroll_distance, page_height - 800)
                
                # 模擬平滑滾動
                page.evaluate(f"""
                    () => {{
                        window.scrollTo({{
                            top: {target_position}, 
                            behavior: 'smooth'
                        }});
                    }}
                """)
                
                # 隨機停頓
                delay = self.random_delay(config["min_delay"], config["max_delay"], "滾動頁面")
                
                # 模擬閱讀行為，在不同位置停留不同時間
                if i % 2 == 0 and i > 0:
                    # 偶爾模擬更長的閱讀時間
                    read_time = random.uniform(1.0, 3.0)
                    logger.debug(f"模擬閱讀，停留 {read_time:.2f} 秒")
                    time.sleep(read_time)
            
            logger.info("完成人類化滾動頁面")
            
        except Exception as e:
            logger.warning(f"模擬滾動頁面時發生錯誤: {str(e)}")
    
    def move_mouse_randomly(self, page: Page, **kwargs) -> None:
        """
        模擬隨機滑鼠移動。

        參數:
            page (Page): Playwright 頁面對象。
            **kwargs: 可選配置參數，用於覆蓋默認配置。
        """
        # 合併配置參數
        config = self.default_config["mouse"].copy()
        config.update(kwargs)
        
        try:
            # 獲取視窗大小
            viewport = page.viewport_size
            if not viewport:
                logger.warning("無法獲取視窗大小，使用默認值")
                viewport = {'width': 1280, 'height': 720}
            
            # 隨機移動次數
            move_times = random.randint(config["min_moves"], config["max_moves"])
            
            logger.debug(f"開始模擬滑鼠隨機移動，計劃移動 {move_times} 次")
            
            for i in range(move_times):
                # 隨機目標位置，避免太靠近邊緣
                x = random.randint(100, viewport['width'] - 200)
                y = random.randint(100, viewport['height'] - 200)
                
                # 移動滑鼠
                page.mouse.move(x, y)
                
                # 偶爾點擊
                if random.random() < 0.2:  # 20% 的概率點擊
                    logger.debug(f"隨機點擊位置: ({x}, {y})")
                    page.mouse.click(x, y, delay=random.randint(50, 150))
                
                # 隨機延遲
                self.random_delay(config["min_delay"], config["max_delay"], "滑鼠移動")
            
            logger.debug("完成滑鼠隨機移動")
            
        except Exception as e:
            logger.warning(f"模擬滑鼠移動時發生錯誤: {str(e)}")
    
    def type_humanly(self, page: Page, selector: str, text: str, **kwargs) -> None:
        """
        模擬人類輸入文字，包含打字錯誤和修正。

        參數:
            page (Page): Playwright 頁面對象。
            selector (str): 要輸入文字的元素選擇器。
            text (str): 要輸入的文字。
            **kwargs: 可選配置參數，用於覆蓋默認配置。
        """
        # 合併配置參數
        config = self.default_config["keyboard"].copy()
        config.update(kwargs)
        
        try:
            # 確保元素存在並可見
            page.wait_for_selector(selector, state="visible")
            
            # 點擊元素以獲取焦點
            page.click(selector)
            
            # 清空輸入框
            page.press(selector, "Control+a")  # 全選
            page.press(selector, "Backspace")  # 刪除
            
            logger.debug(f"開始模擬人類輸入文字: {text[:10]}...")
            
            for char in text:
                # 隨機產生打字錯誤
                if random.random() < config["mistake_probability"]:
                    # 輸入錯誤字符
                    wrong_char = self._get_adjacent_key(char)
                    page.type(selector, wrong_char, delay=self._get_typing_delay(config))
                    
                    # 短暫延遲後修正
                    time.sleep(random.uniform(0.1, 0.3))
                    page.press(selector, "Backspace")
                    
                    # 輸入正確字符
                    page.type(selector, char, delay=self._get_typing_delay(config))
                else:
                    # 正常輸入
                    page.type(selector, char, delay=self._get_typing_delay(config))
            
            logger.debug("完成人類化文字輸入")
            
        except Exception as e:
            logger.warning(f"模擬人類輸入時發生錯誤: {str(e)}")
    
    def _get_typing_delay(self, config: Dict[str, Any]) -> float:
        """獲取打字延遲時間"""
        return random.uniform(config["min_delay"] * 1000, config["max_delay"] * 1000)
    
    def _get_adjacent_key(self, char: str) -> str:
        """模擬鍵盤上的臨近按鍵"""
        # 簡化版鍵盤映射
        keyboard_map = {
            'q': ['w', 'a', '1'],
            'w': ['q', 'e', 's', '2'],
            'e': ['w', 'r', 'd', '3'],
            'r': ['e', 't', 'f', '4'],
            't': ['r', 'y', 'g', '5'],
            'y': ['t', 'u', 'h', '6'],
            'u': ['y', 'i', 'j', '7'],
            'i': ['u', 'o', 'k', '8'],
            'o': ['i', 'p', 'l', '9'],
            'p': ['o', '[', ';', '0'],
            'a': ['q', 's', 'z'],
            's': ['w', 'a', 'd', 'x'],
            'd': ['e', 's', 'f', 'c'],
            'f': ['r', 'd', 'g', 'v'],
            'g': ['t', 'f', 'h', 'b'],
            'h': ['y', 'g', 'j', 'n'],
            'j': ['u', 'h', 'k', 'm'],
            'k': ['i', 'j', 'l', ','],
            'l': ['o', 'k', ';', '.'],
            'z': ['a', 'x'],
            'x': ['z', 's', 'c'],
            'c': ['x', 'd', 'v'],
            'v': ['c', 'f', 'b'],
            'b': ['v', 'g', 'n'],
            'n': ['b', 'h', 'm'],
            'm': ['n', 'j', ','],
            ' ': [' ']  # 空格鍵通常不會出錯
        }
        
        # 為大寫字母添加映射
        for key in list(keyboard_map.keys()):
            if key.isalpha():
                keyboard_map[key.upper()] = [k.upper() for k in keyboard_map[key] if k.isalpha()]
        
        # 數字和符號
        for i in range(10):
            str_i = str(i)
            keyboard_map[str_i] = [str((i+1) % 10), str((i-1) % 10)]
        
        # 查找臨近按鍵，若不存在則返回原字符
        adjacent_keys = keyboard_map.get(char, [char])
        return random.choice(adjacent_keys)
    
    def perform_random_actions(self, page: Page) -> None:
        """
        執行一系列隨機操作，包括滾動、移動滑鼠等。
        
        參數:
            page (Page): Playwright 頁面對象。
        """
        try:
            logger.info("執行隨機人類行為模擬...")
            
            # 隨機操作列表
            actions = [
                (0.7, lambda: self.scroll_page(page)),  # 70% 概率滾動頁面
                (0.3, lambda: self.move_mouse_randomly(page)),  # 30% 概率移動滑鼠
            ]
            
            # 執行 1-3 次隨機操作
            for _ in range(random.randint(1, 3)):
                # 根據權重選擇操作
                action = self._weighted_choice([action for _, action in actions], 
                                             [weight for weight, _ in actions])
                action()
                
                # 操作之間的隨機延遲
                self.random_delay(0.5, 2.0, "操作間隔")
            
            logger.info("隨機人類行為模擬完成")
            
        except Exception as e:
            logger.warning(f"執行隨機行為時發生錯誤: {str(e)}")
    
    def _weighted_choice(self, choices, weights):
        """根據權重隨機選擇"""
        total = sum(weights)
        threshold = random.uniform(0, total)
        current = 0
        for choice, weight in zip(choices, weights):
            current += weight
            if current > threshold:
                return choice
        return choices[-1]  # 防止浮點誤差