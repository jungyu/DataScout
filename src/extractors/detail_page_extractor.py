from typing import Dict, Optional
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

class DetailPageExtractor:
    def __init__(self, driver: webdriver.Chrome, logger):
        self.driver = driver
        self.logger = logger

    def extract_tables(self, tables_xpath: str, table_title_xpath: str) -> Dict:
        """提取所有表格數據"""
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

        except Exception as e:
            self.logger.error(f"提取表格數據失敗: {str(e)}")

        return tables_data

    def _extract_table_data(self, table) -> Dict:
        """從單個表格中提取數據"""
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
                except Exception as e:
                    self.logger.warning(f"提取表格行失敗: {str(e)}")
        except Exception as e:
            self.logger.error(f"提取表格內容失敗: {str(e)}")
        
        return table_data

    def extract_fields(self, fields_config: Dict) -> Dict:
        """提取指定字段數據"""
        fields_data = {}
        for field_name, field_config in fields_config.items():
            try:
                xpath = field_config.get("xpath", "")
                if xpath:
                    elements = self.driver.find_elements(By.XPATH, xpath)
                    if elements:
                        fields_data[field_name] = self._extract_field_value(elements[0], field_config)
            except Exception as e:
                self.logger.warning(f"提取字段 {field_name} 失敗: {str(e)}")
        
        return fields_data

    def _extract_field_value(self, element, field_config: Dict) -> Optional[str]:
        """從元素中提取字段值"""
        extraction_type = field_config.get("type", "text")
        try:
            if extraction_type == "text":
                return element.text.strip()
            elif extraction_type == "attribute":
                attribute_name = field_config.get("attribute_name", "href")
                return element.get_attribute(attribute_name)
            elif extraction_type == "html":
                return element.get_attribute("innerHTML")
        except Exception as e:
            self.logger.error(f"提取字段值失敗: {str(e)}")
        return None

    def wait_for_container(self, container_xpath: str, timeout: int = 20) -> bool:
        """等待容器元素加載"""
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((By.XPATH, container_xpath))
            )
            return True
        except TimeoutException:
            self.logger.error(f"等待容器元素超時: {container_xpath}")
            return False
