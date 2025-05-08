import random
import asyncio
from typing import Optional
from playwright.async_api import Page, ElementHandle
from loguru import logger


class HumanLikeBehavior:
    def __init__(self):
        """初始化人類行為模擬器"""
        self.mouse_speed = {
            "min": 100,  # 最小移動時間（毫秒）
            "max": 300,  # 最大移動時間（毫秒）
        }
        self.click_delay = {
            "min": 50,   # 最小點擊延遲（毫秒）
            "max": 200,  # 最大點擊延遲（毫秒）
        }
        self.type_delay = {
            "min": 100,  # 最小輸入延遲（毫秒）
            "max": 300,  # 最大輸入延遲（毫秒）
        }

    async def move_to_element(
        self,
        page: Page,
        selector: str,
        offset_x: Optional[int] = None,
        offset_y: Optional[int] = None,
    ):
        """
        模擬人類移動鼠標到元素

        Args:
            page: Playwright 頁面對象
            selector: 元素選擇器
            offset_x: X 軸偏移量
            offset_y: Y 軸偏移量
        """
        try:
            element = await page.wait_for_selector(selector)
            if not element:
                return

            # 獲取元素位置
            box = await element.bounding_box()
            if not box:
                return

            # 計算目標位置
            target_x = box["x"] + box["width"] / 2
            target_y = box["y"] + box["height"] / 2

            if offset_x is not None:
                target_x += offset_x
            if offset_y is not None:
                target_y += offset_y

            # 獲取當前鼠標位置
            current_position = await page.evaluate("""() => {
                return {
                    x: window.mouseX || 0,
                    y: window.mouseY || 0
                };
            }""")

            # 計算移動時間
            distance = ((target_x - current_position["x"]) ** 2 + (target_y - current_position["y"]) ** 2) ** 0.5
            duration = random.uniform(self.mouse_speed["min"], self.mouse_speed["max"])
            steps = int(duration / 16)  # 約 60fps

            # 執行平滑移動
            for i in range(steps + 1):
                progress = i / steps
                current_x = current_position["x"] + (target_x - current_position["x"]) * progress
                current_y = current_position["y"] + (target_y - current_position["y"]) * progress

                await page.mouse.move(current_x, current_y)
                # 模擬真實延遲模式
                delay = random.uniform(0.01, 0.05)  # 隨機延遲 10-50ms
                await asyncio.sleep(delay)

        except Exception as e:
            logger.error(f"移動鼠標到元素時發生錯誤: {str(e)}")

    async def human_click(
        self,
        page: Page,
        selector: str,
        button: str = "left",
        click_count: int = 1,
    ):
        """
        模擬人類點擊行為

        Args:
            page: Playwright 頁面對象
            selector: 元素選擇器
            button: 鼠標按鍵
            click_count: 點擊次數
        """
        try:
            # 移動到元素
            await self.move_to_element(page, selector)

            # 隨機延遲
            delay = random.uniform(self.click_delay["min"], self.click_delay["max"]) / 1000
            await asyncio.sleep(delay)

            # 執行點擊
            await page.click(selector, button=button, click_count=click_count)

        except Exception as e:
            logger.error(f"執行人類點擊時發生錯誤: {str(e)}")

    async def human_type(
        self,
        page: Page,
        selector: str,
        text: str,
    ):
        """
        模擬人類輸入行為

        Args:
            page: Playwright 頁面對象
            selector: 元素選擇器
            text: 要輸入的文本
        """
        try:
            # 移動到元素
            await self.move_to_element(page, selector)

            # 點擊輸入框
            await self.human_click(page, selector)

            # 模擬人類輸入
            for char in text:
                delay = random.uniform(self.type_delay["min"], self.type_delay["max"]) / 1000
                await asyncio.sleep(delay)
                await page.type(selector, char)

        except Exception as e:
            logger.error(f"執行人類輸入時發生錯誤: {str(e)}")

    async def random_scroll(self, page: Page):
        """
        模擬人類隨機滾動頁面

        Args:
            page: Playwright 頁面對象
        """
        try:
            # 獲取頁面高度
            page_height = await page.evaluate("document.documentElement.scrollHeight")
            viewport_height = await page.evaluate("window.innerHeight")

            # 計算可滾動的距離
            max_scroll = page_height - viewport_height

            # 隨機滾動到頁面中間位置
            target_scroll = random.randint(0, max_scroll)
            current_scroll = 0
            steps = 20  # 滾動步數

            for i in range(steps + 1):
                progress = i / steps
                current_scroll = target_scroll * progress
                await page.evaluate(f"window.scrollTo(0, {current_scroll})")
                await asyncio.sleep(0.05)  # 50ms 延遲

        except Exception as e:
            logger.error(f"執行隨機滾動時發生錯誤: {str(e)}")

    async def random_mouse_movement(self, page: Page):
        """
        模擬人類隨機鼠標移動

        Args:
            page: Playwright 頁面對象
        """
        try:
            viewport_width = await page.evaluate("window.innerWidth")
            viewport_height = await page.evaluate("window.innerHeight")

            # 生成隨機目標位置
            target_x = random.randint(0, viewport_width)
            target_y = random.randint(0, viewport_height)

            # 獲取當前鼠標位置
            current_position = await page.evaluate("""() => {
                return {
                    x: window.mouseX || 0,
                    y: window.mouseY || 0
                };
            }""")

            # 執行平滑移動
            duration = random.uniform(self.mouse_speed["min"], self.mouse_speed["max"])
            steps = int(duration / 16)  # 約 60fps

            for i in range(steps + 1):
                progress = i / steps
                current_x = current_position["x"] + (target_x - current_position["x"]) * progress
                current_y = current_position["y"] + (target_y - current_position["y"]) * progress

                await page.mouse.move(current_x, current_y)
                await asyncio.sleep(0.016)  # 約 60fps

        except Exception as e:
            logger.error(f"執行隨機鼠標移動時發生錯誤: {str(e)}")


import random
import time
from loguru import logger
from typing import Optional

def human_scroll(page, min_times: int = 3, max_times: int = 8, min_dist: int = 300, max_dist: int = 700, sleep_min: float = 0.5, sleep_max: float = 2.0) -> None:
    """
    模擬人類隨機平滑滾動頁面
    Args:
        page: Playwright Page 物件
        min_times: 最少滾動次數
        max_times: 最多滾動次數
        min_dist: 每次最小滾動距離
        max_dist: 每次最大滾動距離
        sleep_min: 每次滾動後最小等待秒數
        sleep_max: 每次滾動後最大等待秒數
    """
    try:
        page_height = page.evaluate("() => document.body.scrollHeight")
        scroll_times = random.randint(min_times, max_times)
        for _ in range(scroll_times):
            scroll_distance = random.randint(min_dist, max_dist)
            current_position = page.evaluate("() => window.pageYOffset")
            target_position = min(current_position + scroll_distance, page_height - 800)
            page.evaluate(f"() => window.scrollTo({{top: {target_position}, behavior: 'smooth'}})")
            time.sleep(random.uniform(sleep_min, sleep_max))
        logger.info("已完成人類化滾動頁面")
    except Exception as e:
        logger.warning(f"模擬滾動頁面時發生錯誤: {str(e)}")