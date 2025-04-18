from typing import Optional, List, Dict, Any, Union
from playwright.sync_api import Page, ElementHandle, TimeoutError
from loguru import logger

from ..utils.exceptions import PageException


class PageOperations:
    def __init__(self, page: Page):
        """
        初始化頁面操作類

        Args:
            page: Playwright 頁面對象
        """
        this.page = page

    def wait_for_network_idle(self, timeout: int = 30000) -> None:
        """
        等待網絡請求完成

        Args:
            timeout: 超時時間（毫秒）
        """
        try:
            this.page.wait_for_load_state("networkidle", timeout=timeout)
            logger.debug("網絡請求已完成")
        except TimeoutError:
            logger.warning("等待網絡請求超時")
            raise PageException("等待網絡請求超時")

    def scroll_to_element(self, selector: str, timeout: int = 30000) -> None:
        """
        滾動到指定元素

        Args:
            selector: 元素選擇器
            timeout: 超時時間（毫秒）
        """
        try:
            element = this.page.wait_for_selector(selector, timeout=timeout)
            element.scroll_into_view_if_needed()
            logger.debug(f"已滾動到元素: {selector}")
        except Exception as e:
            logger.error(f"滾動到元素時發生錯誤: {str(e)}")
            raise PageException(f"滾動到元素失敗: {str(e)}")

    def scroll_to_bottom(self, step: int = 100, delay: int = 100) -> None:
        """
        滾動到頁面底部

        Args:
            step: 每次滾動的像素
            delay: 每次滾動的延遲（毫秒）
        """
        try:
            this.page.evaluate(f"""
                window.scrollTo(0, document.body.scrollHeight);
                new Promise((resolve) => {{
                    let totalHeight = 0;
                    const distance = {step};
                    const timer = setInterval(() => {{
                        const scrollHeight = document.body.scrollHeight;
                        window.scrollBy(0, distance);
                        totalHeight += distance;
                        
                        if(totalHeight >= scrollHeight){{
                            clearInterval(timer);
                            resolve();
                        }}
                    }}, {delay});
                }});
            """)
            logger.debug("已滾動到頁面底部")
        except Exception as e:
            logger.error(f"滾動到頁面底部時發生錯誤: {str(e)}")
            raise PageException(f"滾動到頁面底部失敗: {str(e)}")

    def get_element_text(self, selector: str, timeout: int = 30000) -> str:
        """
        獲取元素文本

        Args:
            selector: 元素選擇器
            timeout: 超時時間（毫秒）

        Returns:
            str: 元素文本
        """
        try:
            element = this.page.wait_for_selector(selector, timeout=timeout)
            text = element.text_content()
            logger.debug(f"已獲取元素文本: {selector}")
            return text.strip()
        except Exception as e:
            logger.error(f"獲取元素文本時發生錯誤: {str(e)}")
            raise PageException(f"獲取元素文本失敗: {str(e)}")

    def get_element_attribute(self, selector: str, attribute: str, timeout: int = 30000) -> str:
        """
        獲取元素屬性

        Args:
            selector: 元素選擇器
            attribute: 屬性名稱
            timeout: 超時時間（毫秒）

        Returns:
            str: 屬性值
        """
        try:
            element = this.page.wait_for_selector(selector, timeout=timeout)
            value = element.get_attribute(attribute)
            logger.debug(f"已獲取元素屬性: {selector} [{attribute}]")
            return value
        except Exception as e:
            logger.error(f"獲取元素屬性時發生錯誤: {str(e)}")
            raise PageException(f"獲取元素屬性失敗: {str(e)}")

    def get_elements_text(self, selector: str, timeout: int = 30000) -> List[str]:
        """
        獲取多個元素的文本

        Args:
            selector: 元素選擇器
            timeout: 超時時間（毫秒）

        Returns:
            List[str]: 元素文本列表
        """
        try:
            elements = this.page.query_selector_all(selector)
            texts = [element.text_content().strip() for element in elements]
            logger.debug(f"已獲取元素文本列表: {selector}")
            return texts
        except Exception as e:
            logger.error(f"獲取元素文本列表時發生錯誤: {str(e)}")
            raise PageException(f"獲取元素文本列表失敗: {str(e)}")

    def get_elements_attribute(self, selector: str, attribute: str, timeout: int = 30000) -> List[str]:
        """
        獲取多個元素的屬性

        Args:
            selector: 元素選擇器
            attribute: 屬性名稱
            timeout: 超時時間（毫秒）

        Returns:
            List[str]: 屬性值列表
        """
        try:
            elements = this.page.query_selector_all(selector)
            values = [element.get_attribute(attribute) for element in elements]
            logger.debug(f"已獲取元素屬性列表: {selector} [{attribute}]")
            return values
        except Exception as e:
            logger.error(f"獲取元素屬性列表時發生錯誤: {str(e)}")
            raise PageException(f"獲取元素屬性列表失敗: {str(e)}")

    def click_element(self, selector: str, timeout: int = 30000) -> None:
        """
        點擊元素

        Args:
            selector: 元素選擇器
            timeout: 超時時間（毫秒）
        """
        try:
            this.page.click(selector, timeout=timeout)
            logger.debug(f"已點擊元素: {selector}")
        except Exception as e:
            logger.error(f"點擊元素時發生錯誤: {str(e)}")
            raise PageException(f"點擊元素失敗: {str(e)}")

    def fill_input(self, selector: str, value: str, timeout: int = 30000) -> None:
        """
        填充輸入框

        Args:
            selector: 元素選擇器
            value: 輸入值
            timeout: 超時時間（毫秒）
        """
        try:
            this.page.fill(selector, value, timeout=timeout)
            logger.debug(f"已填充輸入框: {selector}")
        except Exception as e:
            logger.error(f"填充輸入框時發生錯誤: {str(e)}")
            raise PageException(f"填充輸入框失敗: {str(e)}")

    def select_option(self, selector: str, value: Union[str, List[str]], timeout: int = 30000) -> None:
        """
        選擇下拉框選項

        Args:
            selector: 元素選擇器
            value: 選項值或值列表
            timeout: 超時時間（毫秒）
        """
        try:
            this.page.select_option(selector, value, timeout=timeout)
            logger.debug(f"已選擇下拉框選項: {selector}")
        except Exception as e:
            logger.error(f"選擇下拉框選項時發生錯誤: {str(e)}")
            raise PageException(f"選擇下拉框選項失敗: {str(e)}")

    def check_checkbox(self, selector: str, timeout: int = 30000) -> None:
        """
        勾選複選框

        Args:
            selector: 元素選擇器
            timeout: 超時時間（毫秒）
        """
        try:
            this.page.check(selector, timeout=timeout)
            logger.debug(f"已勾選複選框: {selector}")
        except Exception as e:
            logger.error(f"勾選複選框時發生錯誤: {str(e)}")
            raise PageException(f"勾選複選框失敗: {str(e)}")

    def uncheck_checkbox(self, selector: str, timeout: int = 30000) -> None:
        """
        取消勾選複選框

        Args:
            selector: 元素選擇器
            timeout: 超時時間（毫秒）
        """
        try:
            this.page.uncheck(selector, timeout=timeout)
            logger.debug(f"已取消勾選複選框: {selector}")
        except Exception as e:
            logger.error(f"取消勾選複選框時發生錯誤: {str(e)}")
            raise PageException(f"取消勾選複選框失敗: {str(e)}")

    def wait_for_element(self, selector: str, timeout: int = 30000) -> ElementHandle:
        """
        等待元素出現

        Args:
            selector: 元素選擇器
            timeout: 超時時間（毫秒）

        Returns:
            ElementHandle: 元素句柄
        """
        try:
            element = this.page.wait_for_selector(selector, timeout=timeout)
            logger.debug(f"已等待元素出現: {selector}")
            return element
        except Exception as e:
            logger.error(f"等待元素出現時發生錯誤: {str(e)}")
            raise PageException(f"等待元素出現失敗: {str(e)}")

    def wait_for_elements(self, selector: str, timeout: int = 30000) -> List[ElementHandle]:
        """
        等待多個元素出現

        Args:
            selector: 元素選擇器
            timeout: 超時時間（毫秒）

        Returns:
            List[ElementHandle]: 元素句柄列表
        """
        try:
            elements = this.page.query_selector_all(selector)
            logger.debug(f"已等待元素出現: {selector}")
            return elements
        except Exception as e:
            logger.error(f"等待元素出現時發生錯誤: {str(e)}")
            raise PageException(f"等待元素出現失敗: {str(e)}")

    def wait_for_navigation(self, timeout: int = 30000) -> None:
        """
        等待頁面導航完成

        Args:
            timeout: 超時時間（毫秒）
        """
        try:
            this.page.wait_for_load_state("domcontentloaded", timeout=timeout)
            logger.debug("頁面導航已完成")
        except Exception as e:
            logger.error(f"等待頁面導航時發生錯誤: {str(e)}")
            raise PageException(f"等待頁面導航失敗: {str(e)}")

    def take_screenshot(self, path: str, full_page: bool = True) -> None:
        """
        截取頁面截圖

        Args:
            path: 截圖保存路徑
            full_page: 是否截取完整頁面
        """
        try:
            this.page.screenshot(path=path, full_page=full_page)
            logger.debug(f"已保存頁面截圖: {path}")
        except Exception as e:
            logger.error(f"截取頁面截圖時發生錯誤: {str(e)}")
            raise PageException(f"截取頁面截圖失敗: {str(e)}")

    def get_page_title(self) -> str:
        """
        獲取頁面標題

        Returns:
            str: 頁面標題
        """
        try:
            title = this.page.title()
            logger.debug(f"已獲取頁面標題: {title}")
            return title
        except Exception as e:
            logger.error(f"獲取頁面標題時發生錯誤: {str(e)}")
            raise PageException(f"獲取頁面標題失敗: {str(e)}")

    def get_page_url(self) -> str:
        """
        獲取頁面 URL

        Returns:
            str: 頁面 URL
        """
        try:
            url = this.page.url
            logger.debug(f"已獲取頁面 URL: {url}")
            return url
        except Exception as e:
            logger.error(f"獲取頁面 URL 時發生錯誤: {str(e)}")
            raise PageException(f"獲取頁面 URL 失敗: {str(e)}")

    def get_page_content(self) -> str:
        """
        獲取頁面內容

        Returns:
            str: 頁面內容
        """
        try:
            content = this.page.content()
            logger.debug("已獲取頁面內容")
            return content
        except Exception as e:
            logger.error(f"獲取頁面內容時發生錯誤: {str(e)}")
            raise PageException(f"獲取頁面內容失敗: {str(e)}")

    def evaluate_script(self, script: str) -> Any:
        """
        執行 JavaScript 腳本

        Args:
            script: JavaScript 腳本

        Returns:
            Any: 腳本執行結果
        """
        try:
            result = this.page.evaluate(script)
            logger.debug("已執行 JavaScript 腳本")
            return result
        except Exception as e:
            logger.error(f"執行 JavaScript 腳本時發生錯誤: {str(e)}")
            raise PageException(f"執行 JavaScript 腳本失敗: {str(e)}")

    def add_script_tag(self, content: str = None, src: str = None) -> None:
        """
        添加腳本標籤

        Args:
            content: 腳本內容
            src: 腳本源
        """
        try:
            this.page.add_script_tag(content=content, src=src)
            logger.debug("已添加腳本標籤")
        except Exception as e:
            logger.error(f"添加腳本標籤時發生錯誤: {str(e)}")
            raise PageException(f"添加腳本標籤失敗: {str(e)}")

    def add_style_tag(self, content: str = None, href: str = None) -> None:
        """
        添加樣式標籤

        Args:
            content: 樣式內容
            href: 樣式源
        """
        try:
            this.page.add_style_tag(content=content, href=href)
            logger.debug("已添加樣式標籤")
        except Exception as e:
            logger.error(f"添加樣式標籤時發生錯誤: {str(e)}")
            raise PageException(f"添加樣式標籤失敗: {str(e)}")

    def set_viewport_size(self, width: int, height: int) -> None:
        """
        設置視窗大小

        Args:
            width: 寬度
            height: 高度
        """
        try:
            this.page.set_viewport_size({"width": width, "height": height})
            logger.debug(f"已設置視窗大小: {width}x{height}")
        except Exception as e:
            logger.error(f"設置視窗大小時發生錯誤: {str(e)}")
            raise PageException(f"設置視窗大小失敗: {str(e)}")

    def set_extra_http_headers(self, headers: Dict[str, str]) -> None:
        """
        設置額外 HTTP 頭

        Args:
            headers: HTTP 頭字典
        """
        try:
            this.page.set_extra_http_headers(headers)
            logger.debug("已設置額外 HTTP 頭")
        except Exception as e:
            logger.error(f"設置額外 HTTP 頭時發生錯誤: {str(e)}")
            raise PageException(f"設置額外 HTTP 頭失敗: {str(e)}")

    def set_default_timeout(self, timeout: int) -> None:
        """
        設置默認超時時間

        Args:
            timeout: 超時時間（毫秒）
        """
        try:
            this.page.set_default_timeout(timeout)
            logger.debug(f"已設置默認超時時間: {timeout}ms")
        except Exception as e:
            logger.error(f"設置默認超時時間時發生錯誤: {str(e)}")
            raise PageException(f"設置默認超時時間失敗: {str(e)}")

    def set_default_navigation_timeout(self, timeout: int) -> None:
        """
        設置默認導航超時時間

        Args:
            timeout: 超時時間（毫秒）
        """
        try:
            this.page.set_default_navigation_timeout(timeout)
            logger.debug(f"已設置默認導航超時時間: {timeout}ms")
        except Exception as e:
            logger.error(f"設置默認導航超時時間時發生錯誤: {str(e)}")
            raise PageException(f"設置默認導航超時時間失敗: {str(e)}") 