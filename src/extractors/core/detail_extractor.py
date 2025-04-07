from typing import Dict, List, Any, Optional, Union
import logging
import re
import time
from urllib.parse import urljoin, urlparse

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException

# 嘗試導入可選依賴
try:
    import dateparser
    DATEPARSER_AVAILABLE = True
except ImportError:
    DATEPARSER_AVAILABLE = False

try:
    from bs4 import BeautifulSoup
    SOUP_AVAILABLE = True
except ImportError:
    SOUP_AVAILABLE = False


class DetailExtractor:
    """詳情頁面數據提取器，支持多種數據類型和提取策略"""
    
    def __init__(self, driver: webdriver.Chrome, logger=None, base_url: Optional[str] = None, timeout: int = 20):
        """
        初始化詳情頁面提取器
        
        Args:
            driver: Selenium WebDriver實例
            logger: 日誌記錄器
            base_url: 基礎URL，用於URL標準化
            timeout: 默認等待超時時間(秒)
        """
        self.driver = driver
        self.logger = logger or logging.getLogger(__name__)
        self.base_url = base_url
        self.default_timeout = timeout
        
        # 統計計數
        self.extracted_fields_count = 0
        self.extraction_errors_count = 0

    def extract_tables(self, tables_xpath: str, table_title_xpath: str) -> Dict:
        """
        提取所有表格數據
        
        Args:
            tables_xpath: 表格元素的XPath
            table_title_xpath: 表格標題的XPath
            
        Returns:
            包含所有表格數據的字典
        """
        tables_data = {}
        try:
            tables = self.driver.find_elements(By.XPATH, tables_xpath)
            self.logger.info(f"找到 {len(tables)} 個表格")

            for table_index, table in enumerate(tables):
                try:
                    title_elements = table.find_elements(By.XPATH, table_title_xpath)
                    table_title = title_elements[0].text.strip() if title_elements else f"table_{table_index}"
                    table_data = self._extract_table_data(table)
                    tables_data[table_title] = table_data
                except Exception as e:
                    self.logger.warning(f"提取表格 {table_index} 失敗: {str(e)}")
                    self.extraction_errors_count += 1

        except Exception as e:
            self.logger.error(f"提取表格數據失敗: {str(e)}")
            self.extraction_errors_count += 1

        return tables_data

    def _extract_table_data(self, table) -> Dict:
        """
        從單個表格中提取數據
        
        Args:
            table: 表格WebElement元素
            
        Returns:
            表格數據字典
        """
        table_data = {}
        try:
            rows = table.find_elements(By.XPATH, ".//tr")
            for row in rows:
                try:
                    cols = row.find_elements(By.XPATH, ".//th | .//td")
                    if len(cols) >= 2:
                        key = cols[0].text.strip()
                        value = cols[1].text.strip()
                        if key:
                            table_data[key] = value
                            self.extracted_fields_count += 1
                except Exception as e:
                    self.logger.warning(f"提取表格行失敗: {str(e)}")
        except Exception as e:
            self.logger.error(f"提取表格內容失敗: {str(e)}")
        
        return table_data

    def extract_fields(self, fields_config: Dict) -> Dict:
        """
        提取指定字段數據
        
        Args:
            fields_config: 字段配置字典
            
        Returns:
            提取的字段數據字典
        """
        fields_data = {}
        for field_name, field_config in fields_config.items():
            try:
                xpath = field_config.get("xpath", "")
                if xpath:
                    elements = self.wait_for_elements(By.XPATH, xpath)
                    if elements:
                        value = self._extract_field_value(elements[0], field_config)
                        if value is not None:
                            fields_data[field_name] = value
                            self.extracted_fields_count += 1
            except Exception as e:
                self.logger.warning(f"提取字段 {field_name} 失敗: {str(e)}")
                self.extraction_errors_count += 1
        
        return fields_data

    def _extract_field_value(self, element: WebElement, field_config: Dict) -> Optional[Any]:
        """
        從元素中提取字段值
        
        Args:
            element: WebElement元素
            field_config: 字段配置
            
        Returns:
            提取的字段值
        """
        extraction_type = field_config.get("type", "text")
        try:
            if extraction_type == "text":
                text = element.text.strip()
                return self._clean_text(text, field_config)
                
            elif extraction_type == "attribute":
                attribute_name = field_config.get("attribute_name", "href")
                value = element.get_attribute(attribute_name)
                return value.strip() if value else None
                
            elif extraction_type == "html":
                return element.get_attribute("innerHTML")
                
            elif extraction_type == "date":
                text = element.text.strip()
                return self._parse_date(text, field_config)
                
            elif extraction_type == "number":
                text = element.text.strip()
                return self._parse_number(text)
                
            elif extraction_type == "url":
                attribute_name = field_config.get("attribute_name", "href")
                url = element.get_attribute(attribute_name)
                if url:
                    return self._normalize_url(url)
                return None
                
            elif extraction_type == "compound":
                return self._extract_compound_field(element, field_config)
                
            else:
                self.logger.warning(f"未知的提取類型: {extraction_type}")
                return None
                
        except Exception as e:
            self.logger.error(f"提取字段值失敗: {str(e)}")
            return None

    def _clean_text(self, text: str, field_config: Dict) -> str:
        """
        清理文本內容
        
        Args:
            text: 原始文本
            field_config: 字段配置
            
        Returns:
            清理後的文本
        """
        if not text:
            return ""
            
        # 移除多餘的空白字符
        if field_config.get("remove_whitespace", True):
            text = re.sub(r'\s+', ' ', text)
            
        # 移除換行符
        if field_config.get("remove_newlines", True):
            text = text.replace('\n', ' ').replace('\r', '')
            
        # 移除頭尾空白
        if field_config.get("trim", True):
            text = text.strip()
            
        # 轉為小寫
        if field_config.get("lowercase", False):
            text = text.lower()
            
        # 轉為大寫
        if field_config.get("uppercase", False):
            text = text.upper()
            
        # 自定義替換
        custom_replacements = field_config.get("custom_replacements", {})
        for old, new in custom_replacements.items():
            text = text.replace(old, new)
            
        # 正則表達式提取
        regex = field_config.get("regex")
        if regex:
            match = re.search(regex, text)
            if match:
                if match.groups():
                    text = match.group(1)  # 取第一個捕獲組
                else:
                    text = match.group(0)  # 取整個匹配
                    
        # 長度限制
        max_length = field_config.get("max_length")
        if max_length and len(text) > max_length:
            text = text[:max_length]
            
        return text

    def _parse_date(self, date_str: str, field_config: Dict) -> Optional[str]:
        """
        解析日期字符串
        
        Args:
            date_str: 日期字符串
            field_config: 字段配置
            
        Returns:
            解析後的日期字符串
        """
        if not date_str:
            return None
            
        try:
            # 使用自定義格式
            date_format = field_config.get("date_format")
            output_format = field_config.get("output_format", "%Y-%m-%d")
            
            # 使用dateparser庫進行解析
            if DATEPARSER_AVAILABLE:
                parsed_date = dateparser.parse(date_str)
                if parsed_date:
                    return parsed_date.strftime(output_format)
                    
            # 使用日期正則表達式提取
            date_regex = field_config.get("date_regex")
            if date_regex:
                match = re.search(date_regex, date_str)
                if match:
                    return match.group(0)
            
            # 返回原始日期字符串
            return date_str
        except Exception as e:
            self.logger.error(f"日期解析失敗: {str(e)}")
            return None

    def _parse_number(self, number_str: str) -> Union[int, float, None]:
        """
        解析數字字符串
        
        Args:
            number_str: 數字字符串
            
        Returns:
            解析後的數字
        """
        if not number_str:
            return None
            
        try:
            # 清理數字字符串
            clean_str = re.sub(r'[^\d.,\-+]', '', number_str)
            
            # 替換逗號為小數點
            clean_str = clean_str.replace(',', '.')
            
            # 處理多個小數點的情況
            if clean_str.count('.') > 1:
                parts = clean_str.split('.')
                clean_str = parts[0] + '.' + ''.join(parts[1:])
            
            # 嘗試轉換
            if '.' in clean_str:
                return float(clean_str)
            else:
                return int(clean_str)
        except Exception as e:
            self.logger.debug(f"數字解析失敗: {str(e)}")
            return None

    def _normalize_url(self, url: str) -> str:
        """
        標準化URL
        
        Args:
            url: 原始URL
            
        Returns:
            標準化後的URL
        """
        if not url:
            return ""
            
        # 處理相對URL
        if self.base_url and not url.startswith(('http://', 'https://')):
            if url.startswith('//'):
                # 協議相對URL
                parsed_base = urlparse(self.base_url)
                url = f"{parsed_base.scheme}:{url}"
            else:
                # 完全相對URL
                url = urljoin(self.base_url, url)
                
        return url

    def _extract_compound_field(self, element: WebElement, field_config: Dict) -> Dict:
        """
        提取複合字段（嵌套字段）
        
        Args:
            element: WebElement元素
            field_config: 字段配置
            
        Returns:
            複合字段數據
        """
        result = {}
        nested_fields = field_config.get("fields", {})
        
        for field_name, nested_config in nested_fields.items():
            try:
                xpath = nested_config.get("xpath", "")
                relative_xpath = f".{xpath}" if xpath.startswith('/') else xpath
                
                elements = element.find_elements(By.XPATH, relative_xpath)
                if elements:
                    if nested_config.get("multiple", False):
                        values = []
                        for el in elements:
                            value = self._extract_field_value(el, nested_config)
                            if value is not None:
                                values.append(value)
                        result[field_name] = values
                    else:
                        value = self._extract_field_value(elements[0], nested_config)
                        if value is not None:
                            result[field_name] = value
            except Exception as e:
                self.logger.warning(f"提取嵌套字段 {field_name} 失敗: {str(e)}")
                
        return result

    def wait_for_elements(self, by: By, selector: str, timeout: Optional[int] = None) -> List[WebElement]:
        """
        等待多個元素出現
        
        Args:
            by: 定位方式
            selector: 選擇器
            timeout: 超時時間(秒)
            
        Returns:
            找到的元素列表
        """
        if not self.driver:
            self.logger.error("WebDriver未初始化")
            return []
            
        timeout = timeout or self.default_timeout
            
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, selector))
            )
            return self.driver.find_elements(by, selector)
        except TimeoutException:
            self.logger.warning(f"等待元素超時: {selector}")
            return []
        except Exception as e:
            self.logger.error(f"等待元素出錯: {str(e)}")
            return []

    def wait_for_container(self, container_xpath: str, timeout: int = 20) -> Optional[WebElement]:
        """
        等待容器元素加載
        
        Args:
            container_xpath: 容器元素XPath
            timeout: 超時時間(秒)
            
        Returns:
            容器元素，如果未找到則返回None
        """
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((By.XPATH, container_xpath))
            )
            return element
        except TimeoutException:
            self.logger.error(f"等待容器元素超時: {container_xpath}")
            return None
        except Exception as e:
            self.logger.error(f"等待容器元素出錯: {str(e)}")
            return None

    def extract_detail_page(self, detail_config: Dict, container_xpath: Optional[str] = None) -> Dict[str, Any]:
        """
        提取詳情頁面數據
        
        Args:
            detail_config: 詳情頁配置
            container_xpath: 容器元素XPath，如果未提供則使用配置中的值
            
        Returns:
            詳情頁數據
        """
        try:
            # 等待主容器
            container_xpath = container_xpath or detail_config.get("container_xpath", "//body")
            container = self.wait_for_container(container_xpath)
            
            if not container:
                self.logger.error(f"找不到容器元素: {container_xpath}")
                return {}
                
            # 提取字段
            fields_config = detail_config.get("fields", {})
            result = self.extract_fields(fields_config)
            
            # 提取表格（如果配置了）
            tables_config = detail_config.get("tables", {})
            if tables_config:
                tables_xpath = tables_config.get("tables_xpath")
                title_xpath = tables_config.get("title_xpath", ".//caption | .//th[1]")
                if tables_xpath:
                    tables_data = self.extract_tables(tables_xpath, title_xpath)
                    result["tables"] = tables_data
            
            # 添加元數據
            result["_metadata"] = {
                "url": self.driver.current_url,
                "title": self.driver.title,
                "extraction_time": int(time.time())
            }
            
            return result
            
        except Exception as e:
            self.logger.error(f"提取詳情頁數據失敗: {str(e)}")
            return {}

    def expand_sections(self, expand_sections: List[Dict]) -> None:
        """
        展開頁面中的可折疊區塊
        
        Args:
            expand_sections: 展開區塊配置
        """
        if not self.driver or not expand_sections:
            return
        
        for section in expand_sections:
            try:
                xpath = section.get("xpath")
                if not xpath:
                    continue
                    
                elements = self.driver.find_elements(By.XPATH, xpath)
                click_attempts = section.get("click_attempts", 1)
                wait_time = section.get("wait_time", 0.5)
                
                if elements:
                    for i in range(min(len(elements), section.get("max_clicks", len(elements)))):
                        try:
                            for attempt in range(click_attempts):
                                try:
                                    elements[i].click()
                                    time.sleep(wait_time)
                                    break
                                except:
                                    if attempt == click_attempts - 1:
                                        raise
                                    time.sleep(0.2)
                        except Exception as click_error:
                            self.logger.debug(f"點擊元素失敗: {str(click_error)}")
            except Exception as e:
                self.logger.warning(f"展開區塊失敗: {str(e)}")

    def get_statistics(self) -> Dict[str, int]:
        """
        獲取提取統計信息
        
        Returns:
            包含提取統計的字典
        """
        return {
            "extracted_fields": self.extracted_fields_count,
            "extraction_errors": self.extraction_errors_count
        }

    def reset_statistics(self) -> None:
        """重置統計計數"""
        self.extracted_fields_count = 0
        self.extraction_errors_count = 0

    def extract_images(self, container_xpath: Optional[str] = None) -> List[Dict[str, str]]:
        """
        提取頁面中的圖片
        
        Args:
            container_xpath: 容器元素XPath，如果未提供則從整個頁面提取
            
        Returns:
            圖片列表，每個圖片包含URL和可能的alt文本
        """
        images = []
        try:
            container = None
            if container_xpath:
                container = self.wait_for_container(container_xpath)
                
            context = container or self.driver
                
            img_elements = context.find_elements(By.XPATH, ".//img")
            for img in img_elements:
                try:
                    src = img.get_attribute("src")
                    if src:
                        image_info = {
                            "url": self._normalize_url(src),
                            "alt": img.get_attribute("alt") or ""
                        }
                        images.append(image_info)
                except StaleElementReferenceException:
                    continue
                except Exception as e:
                    self.logger.debug(f"提取圖片失敗: {str(e)}")
                    
            return images
        except Exception as e:
            self.logger.error(f"提取圖片列表失敗: {str(e)}")
            return []
