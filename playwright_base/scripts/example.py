import asyncio
import os
from pathlib import Path
from loguru import logger

from ..core.base import PlaywrightBase


async def main():
    # 設置日誌
    logger.add(
        "logs/example.log",
        rotation="500 MB",
        retention="10 days",
        level="INFO",
    )

    # 創建截圖目錄
    screenshots_dir = Path("screenshots")
    screenshots_dir.mkdir(exist_ok=True)

    # 初始化爬蟲實例
    async with PlaywrightBase(
        headless=False,  # 設置為 True 則使用無頭模式
        proxy=None,      # 設置代理服務器
    ) as scraper:
        try:
            # 訪問目標網站
            await scraper.navigate("https://example.com")

            # 等待頁面加載完成
            await scraper.wait_for_load_state("networkidle")

            # 截取頁面截圖
            await scraper.screenshot(
                screenshots_dir / "example.png",
                full_page=True,
            )

            # 獲取頁面標題
            title = await scraper.get_text("h1")
            logger.info(f"頁面標題: {title}")

            # 模擬人類行為：隨機滾動
            await scraper.human_like.random_scroll(scraper.page)

            # 模擬人類行為：隨機鼠標移動
            await scraper.human_like.random_mouse_movement(scraper.page)

            # 執行 JavaScript
            page_title = await scraper.evaluate("document.title")
            logger.info(f"JavaScript 獲取的標題: {page_title}")

        except Exception as e:
            logger.error(f"執行過程中發生錯誤: {str(e)}")
            raise


if __name__ == "__main__":
    asyncio.run(main()) 