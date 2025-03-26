#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from selenium import webdriver


class HoneypotDetector:
    """檢測蜜罐和陷阱"""
    
    def __init__(self, logger=None):
        """
        初始化蜜罐檢測器
        
        Args:
            logger: 日誌記錄器
        """
        self.logger = logger or logging.getLogger(__name__)
    
    def detect(self, driver: webdriver.Remote) -> bool:
        """
        檢測頁面中的蜜罐和陷阱
        
        Args:
            driver: WebDriver實例
            
        Returns:
            是否檢測到蜜罐
        """
        try:
            # 檢測隱藏元素陷阱
            honeypot_script = """
            // 檢測隱藏元素陷阱
            const honeypots = [];
            
            // 查找隱藏元素
            const elements = document.querySelectorAll('*');
            for (const element of elements) {
                const style = window.getComputedStyle(element);
                
                // 檢查是否為隱藏元素但可點擊
                if ((style.display === 'none' || style.visibility === 'hidden' || 
                     style.opacity === '0' || 
                     (element.getBoundingClientRect().width === 0 && element.getBoundingClientRect().height === 0)) &&
                    (element.tagName === 'A' || element.tagName === 'BUTTON' || 
                     element.onclick || element.getAttribute('role') === 'button')) {
                    honeypots.push({
                        tag: element.tagName,
                        id: element.id,
                        class: element.className,
                        type: 'hidden_clickable'
                    });
                }
                
                // 檢查不可見但可填寫的輸入框
                if ((style.display === 'none' || style.visibility === 'hidden' || style.opacity === '0') &&
                    (element.tagName === 'INPUT' || element.tagName === 'TEXTAREA')) {
                    honeypots.push({
                        tag: element.tagName,
                        id: element.id,
                        class: element.className,
                        type: 'hidden_input'
                    });
                }
            }
            
            return honeypots;
            """
            
            honeypots = driver.execute_script(honeypot_script)
            
            if honeypots:
                self.logger.warning(f"檢測到 {len(honeypots)} 個蜜罐元素")
                for honeypot in honeypots[:5]:  # 僅顯示前5個
                    self.logger.debug(f"蜜罐元素: {honeypot}")
                return True
            
            # 檢測行為監控腳本
            monitoring_script = """
            // 檢測行為監控腳本
            const monitoringScripts = [];
            
            // 檢查是否有監聽全局鼠標和鍵盤事件
            if (window.__originalAddEventListener) {
                monitoringScripts.push({ type: 'event_listener_override', detail: 'addEventListener has been overridden' });
            }
            
            // 檢查是否有常見的反爬工具
            for (const key of Object.keys(window)) {
                if (key.includes('captcha') || key.includes('monitor') || key.includes('track') || 
                    key.includes('detect') || key.includes('spider') || key.includes('bot')) {
                    monitoringScripts.push({ type: 'suspicious_global', name: key });
                }
            }
            
            return monitoringScripts;
            """
            
            monitoring_results = driver.execute_script(monitoring_script)
            
            if monitoring_results:
                self.logger.warning(f"檢測到 {len(monitoring_results)} 個監控腳本")
                for script in monitoring_results[:5]:  # 僅顯示前5個
                    self.logger.debug(f"監控腳本: {script}")
                return True
            
            return False
        
        except Exception as e:
            self.logger.error(f"檢測蜜罐失敗: {str(e)}")
            return False