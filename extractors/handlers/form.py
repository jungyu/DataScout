#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
表單提取器模組

提供表單數據提取功能，包括：
1. 表單定位
2. 表單字段提取
3. 表單驗證
4. 表單提交
"""

from typing import Dict, List, Optional, Union, Any, Set, Callable
from dataclasses import dataclass
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementNotInteractableException
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.action_chains import ActionChains
import re
import time
import json
from datetime import datetime

from ..core.base import BaseExtractor
from ..core.error import handle_extractor_error, ExtractorError

@dataclass
class FormExtractorConfig:
    """表單提取器配置"""
    # 表單選擇器
    form_selector: str = "form"
    input_selector: str = "input, select, textarea"
    submit_selector: str = "button[type='submit'], input[type='submit']"
    error_selector: str = ".error, .invalid, [aria-invalid='true']"
    success_selector: str = ".success, .valid, [aria-invalid='false']"
    state_selector: str = "[data-state], [aria-busy], [aria-disabled]"
    
    # 等待設置
    timeout: int = 10
    poll_frequency: float = 0.5
    
    # 表單處理設置
    include_hidden: bool = False
    include_disabled: bool = False
    include_readonly: bool = True
    include_required: bool = True
    include_optional: bool = True
    include_multiple: bool = True
    include_file: bool = True
    include_checkbox: bool = True
    include_radio: bool = True
    include_select: bool = True
    include_textarea: bool = True
    include_text: bool = True
    include_password: bool = True
    include_email: bool = True
    include_number: bool = True
    include_tel: bool = True
    include_url: bool = True
    include_date: bool = True
    include_time: bool = True
    include_datetime: bool = True
    include_color: bool = True
    include_range: bool = True
    include_search: bool = True
    
    # 表單填充設置
    clear_before_fill: bool = True
    click_before_fill: bool = True
    wait_after_fill: float = 0.5
    wait_after_submit: float = 1.0
    scroll_to_element: bool = True
    
    # 表單驗證設置
    validate_before_submit: bool = True
    validate_after_submit: bool = True
    max_validation_attempts: int = 3
    validation_timeout: float = 5.0
    validation_poll_frequency: float = 0.5
    
    # 錯誤處理設置
    retry_on_error: bool = True
    max_retries: int = 3
    retry_delay: float = 1.0
    ignore_errors: List[str] = None
    
    # 狀態管理設置
    track_state_changes: bool = True
    state_change_timeout: float = 5.0
    state_change_poll_frequency: float = 0.5
    save_state_history: bool = True
    state_history_limit: int = 10
    
    # 事件處理設置
    handle_field_change: bool = True
    handle_field_focus: bool = True
    handle_field_blur: bool = True
    handle_form_submit: bool = True
    handle_form_reset: bool = True
    
    def __post_init__(self):
        if self.ignore_errors is None:
            self.ignore_errors = []

class FormExtractor(BaseExtractor):
    """表單提取器類別"""
    
    def __init__(self, driver, config: Optional[Dict] = None):
        """初始化表單提取器
        
        Args:
            driver: WebDriver 實例
            config: 配置字典
        """
        super().__init__(driver)
        self.config = FormExtractorConfig(**(config or {}))
        
    @handle_extractor_error()
    def find_form_elements(self, selector: Optional[str] = None) -> List[Any]:
        """查找表單元素
        
        Args:
            selector: 表單選擇器，如果為 None 則使用配置中的選擇器
            
        Returns:
            List[Any]: 表單元素列表
        """
        selector = selector or self.config.form_selector
        try:
            WebDriverWait(self.driver, self.config.timeout).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, selector))
            )
            return self.driver.find_elements(By.CSS_SELECTOR, selector)
        except TimeoutException:
            return []
            
    @handle_extractor_error()
    def get_field_info(self, element: Any) -> Dict[str, Any]:
        """獲取字段信息
        
        Args:
            element: 字段元素
            
        Returns:
            Dict[str, Any]: 字段信息字典
        """
        field_type = element.get_attribute("type") or element.tag_name
        field_name = element.get_attribute("name")
        field_id = element.get_attribute("id")
        field_value = element.get_attribute("value")
        field_placeholder = element.get_attribute("placeholder")
        field_required = element.get_attribute("required") is not None
        field_disabled = element.get_attribute("disabled") is not None
        field_readonly = element.get_attribute("readonly") is not None
        field_multiple = element.get_attribute("multiple") is not None
        field_maxlength = element.get_attribute("maxlength")
        field_minlength = element.get_attribute("minlength")
        field_pattern = element.get_attribute("pattern")
        field_accept = element.get_attribute("accept")
        field_autocomplete = element.get_attribute("autocomplete")
        field_autofocus = element.get_attribute("autofocus") is not None
        field_form = element.get_attribute("form")
        field_formaction = element.get_attribute("formaction")
        field_formenctype = element.get_attribute("formenctype")
        field_formmethod = element.get_attribute("formmethod")
        field_formtarget = element.get_attribute("formtarget")
        field_formnovalidate = element.get_attribute("formnovalidate") is not None
        
        # 處理選擇框
        if field_type == "select":
            select = Select(element)
            options = []
            for option in select.options:
                options.append({
                    "value": option.get_attribute("value"),
                    "text": option.text,
                    "selected": option.is_selected(),
                    "disabled": option.get_attribute("disabled") is not None
                })
            field_value = options
            
        # 處理複選框和單選框
        elif field_type in ["checkbox", "radio"]:
            field_value = element.is_selected()
            
        # 處理文本區域
        elif field_type == "textarea":
            field_value = element.text
            
        return {
            "type": field_type,
            "name": field_name,
            "id": field_id,
            "value": field_value,
            "placeholder": field_placeholder,
            "required": field_required,
            "disabled": field_disabled,
            "readonly": field_readonly,
            "multiple": field_multiple,
            "maxlength": field_maxlength,
            "minlength": field_minlength,
            "pattern": field_pattern,
            "accept": field_accept,
            "autocomplete": field_autocomplete,
            "autofocus": field_autofocus,
            "form": field_form,
            "formaction": field_formaction,
            "formenctype": field_formenctype,
            "formmethod": field_formmethod,
            "formtarget": field_formtarget,
            "formnovalidate": field_formnovalidate
        }
        
    @handle_extractor_error()
    def validate_field(self, field_info: Dict[str, Any]) -> bool:
        """驗證字段
        
        Args:
            field_info: 字段信息
            
        Returns:
            bool: 是否通過驗證
        """
        field_type = field_info["type"]
        
        # 檢查字段類型
        if field_type == "hidden" and not self.config.include_hidden:
            return False
        if field_type == "file" and not self.config.include_file:
            return False
        if field_type == "checkbox" and not self.config.include_checkbox:
            return False
        if field_type == "radio" and not self.config.include_radio:
            return False
        if field_type == "select" and not self.config.include_select:
            return False
        if field_type == "textarea" and not self.config.include_textarea:
            return False
        if field_type == "text" and not self.config.include_text:
            return False
        if field_type == "password" and not self.config.include_password:
            return False
        if field_type == "email" and not self.config.include_email:
            return False
        if field_type == "number" and not self.config.include_number:
            return False
        if field_type == "tel" and not self.config.include_tel:
            return False
        if field_type == "url" and not self.config.include_url:
            return False
        if field_type == "date" and not self.config.include_date:
            return False
        if field_type == "time" and not self.config.include_time:
            return False
        if field_type == "datetime-local" and not self.config.include_datetime:
            return False
        if field_type == "color" and not self.config.include_color:
            return False
        if field_type == "range" and not self.config.include_range:
            return False
        if field_type == "search" and not self.config.include_search:
            return False
            
        # 檢查字段狀態
        if field_info["disabled"] and not self.config.include_disabled:
            return False
        if field_info["readonly"] and not self.config.include_readonly:
            return False
        if field_info["required"] and not self.config.include_required:
            return False
        if not field_info["required"] and not self.config.include_optional:
            return False
        if field_info["multiple"] and not self.config.include_multiple:
            return False
            
        return True
        
    @handle_extractor_error()
    def extract_fields(
        self,
        form_element: Any,
        selector: Optional[str] = None,
        validate: bool = True
    ) -> Dict[str, Dict[str, Any]]:
        """提取表單字段
        
        Args:
            form_element: 表單元素
            selector: 字段選擇器
            validate: 是否驗證字段
            
        Returns:
            Dict[str, Dict[str, Any]]: 字段信息字典
        """
        selector = selector or self.config.input_selector
        elements = form_element.find_elements(By.CSS_SELECTOR, selector)
        fields = {}
        
        for element in elements:
            field_info = self.get_field_info(element)
            if field_info["name"]:
                if not validate or self.validate_field(field_info):
                    fields[field_info["name"]] = field_info
                    
        return fields
        
    @handle_extractor_error()
    def find_submit_button(self, form_element: Any) -> Optional[Any]:
        """查找提交按鈕
        
        Args:
            form_element: 表單元素
            
        Returns:
            Optional[Any]: 提交按鈕元素
        """
        try:
            return form_element.find_element(By.CSS_SELECTOR, self.config.submit_selector)
        except NoSuchElementException:
            return None
            
    @handle_extractor_error()
    def extract_form(
        self,
        selector: Optional[str] = None,
        validate: bool = True
    ) -> List[Dict[str, Any]]:
        """提取表單
        
        Args:
            selector: 表單選擇器
            validate: 是否驗證字段
            
        Returns:
            List[Dict[str, Any]]: 表單信息列表
        """
        forms = self.find_form_elements(selector)
        form_info_list = []
        
        for form in forms:
            form_info = {
                "id": form.get_attribute("id"),
                "name": form.get_attribute("name"),
                "action": form.get_attribute("action"),
                "method": form.get_attribute("method"),
                "enctype": form.get_attribute("enctype"),
                "target": form.get_attribute("target"),
                "novalidate": form.get_attribute("novalidate") is not None,
                "fields": self.extract_fields(form, None, validate),
                "submit_button": self.find_submit_button(form) is not None
            }
            form_info_list.append(form_info)
            
        return form_info_list
        
    @handle_extractor_error()
    def extract(
        self,
        selector: Optional[str] = None,
        validate: bool = True
    ) -> List[Dict[str, Any]]:
        """提取表單
        
        Args:
            selector: 表單選擇器
            validate: 是否驗證字段
            
        Returns:
            List[Dict[str, Any]]: 表單信息列表
        """
        return self.extract_form(selector, validate)
        
    @handle_extractor_error()
    def find_field_element(
        self,
        form_element: Any,
        field_name: str,
        field_type: Optional[str] = None
    ) -> Optional[Any]:
        """查找字段元素
        
        Args:
            form_element: 表單元素
            field_name: 字段名稱
            field_type: 字段類型
            
        Returns:
            Optional[Any]: 字段元素
        """
        try:
            if field_type:
                selector = f"{field_type}[name='{field_name}']"
            else:
                selector = f"[name='{field_name}']"
            return form_element.find_element(By.CSS_SELECTOR, selector)
        except NoSuchElementException:
            return None
            
    @handle_extractor_error()
    def scroll_to_element(self, element: Any) -> None:
        """滾動到元素
        
        Args:
            element: 目標元素
        """
        if self.config.scroll_to_element:
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
            
    @handle_extractor_error()
    def fill_text_field(self, element: Any, value: str) -> None:
        """填充文本字段
        
        Args:
            element: 字段元素
            value: 填充值
        """
        if self.config.click_before_fill:
            element.click()
            
        if self.config.clear_before_fill:
            element.clear()
            
        element.send_keys(value)
        
    @handle_extractor_error()
    def fill_checkbox_field(self, element: Any, value: bool) -> None:
        """填充複選框字段
        
        Args:
            element: 字段元素
            value: 填充值
        """
        if element.is_selected() != value:
            element.click()
            
    @handle_extractor_error()
    def fill_radio_field(self, element: Any, value: bool) -> None:
        """填充單選框字段
        
        Args:
            element: 字段元素
            value: 填充值
        """
        if element.is_selected() != value:
            element.click()
            
    @handle_extractor_error()
    def fill_select_field(self, element: Any, value: Union[str, List[str]]) -> None:
        """填充選擇框字段
        
        Args:
            element: 字段元素
            value: 填充值
        """
        select = Select(element)
        
        if isinstance(value, list):
            # 清除所有選項
            for option in select.all_selected_options:
                option.click()
                
            # 選擇新選項
            for v in value:
                select.select_by_value(str(v))
        else:
            select.select_by_value(str(value))
            
    @handle_extractor_error()
    def fill_textarea_field(self, element: Any, value: str) -> None:
        """填充文本區域字段
        
        Args:
            element: 字段元素
            value: 填充值
        """
        if self.config.click_before_fill:
            element.click()
            
        if self.config.clear_before_fill:
            element.clear()
            
        element.send_keys(value)
        
    @handle_extractor_error()
    def fill_file_field(self, element: Any, file_path: str) -> None:
        """填充文件字段
        
        Args:
            element: 字段元素
            file_path: 文件路徑
        """
        element.send_keys(file_path)
        
    @handle_extractor_error()
    def fill_field(
        self,
        form_element: Any,
        field_name: str,
        value: Any,
        field_type: Optional[str] = None
    ) -> bool:
        """填充字段
        
        Args:
            form_element: 表單元素
            field_name: 字段名稱
            value: 填充值
            field_type: 字段類型
            
        Returns:
            bool: 是否填充成功
        """
        element = self.find_field_element(form_element, field_name, field_type)
        if not element:
            return False
            
        self.scroll_to_element(element)
        
        field_type = field_type or element.get_attribute("type") or element.tag_name
        
        if field_type == "checkbox":
            self.fill_checkbox_field(element, value)
        elif field_type == "radio":
            self.fill_radio_field(element, value)
        elif field_type == "select":
            self.fill_select_field(element, value)
        elif field_type == "textarea":
            self.fill_textarea_field(element, value)
        elif field_type == "file":
            self.fill_file_field(element, value)
        else:
            self.fill_text_field(element, str(value))
            
        if self.config.wait_after_fill > 0:
            import time
            time.sleep(self.config.wait_after_fill)
            
        return True
        
    @handle_extractor_error()
    def fill_form(
        self,
        form_element: Any,
        form_data: Dict[str, Any],
        field_types: Optional[Dict[str, str]] = None
    ) -> Dict[str, bool]:
        """填充表單
        
        Args:
            form_element: 表單元素
            form_data: 表單數據
            field_types: 字段類型映射
            
        Returns:
            Dict[str, bool]: 字段填充結果
        """
        results = {}
        
        for field_name, value in form_data.items():
            field_type = field_types.get(field_name) if field_types else None
            results[field_name] = self.fill_field(form_element, field_name, value, field_type)
            
        return results
        
    @handle_extractor_error()
    def submit_form(self, form_element: Any) -> bool:
        """提交表單
        
        Args:
            form_element: 表單元素
            
        Returns:
            bool: 是否提交成功
        """
        submit_button = self.find_submit_button(form_element)
        if not submit_button:
            return False
            
        self.scroll_to_element(submit_button)
        submit_button.click()
        
        if self.config.wait_after_submit > 0:
            import time
            time.sleep(self.config.wait_after_submit)
            
        return True
        
    @handle_extractor_error()
    def validate_field_value(self, field_info: Dict[str, Any], value: Any) -> Dict[str, Any]:
        """驗證字段值
        
        Args:
            field_info: 字段信息
            value: 字段值
            
        Returns:
            Dict[str, Any]: 驗證結果
        """
        field_type = field_info["type"]
        field_name = field_info["name"]
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": []
        }
        
        # 檢查必填字段
        if field_info["required"] and (value is None or value == ""):
            validation_result["valid"] = False
            validation_result["errors"].append(f"字段 '{field_name}' 為必填")
            return validation_result
            
        # 檢查字段長度
        if isinstance(value, str):
            if field_info["minlength"] and len(value) < int(field_info["minlength"]):
                validation_result["valid"] = False
                validation_result["errors"].append(
                    f"字段 '{field_name}' 長度不能小於 {field_info['minlength']}"
                )
            if field_info["maxlength"] and len(value) > int(field_info["maxlength"]):
                validation_result["valid"] = False
                validation_result["errors"].append(
                    f"字段 '{field_name}' 長度不能大於 {field_info['maxlength']}"
                )
                
        # 檢查字段格式
        if field_info["pattern"] and isinstance(value, str):
            if not re.match(field_info["pattern"], value):
                validation_result["valid"] = False
                validation_result["errors"].append(f"字段 '{field_name}' 格式不正確")
                
        # 檢查字段類型
        if field_type == "email" and isinstance(value, str):
            email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
            if not re.match(email_pattern, value):
                validation_result["valid"] = False
                validation_result["errors"].append(f"字段 '{field_name}' 不是有效的電子郵件地址")
                
        elif field_type == "number" and isinstance(value, (int, float, str)):
            try:
                float(str(value))
            except ValueError:
                validation_result["valid"] = False
                validation_result["errors"].append(f"字段 '{field_name}' 不是有效的數字")
                
        elif field_type == "url" and isinstance(value, str):
            url_pattern = r"^https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)$"
            if not re.match(url_pattern, value):
                validation_result["valid"] = False
                validation_result["errors"].append(f"字段 '{field_name}' 不是有效的 URL")
                
        elif field_type == "tel" and isinstance(value, str):
            tel_pattern = r"^\+?[1-9]\d{1,14}$"
            if not re.match(tel_pattern, value):
                validation_result["valid"] = False
                validation_result["errors"].append(f"字段 '{field_name}' 不是有效的電話號碼")
                
        elif field_type == "date" and isinstance(value, str):
            date_pattern = r"^\d{4}-\d{2}-\d{2}$"
            if not re.match(date_pattern, value):
                validation_result["valid"] = False
                validation_result["errors"].append(f"字段 '{field_name}' 不是有效的日期格式 (YYYY-MM-DD)")
                
        elif field_type == "time" and isinstance(value, str):
            time_pattern = r"^([01]\d|2[0-3]):([0-5]\d)$"
            if not re.match(time_pattern, value):
                validation_result["valid"] = False
                validation_result["errors"].append(f"字段 '{field_name}' 不是有效的時間格式 (HH:MM)")
                
        elif field_type == "datetime-local" and isinstance(value, str):
            datetime_pattern = r"^\d{4}-\d{2}-\d{2}T([01]\d|2[0-3]):([0-5]\d)$"
            if not re.match(datetime_pattern, value):
                validation_result["valid"] = False
                validation_result["errors"].append(f"字段 '{field_name}' 不是有效的日期時間格式 (YYYY-MM-DDTHH:MM)")
                
        elif field_type == "color" and isinstance(value, str):
            color_pattern = r"^#[0-9a-fA-F]{6}$"
            if not re.match(color_pattern, value):
                validation_result["valid"] = False
                validation_result["errors"].append(f"字段 '{field_name}' 不是有效的顏色格式 (#RRGGBB)")
                
        elif field_type == "range" and isinstance(value, (int, float, str)):
            try:
                value_float = float(str(value))
                min_value = float(field_info.get("min", float("-inf")))
                max_value = float(field_info.get("max", float("inf")))
                if value_float < min_value or value_float > max_value:
                    validation_result["valid"] = False
                    validation_result["errors"].append(
                        f"字段 '{field_name}' 的值必須在 {min_value} 和 {max_value} 之間"
                    )
            except ValueError:
                validation_result["valid"] = False
                validation_result["errors"].append(f"字段 '{field_name}' 不是有效的數字")
                
        return validation_result
        
    @handle_extractor_error()
    def validate_form_data(
        self,
        form_element: Any,
        form_data: Dict[str, Any],
        field_types: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """驗證表單數據
        
        Args:
            form_element: 表單元素
            form_data: 表單數據
            field_types: 字段類型映射
            
        Returns:
            Dict[str, Any]: 驗證結果
        """
        validation_results = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "field_results": {}
        }
        
        for field_name, value in form_data.items():
            field_type = field_types.get(field_name) if field_types else None
            element = self.find_field_element(form_element, field_name, field_type)
            
            if element:
                field_info = self.get_field_info(element)
                field_result = self.validate_field_value(field_info, value)
                validation_results["field_results"][field_name] = field_result
                
                if not field_result["valid"]:
                    validation_results["valid"] = False
                    validation_results["errors"].extend(field_result["errors"])
                validation_results["warnings"].extend(field_result["warnings"])
                
        return validation_results
        
    @handle_extractor_error()
    def check_form_errors(self, form_element: Any) -> List[str]:
        """檢查表單錯誤
        
        Args:
            form_element: 表單元素
            
        Returns:
            List[str]: 錯誤信息列表
        """
        errors = []
        try:
            error_elements = form_element.find_elements(By.CSS_SELECTOR, self.config.error_selector)
            for element in error_elements:
                error_text = element.text.strip()
                if error_text:
                    errors.append(error_text)
        except Exception as e:
            self.logger.warning(f"檢查表單錯誤時發生異常: {str(e)}")
            
        return errors
        
    @handle_extractor_error()
    def check_form_success(self, form_element: Any) -> bool:
        """檢查表單是否提交成功
        
        Args:
            form_element: 表單元素
            
        Returns:
            bool: 是否提交成功
        """
        try:
            success_elements = form_element.find_elements(By.CSS_SELECTOR, self.config.success_selector)
            return len(success_elements) > 0
        except Exception as e:
            self.logger.warning(f"檢查表單成功狀態時發生異常: {str(e)}")
            return False
            
    @handle_extractor_error()
    def wait_for_validation(self, form_element: Any) -> Dict[str, Any]:
        """等待表單驗證完成
        
        Args:
            form_element: 表單元素
            
        Returns:
            Dict[str, Any]: 驗證結果
        """
        start_time = time.time()
        while time.time() - start_time < self.config.validation_timeout:
            errors = self.check_form_errors(form_element)
            if errors:
                return {
                    "valid": False,
                    "errors": errors,
                    "success": False
                }
                
            if self.check_form_success(form_element):
                return {
                    "valid": True,
                    "errors": [],
                    "success": True
                }
                
            time.sleep(self.config.validation_poll_frequency)
            
        return {
            "valid": True,
            "errors": [],
            "success": False,
            "timeout": True
        }
        
    @handle_extractor_error()
    def handle_form_error(self, error: Exception, attempt: int) -> bool:
        """處理表單錯誤
        
        Args:
            error: 錯誤異常
            attempt: 當前嘗試次數
            
        Returns:
            bool: 是否應該重試
        """
        error_message = str(error)
        
        # 檢查是否應該忽略此錯誤
        for ignore_pattern in self.config.ignore_errors:
            if re.search(ignore_pattern, error_message):
                self.logger.info(f"忽略錯誤: {error_message}")
                return False
                
        # 檢查是否應該重試
        if self.config.retry_on_error and attempt < self.config.max_retries:
            self.logger.warning(f"表單操作失敗 (嘗試 {attempt}/{self.config.max_retries}): {error_message}")
            time.sleep(self.config.retry_delay)
            return True
            
        self.logger.error(f"表單操作失敗: {error_message}")
        return False
        
    @handle_extractor_error()
    def get_form_state(self, form_element: Any) -> Dict[str, Any]:
        """獲取表單狀態
        
        Args:
            form_element: 表單元素
            
        Returns:
            Dict[str, Any]: 表單狀態信息
        """
        state = {
            "timestamp": datetime.now().isoformat(),
            "form_id": form_element.get_attribute("id"),
            "form_name": form_element.get_attribute("name"),
            "is_disabled": form_element.get_attribute("disabled") is not None,
            "is_readonly": form_element.get_attribute("readonly") is not None,
            "is_valid": not bool(self.check_form_errors(form_element)),
            "is_submitted": self.check_form_success(form_element),
            "fields": {}
        }
        
        # 獲取所有字段狀態
        fields = self.extract_fields(form_element, None, False)
        for field_name, field_info in fields.items():
            state["fields"][field_name] = {
                "type": field_info["type"],
                "value": field_info["value"],
                "is_disabled": field_info["disabled"],
                "is_readonly": field_info["readonly"],
                "is_required": field_info["required"],
                "is_valid": True  # 默認值，實際驗證結果需要單獨檢查
            }
            
        # 檢查字段驗證狀態
        for field_name in state["fields"]:
            element = self.find_field_element(form_element, field_name)
            if element:
                error_elements = element.find_elements(By.CSS_SELECTOR, self.config.error_selector)
                state["fields"][field_name]["is_valid"] = len(error_elements) == 0
                
        return state
        
    @handle_extractor_error()
    def wait_for_state_change(
        self,
        form_element: Any,
        initial_state: Dict[str, Any],
        timeout: Optional[float] = None
    ) -> Dict[str, Any]:
        """等待表單狀態變化
        
        Args:
            form_element: 表單元素
            initial_state: 初始狀態
            timeout: 超時時間
            
        Returns:
            Dict[str, Any]: 最終狀態
        """
        timeout = timeout or self.config.state_change_timeout
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            current_state = self.get_form_state(form_element)
            
            # 檢查狀態是否發生變化
            if current_state != initial_state:
                return current_state
                
            time.sleep(self.config.state_change_poll_frequency)
            
        return self.get_form_state(form_element)
        
    @handle_extractor_error()
    def track_form_state(
        self,
        form_element: Any,
        callback: Optional[Callable[[Dict[str, Any]], None]] = None
    ) -> Dict[str, List[Dict[str, Any]]]:
        """追蹤表單狀態變化
        
        Args:
            form_element: 表單元素
            callback: 狀態變化回調函數
            
        Returns:
            Dict[str, List[Dict[str, Any]]]: 狀態歷史記錄
        """
        if not self.config.track_state_changes:
            return {}
            
        state_history = {
            "initial": [],
            "changes": [],
            "final": None
        }
        
        # 記錄初始狀態
        initial_state = self.get_form_state(form_element)
        state_history["initial"].append(initial_state)
        
        if callback:
            callback(initial_state)
            
        # 監聽字段變化事件
        if self.config.handle_field_change:
            self.driver.execute_script("""
                var form = arguments[0];
                var fields = form.querySelectorAll(arguments[1]);
                
                fields.forEach(function(field) {
                    field.addEventListener('change', function() {
                        window.dispatchEvent(new CustomEvent('formFieldChange', {
                            detail: {
                                fieldName: field.name,
                                fieldType: field.type || field.tagName.toLowerCase(),
                                fieldValue: field.value
                            }
                        }));
                    });
                    
                    if (arguments[2]) {
                        field.addEventListener('focus', function() {
                            window.dispatchEvent(new CustomEvent('formFieldFocus', {
                                detail: {
                                    fieldName: field.name,
                                    fieldType: field.type || field.tagName.toLowerCase()
                                }
                            }));
                        });
                    }
                    
                    if (arguments[3]) {
                        field.addEventListener('blur', function() {
                            window.dispatchEvent(new CustomEvent('formFieldBlur', {
                                detail: {
                                    fieldName: field.name,
                                    fieldType: field.type || field.tagName.toLowerCase()
                                }
                            }));
                        });
                    }
                });
                
                if (arguments[4]) {
                    form.addEventListener('submit', function() {
                        window.dispatchEvent(new CustomEvent('formSubmit', {
                            detail: {
                                formId: form.id,
                                formName: form.name
                            }
                        }));
                    });
                }
                
                if (arguments[5]) {
                    form.addEventListener('reset', function() {
                        window.dispatchEvent(new CustomEvent('formReset', {
                            detail: {
                                formId: form.id,
                                formName: form.name
                            }
                        }));
                    });
                }
            """, form_element, self.config.input_selector, 
                self.config.handle_field_focus,
                self.config.handle_field_blur,
                self.config.handle_form_submit,
                self.config.handle_form_reset)
                
        # 監聽狀態變化事件
        self.driver.execute_script("""
            window.addEventListener('formFieldChange', function(event) {
                window.dispatchEvent(new CustomEvent('formStateChange', {
                    detail: {
                        type: 'fieldChange',
                        field: event.detail
                    }
                }));
            });
            
            window.addEventListener('formFieldFocus', function(event) {
                window.dispatchEvent(new CustomEvent('formStateChange', {
                    detail: {
                        type: 'fieldFocus',
                        field: event.detail
                    }
                }));
            });
            
            window.addEventListener('formFieldBlur', function(event) {
                window.dispatchEvent(new CustomEvent('formStateChange', {
                    detail: {
                        type: 'fieldBlur',
                        field: event.detail
                    }
                }));
            });
            
            window.addEventListener('formSubmit', function(event) {
                window.dispatchEvent(new CustomEvent('formStateChange', {
                    detail: {
                        type: 'formSubmit',
                        form: event.detail
                    }
                }));
            });
            
            window.addEventListener('formReset', function(event) {
                window.dispatchEvent(new CustomEvent('formStateChange', {
                    detail: {
                        type: 'formReset',
                        form: event.detail
                    }
                }));
            });
        """)
        
        # 等待狀態變化
        def handle_state_change(event):
            new_state = self.get_form_state(form_element)
            state_history["changes"].append(new_state)
            
            if callback:
                callback(new_state)
                
            # 限制歷史記錄大小
            if len(state_history["changes"]) > self.config.state_history_limit:
                state_history["changes"] = state_history["changes"][-self.config.state_history_limit:]
                
        self.driver.execute_script("""
            window.addEventListener('formStateChange', function(event) {
                window.dispatchEvent(new CustomEvent('formStateUpdated', {
                    detail: event.detail
                }));
            });
        """)
        
        # 記錄最終狀態
        state_history["final"] = self.get_form_state(form_element)
        
        return state_history
        
    @handle_extractor_error()
    def save_form_state(self, state: Dict[str, Any], file_path: Optional[str] = None) -> str:
        """保存表單狀態
        
        Args:
            state: 表單狀態
            file_path: 文件路徑
            
        Returns:
            str: 保存的文件路徑
        """
        if not file_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            form_id = state.get("form_id", "unknown")
            file_path = f"form_state_{form_id}_{timestamp}.json"
            
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
            
        return file_path
        
    @handle_extractor_error()
    def load_form_state(self, file_path: str) -> Dict[str, Any]:
        """加載表單狀態
        
        Args:
            file_path: 文件路徑
            
        Returns:
            Dict[str, Any]: 表單狀態
        """
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
            
    @handle_extractor_error()
    def restore_form_state(
        self,
        form_element: Any,
        state: Dict[str, Any],
        restore_values: bool = True,
        restore_disabled: bool = False,
        restore_readonly: bool = False
    ) -> Dict[str, bool]:
        """恢復表單狀態
        
        Args:
            form_element: 表單元素
            state: 表單狀態
            restore_values: 是否恢復字段值
            restore_disabled: 是否恢復禁用狀態
            restore_readonly: 是否恢復只讀狀態
            
        Returns:
            Dict[str, bool]: 恢復結果
        """
        results = {}
        
        # 恢復字段狀態
        for field_name, field_state in state.get("fields", {}).items():
            element = self.find_field_element(form_element, field_name)
            if not element:
                results[field_name] = False
                continue
                
            try:
                # 恢復字段值
                if restore_values and "value" in field_state:
                    self.fill_field(form_element, field_name, field_state["value"])
                    
                # 恢復禁用狀態
                if restore_disabled and "is_disabled" in field_state:
                    if field_state["is_disabled"]:
                        self.driver.execute_script("arguments[0].setAttribute('disabled', '');", element)
                    else:
                        self.driver.execute_script("arguments[0].removeAttribute('disabled');", element)
                        
                # 恢復只讀狀態
                if restore_readonly and "is_readonly" in field_state:
                    if field_state["is_readonly"]:
                        self.driver.execute_script("arguments[0].setAttribute('readonly', '');", element)
                    else:
                        self.driver.execute_script("arguments[0].removeAttribute('readonly');", element)
                        
                results[field_name] = True
            except Exception as e:
                self.logger.error(f"恢復字段 '{field_name}' 狀態時發生錯誤: {str(e)}")
                results[field_name] = False
                
        return results
        
    @handle_extractor_error()
    def fill_and_submit_with_state_tracking(
        self,
        selector: Optional[str] = None,
        form_data: Optional[Dict[str, Any]] = None,
        field_types: Optional[Dict[str, str]] = None,
        auto_submit: bool = True,
        state_callback: Optional[Callable[[Dict[str, Any]], None]] = None
    ) -> Dict[str, Any]:
        """填充並提交表單（帶狀態追蹤）
        
        Args:
            selector: 表單選擇器
            form_data: 表單數據
            field_types: 字段類型映射
            auto_submit: 是否自動提交
            state_callback: 狀態變化回調函數
            
        Returns:
            Dict[str, Any]: 操作結果
        """
        forms = self.find_form_elements(selector)
        if not forms:
            return {"success": False, "error": "表單未找到"}
            
        form_element = forms[0]
        form_data = form_data or {}
        field_types = field_types or {}
        
        # 開始追蹤表單狀態
        state_history = self.track_form_state(form_element, state_callback)
        
        # 驗證表單數據
        if self.config.validate_before_submit:
            validation_result = self.validate_form_data(form_element, form_data, field_types)
            if not validation_result["valid"]:
                return {
                    "success": False,
                    "error": "表單驗證失敗",
                    "validation_result": validation_result,
                    "state_history": state_history
                }
                
        # 填充表單
        attempt = 1
        while True:
            try:
                fill_results = self.fill_form(form_element, form_data, field_types)
                break
            except Exception as e:
                if not self.handle_form_error(e, attempt):
                    return {
                        "success": False,
                        "error": str(e),
                        "state_history": state_history
                    }
                attempt += 1
                
        # 提交表單
        if auto_submit:
            attempt = 1
            while True:
                try:
                    submit_success = self.submit_form(form_element)
                    if not submit_success:
                        return {
                            "success": False,
                            "error": "提交按鈕未找到",
                            "state_history": state_history
                        }
                        
                    # 等待驗證結果
                    if self.config.validate_after_submit:
                        validation_result = self.wait_for_validation(form_element)
                        return {
                            "success": validation_result["valid"] and validation_result["success"],
                            "validation_result": validation_result,
                            "fill_results": fill_results,
                            "state_history": state_history
                        }
                        
                    return {
                        "success": True,
                        "fill_results": fill_results,
                        "submit_success": True,
                        "state_history": state_history
                    }
                except Exception as e:
                    if not self.handle_form_error(e, attempt):
                        return {
                            "success": False,
                            "error": str(e),
                            "state_history": state_history
                        }
                    attempt += 1
                    
        return {
            "success": True,
            "fill_results": fill_results,
            "submit_success": None,
            "state_history": state_history
        }
        
    @handle_extractor_error()
    def fill_and_submit_with_validation(
        self,
        selector: Optional[str] = None,
        form_data: Optional[Dict[str, Any]] = None,
        field_types: Optional[Dict[str, str]] = None,
        auto_submit: bool = True
    ) -> Dict[str, Any]:
        """填充並提交表單（帶驗證）
        
        Args:
            selector: 表單選擇器
            form_data: 表單數據
            field_types: 字段類型映射
            auto_submit: 是否自動提交
            
        Returns:
            Dict[str, Any]: 操作結果
        """
        forms = self.find_form_elements(selector)
        if not forms:
            return {"success": False, "error": "表單未找到"}
            
        form_element = forms[0]
        form_data = form_data or {}
        field_types = field_types or {}
        
        # 驗證表單數據
        if self.config.validate_before_submit:
            validation_result = self.validate_form_data(form_element, form_data, field_types)
            if not validation_result["valid"]:
                return {
                    "success": False,
                    "error": "表單驗證失敗",
                    "validation_result": validation_result
                }
                
        # 填充表單
        attempt = 1
        while True:
            try:
                fill_results = self.fill_form(form_element, form_data, field_types)
                break
            except Exception as e:
                if not self.handle_form_error(e, attempt):
                    return {"success": False, "error": str(e)}
                attempt += 1
                
        # 提交表單
        if auto_submit:
            attempt = 1
            while True:
                try:
                    submit_success = self.submit_form(form_element)
                    if not submit_success:
                        return {"success": False, "error": "提交按鈕未找到"}
                        
                    # 等待驗證結果
                    if self.config.validate_after_submit:
                        validation_result = self.wait_for_validation(form_element)
                        return {
                            "success": validation_result["valid"] and validation_result["success"],
                            "validation_result": validation_result,
                            "fill_results": fill_results
                        }
                        
                    return {
                        "success": True,
                        "fill_results": fill_results,
                        "submit_success": True
                    }
                except Exception as e:
                    if not self.handle_form_error(e, attempt):
                        return {"success": False, "error": str(e)}
                    attempt += 1
                    
        return {
            "success": True,
            "fill_results": fill_results,
            "submit_success": None
        }
        
    @handle_extractor_error()
    def setup_form_event_listeners(self, form_element: Any) -> None:
        """設置表單事件監聽器
        
        Args:
            form_element: 表單元素
        """
        # 設置字段變化事件監聽器
        if self.config.handle_field_change:
            self.driver.execute_script("""
                var form = arguments[0];
                var fields = form.querySelectorAll(arguments[1]);
                
                fields.forEach(function(field) {
                    field.addEventListener('change', function() {
                        window.dispatchEvent(new CustomEvent('formFieldChange', {
                            detail: {
                                fieldName: field.name,
                                fieldType: field.type || field.tagName.toLowerCase(),
                                fieldValue: field.value
                            }
                        }));
                    });
                    
                    if (arguments[2]) {
                        field.addEventListener('focus', function() {
                            window.dispatchEvent(new CustomEvent('formFieldFocus', {
                                detail: {
                                    fieldName: field.name,
                                    fieldType: field.type || field.tagName.toLowerCase()
                                }
                            }));
                        });
                    }
                    
                    if (arguments[3]) {
                        field.addEventListener('blur', function() {
                            window.dispatchEvent(new CustomEvent('formFieldBlur', {
                                detail: {
                                    fieldName: field.name,
                                    fieldType: field.type || field.tagName.toLowerCase()
                                }
                            }));
                        });
                    }
                });
                
                if (arguments[4]) {
                    form.addEventListener('submit', function() {
                        window.dispatchEvent(new CustomEvent('formSubmit', {
                            detail: {
                                formId: form.id,
                                formName: form.name
                            }
                        }));
                    });
                }
                
                if (arguments[5]) {
                    form.addEventListener('reset', function() {
                        window.dispatchEvent(new CustomEvent('formReset', {
                            detail: {
                                formId: form.id,
                                formName: form.name
                            }
                        }));
                    });
                }
            """, form_element, self.config.input_selector, 
                self.config.handle_field_focus,
                self.config.handle_field_blur,
                self.config.handle_form_submit,
                self.config.handle_form_reset)
                
        # 設置狀態變化事件監聽器
        self.driver.execute_script("""
            window.addEventListener('formFieldChange', function(event) {
                window.dispatchEvent(new CustomEvent('formStateChange', {
                    detail: {
                        type: 'fieldChange',
                        field: event.detail
                    }
                }));
            });
            
            window.addEventListener('formFieldFocus', function(event) {
                window.dispatchEvent(new CustomEvent('formStateChange', {
                    detail: {
                        type: 'fieldFocus',
                        field: event.detail
                    }
                }));
            });
            
            window.addEventListener('formFieldBlur', function(event) {
                window.dispatchEvent(new CustomEvent('formStateChange', {
                    detail: {
                        type: 'fieldBlur',
                        field: event.detail
                    }
                }));
            });
            
            window.addEventListener('formSubmit', function(event) {
                window.dispatchEvent(new CustomEvent('formStateChange', {
                    detail: {
                        type: 'formSubmit',
                        form: event.detail
                    }
                }));
            });
            
            window.addEventListener('formReset', function(event) {
                window.dispatchEvent(new CustomEvent('formStateChange', {
                    detail: {
                        type: 'formReset',
                        form: event.detail
                    }
                }));
            });
        """)
        
    @handle_extractor_error()
    def remove_form_event_listeners(self, form_element: Any) -> None:
        """移除表單事件監聽器
        
        Args:
            form_element: 表單元素
        """
        self.driver.execute_script("""
            var form = arguments[0];
            var fields = form.querySelectorAll(arguments[1]);
            
            fields.forEach(function(field) {
                field.removeEventListener('change', null);
                field.removeEventListener('focus', null);
                field.removeEventListener('blur', null);
            });
            
            form.removeEventListener('submit', null);
            form.removeEventListener('reset', null);
            
            window.removeEventListener('formFieldChange', null);
            window.removeEventListener('formFieldFocus', null);
            window.removeEventListener('formFieldBlur', null);
            window.removeEventListener('formSubmit', null);
            window.removeEventListener('formReset', null);
            window.removeEventListener('formStateChange', null);
        """, form_element, self.config.input_selector)
        
    @handle_extractor_error()
    def get_form_event_history(self) -> List[Dict[str, Any]]:
        """獲取表單事件歷史
        
        Returns:
            List[Dict[str, Any]]: 事件歷史記錄
        """
        return self.driver.execute_script("""
            return window.formEventHistory || [];
        """)
        
    @handle_extractor_error()
    def clear_form_event_history(self) -> None:
        """清除表單事件歷史"""
        self.driver.execute_script("""
            window.formEventHistory = [];
        """)
        
    @handle_extractor_error()
    def track_form_events(
        self,
        form_element: Any,
        callback: Optional[Callable[[Dict[str, Any]], None]] = None
    ) -> List[Dict[str, Any]]:
        """追蹤表單事件
        
        Args:
            form_element: 表單元素
            callback: 事件回調函數
            
        Returns:
            List[Dict[str, Any]]: 事件歷史記錄
        """
        # 初始化事件歷史記錄
        self.driver.execute_script("""
            window.formEventHistory = [];
        """)
        
        # 設置事件監聽器
        self.setup_form_event_listeners(form_element)
        
        # 設置事件處理器
        def handle_event(event):
            event_data = {
                "timestamp": datetime.now().isoformat(),
                "type": event["type"],
                "detail": event["detail"]
            }
            
            self.driver.execute_script("""
                window.formEventHistory.push(arguments[0]);
            """, event_data)
            
            if callback:
                callback(event_data)
                
        self.driver.execute_script("""
            window.addEventListener('formStateChange', function(event) {
                window.dispatchEvent(new CustomEvent('formEventRecorded', {
                    detail: {
                        type: event.detail.type,
                        detail: event.detail
                    }
                }));
            });
        """)
        
        return self.get_form_event_history()
        
    @handle_extractor_error()
    def get_form_state_diff(
        self,
        old_state: Dict[str, Any],
        new_state: Dict[str, Any]
    ) -> Dict[str, Any]:
        """獲取表單狀態差異
        
        Args:
            old_state: 舊狀態
            new_state: 新狀態
            
        Returns:
            Dict[str, Any]: 狀態差異
        """
        diff = {
            "timestamp": datetime.now().isoformat(),
            "form_id": new_state["form_id"],
            "form_name": new_state["form_name"],
            "changes": {
                "form": {},
                "fields": {}
            }
        }
        
        # 檢查表單屬性變化
        for key in ["is_disabled", "is_readonly", "is_valid", "is_submitted"]:
            if old_state[key] != new_state[key]:
                diff["changes"]["form"][key] = {
                    "old": old_state[key],
                    "new": new_state[key]
                }
                
        # 檢查字段變化
        for field_name, new_field_state in new_state["fields"].items():
            if field_name in old_state["fields"]:
                old_field_state = old_state["fields"][field_name]
                field_diff = {}
                
                for key in ["value", "is_disabled", "is_readonly", "is_required", "is_valid"]:
                    if old_field_state[key] != new_field_state[key]:
                        field_diff[key] = {
                            "old": old_field_state[key],
                            "new": new_field_state[key]
                        }
                        
                if field_diff:
                    diff["changes"]["fields"][field_name] = field_diff
            else:
                diff["changes"]["fields"][field_name] = {
                    "added": True,
                    "state": new_field_state
                }
                
        # 檢查刪除的字段
        for field_name in old_state["fields"]:
            if field_name not in new_state["fields"]:
                diff["changes"]["fields"][field_name] = {
                    "deleted": True,
                    "state": old_state["fields"][field_name]
                }
                
        return diff
        
    @handle_extractor_error()
    def analyze_form_state_changes(
        self,
        state_history: Dict[str, List[Dict[str, Any]]]
    ) -> Dict[str, Any]:
        """分析表單狀態變化
        
        Args:
            state_history: 狀態歷史記錄
            
        Returns:
            Dict[str, Any]: 分析結果
        """
        analysis = {
            "total_changes": len(state_history["changes"]),
            "field_changes": {},
            "form_changes": {},
            "validation_changes": [],
            "submission_changes": []
        }
        
        # 分析字段變化
        for state in state_history["changes"]:
            for field_name, field_state in state["fields"].items():
                if field_name not in analysis["field_changes"]:
                    analysis["field_changes"][field_name] = {
                        "value_changes": 0,
                        "validation_changes": 0,
                        "state_changes": 0
                    }
                    
                field_analysis = analysis["field_changes"][field_name]
                
                if "value" in field_state:
                    field_analysis["value_changes"] += 1
                if "is_valid" in field_state:
                    field_analysis["validation_changes"] += 1
                if any(key in field_state for key in ["is_disabled", "is_readonly", "is_required"]):
                    field_analysis["state_changes"] += 1
                    
        # 分析表單變化
        for state in state_history["changes"]:
            for key, value in state.items():
                if key in ["is_disabled", "is_readonly"]:
                    if key not in analysis["form_changes"]:
                        analysis["form_changes"][key] = 0
                    analysis["form_changes"][key] += 1
                    
        # 分析驗證變化
        for state in state_history["changes"]:
            if "is_valid" in state:
                analysis["validation_changes"].append({
                    "timestamp": state["timestamp"],
                    "is_valid": state["is_valid"]
                })
                
        # 分析提交變化
        for state in state_history["changes"]:
            if "is_submitted" in state:
                analysis["submission_changes"].append({
                    "timestamp": state["timestamp"],
                    "is_submitted": state["is_submitted"]
                })
                
        return analysis
        
    @handle_extractor_error()
    def get_form_state_summary(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """獲取表單狀態摘要
        
        Args:
            state: 表單狀態
            
        Returns:
            Dict[str, Any]: 狀態摘要
        """
        summary = {
            "timestamp": state["timestamp"],
            "form_id": state["form_id"],
            "form_name": state["form_name"],
            "total_fields": len(state["fields"]),
            "valid_fields": 0,
            "invalid_fields": 0,
            "required_fields": 0,
            "optional_fields": 0,
            "disabled_fields": 0,
            "readonly_fields": 0,
            "field_types": {}
        }
        
        for field_name, field_state in state["fields"].items():
            field_type = field_state["type"]
            
            if field_type not in summary["field_types"]:
                summary["field_types"][field_type] = 0
            summary["field_types"][field_type] += 1
            
            if field_state["is_valid"]:
                summary["valid_fields"] += 1
            else:
                summary["invalid_fields"] += 1
                
            if field_state["is_required"]:
                summary["required_fields"] += 1
            else:
                summary["optional_fields"] += 1
                
            if field_state["is_disabled"]:
                summary["disabled_fields"] += 1
                
            if field_state["is_readonly"]:
                summary["readonly_fields"] += 1
                
        return summary 