#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
隱身管理器模組

此模組提供隱藏自動化特徵的功能，包括：
1. WebDriver 特徵隱藏
2. 自動化標誌隱藏
3. 開發者工具隱藏
4. 控制台日誌隱藏
5. 性能監控隱藏
"""

import json
import time
from typing import Dict, List, Optional, Union, Any

from selenium.webdriver.remote.webdriver import WebDriver

from ..base_manager import BaseManager
from ..base_error import AntiDetectionError, handle_error

class StealthManager(BaseManager):
    """隱身管理器類"""
    
    def __init__(self, driver: WebDriver, config: Optional[Dict] = None):
        """
        初始化隱身管理器
        
        Args:
            driver: WebDriver 實例
            config: 配置字典
        """
        super().__init__(driver, config)
        self.stealth_status = {}
        self.stealth_history = []
        
    @handle_error()
    def setup(self) -> None:
        """設置隱身管理器"""
        self._load_config()
        self._hide_webdriver()
        self._hide_automation()
        self._hide_devtools()
        self._hide_console()
        self._hide_performance()
        self._validate_stealth()
        
    @handle_error()
    def cleanup(self) -> None:
        """清理隱身管理器"""
        self._restore_webdriver()
        self._restore_automation()
        self._restore_devtools()
        self._restore_console()
        self._restore_performance()
        self.stealth_status = {}
        
    @handle_error()
    def _load_config(self) -> None:
        """加載配置"""
        if not self.config:
            self.config = {
                'hide_webdriver': True,
                'hide_automation': True,
                'hide_devtools': True,
                'hide_console': True,
                'hide_performance': True,
                'webdriver_flags': [
                    'webdriver',
                    '_selenium',
                    'callSelenium',
                    '_Selenium_IDE_Recorder',
                    '_phantom',
                    'domAutomation',
                    'domAutomationController'
                ],
                'automation_flags': [
                    'navigator.webdriver',
                    'window.chrome',
                    'window.__nightmare',
                    'window._phantom',
                    'window.callPhantom',
                    'window.__webdriver_evaluate',
                    'window.__selenium_evaluate',
                    'window.__webdriver_script_fn',
                    'window.__selenium_script_fn',
                    'window.__webdriver_script_fn',
                    'window.__fxdriver_evaluate',
                    'window.__driver_evaluate',
                    'window.__webdriver_unwrapped',
                    'window.__webdriver_script_fn_unwrapped',
                    'window.__fxdriver_unwrapped',
                    'window.__driver_unwrapped',
                    'window.__webdriver_evaluate',
                    'window.__selenium_evaluate',
                    'window.__webdriver_script_fn',
                    'window.__selenium_script_fn',
                    'window.__webdriver_script_fn',
                    'window.__fxdriver_evaluate',
                    'window.__driver_evaluate',
                    'window.__webdriver_unwrapped',
                    'window.__webdriver_script_fn_unwrapped',
                    'window.__fxdriver_unwrapped',
                    'window.__driver_unwrapped'
                ],
                'devtools_flags': [
                    'window.console.debug',
                    'window.console.info',
                    'window.console.warn',
                    'window.console.error',
                    'window.console.log',
                    'window.console.trace',
                    'window.console.dir',
                    'window.console.dirxml',
                    'window.console.group',
                    'window.console.groupEnd',
                    'window.console.time',
                    'window.console.timeEnd',
                    'window.console.assert',
                    'window.console.count',
                    'window.console.markTimeline',
                    'window.console.profile',
                    'window.console.profileEnd',
                    'window.console.clear',
                    'window.console.memory'
                ],
                'performance_flags': [
                    'window.performance',
                    'window.performance.memory',
                    'window.performance.timing',
                    'window.performance.navigation',
                    'window.performance.getEntries',
                    'window.performance.getEntriesByType',
                    'window.performance.getEntriesByName',
                    'window.performance.mark',
                    'window.performance.measure',
                    'window.performance.clearMarks',
                    'window.performance.clearMeasures',
                    'window.performance.now'
                ]
            }
            
    @handle_error()
    def _hide_webdriver(self) -> None:
        """隱藏 WebDriver 特徵"""
        try:
            # 隱藏 WebDriver 標誌
            self.driver.execute_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
                
                // 隱藏其他 WebDriver 相關標誌
                const flags = arguments[0];
                for (const flag of flags) {
                    Object.defineProperty(window, flag, {
                        get: () => undefined
                    });
                }
            """, self.config['webdriver_flags'])
            
            self.stealth_status['webdriver'] = True
            self.logger.info("成功隱藏 WebDriver 特徵")
        except Exception as e:
            self.logger.error(f"隱藏 WebDriver 特徵失敗: {str(e)}")
            raise
            
    @handle_error()
    def _hide_automation(self) -> None:
        """隱藏自動化標誌"""
        try:
            # 隱藏自動化標誌
            self.driver.execute_script("""
                const flags = arguments[0];
                for (const flag of flags) {
                    const parts = flag.split('.');
                    let obj = window;
                    for (let i = 0; i < parts.length - 1; i++) {
                        obj = obj[parts[i]];
                    }
                    const prop = parts[parts.length - 1];
                    Object.defineProperty(obj, prop, {
                        get: () => undefined
                    });
                }
            """, self.config['automation_flags'])
            
            self.stealth_status['automation'] = True
            self.logger.info("成功隱藏自動化標誌")
        except Exception as e:
            self.logger.error(f"隱藏自動化標誌失敗: {str(e)}")
            raise
            
    @handle_error()
    def _hide_devtools(self) -> None:
        """隱藏開發者工具"""
        try:
            # 隱藏開發者工具
            self.driver.execute_script("""
                const flags = arguments[0];
                for (const flag of flags) {
                    const parts = flag.split('.');
                    let obj = window;
                    for (let i = 0; i < parts.length - 1; i++) {
                        obj = obj[parts[i]];
                    }
                    const prop = parts[parts.length - 1];
                    Object.defineProperty(obj, prop, {
                        get: () => undefined
                    });
                }
            """, self.config['devtools_flags'])
            
            self.stealth_status['devtools'] = True
            self.logger.info("成功隱藏開發者工具")
        except Exception as e:
            self.logger.error(f"隱藏開發者工具失敗: {str(e)}")
            raise
            
    @handle_error()
    def _hide_console(self) -> None:
        """隱藏控制台日誌"""
        try:
            # 隱藏控制台日誌
            self.driver.execute_script("""
                const originalConsole = window.console;
                window.console = {
                    debug: () => {},
                    info: () => {},
                    warn: () => {},
                    error: () => {},
                    log: () => {},
                    trace: () => {},
                    dir: () => {},
                    dirxml: () => {},
                    group: () => {},
                    groupEnd: () => {},
                    time: () => {},
                    timeEnd: () => {},
                    assert: () => {},
                    count: () => {},
                    markTimeline: () => {},
                    profile: () => {},
                    profileEnd: () => {},
                    clear: () => {},
                    memory: {}
                };
            """)
            
            self.stealth_status['console'] = True
            self.logger.info("成功隱藏控制台日誌")
        except Exception as e:
            self.logger.error(f"隱藏控制台日誌失敗: {str(e)}")
            raise
            
    @handle_error()
    def _hide_performance(self) -> None:
        """隱藏性能監控"""
        try:
            # 隱藏性能監控
            self.driver.execute_script("""
                const flags = arguments[0];
                for (const flag of flags) {
                    const parts = flag.split('.');
                    let obj = window;
                    for (let i = 0; i < parts.length - 1; i++) {
                        obj = obj[parts[i]];
                    }
                    const prop = parts[parts.length - 1];
                    Object.defineProperty(obj, prop, {
                        get: () => undefined
                    });
                }
            """, self.config['performance_flags'])
            
            self.stealth_status['performance'] = True
            self.logger.info("成功隱藏性能監控")
        except Exception as e:
            self.logger.error(f"隱藏性能監控失敗: {str(e)}")
            raise
            
    @handle_error()
    def _validate_stealth(self) -> None:
        """驗證隱身效果"""
        try:
            # 檢查 WebDriver 特徵
            webdriver_hidden = self.driver.execute_script("""
                return !navigator.webdriver;
            """)
            
            # 檢查自動化標誌
            automation_hidden = self.driver.execute_script("""
                const flags = arguments[0];
                for (const flag of flags) {
                    const parts = flag.split('.');
                    let obj = window;
                    for (let i = 0; i < parts.length - 1; i++) {
                        if (!obj[parts[i]]) return false;
                        obj = obj[parts[i]];
                    }
                    if (obj[parts[parts.length - 1]] !== undefined) return false;
                }
                return true;
            """, self.config['automation_flags'])
            
            # 檢查開發者工具
            devtools_hidden = self.driver.execute_script("""
                return !window.console.debug;
            """)
            
            # 檢查控制台日誌
            console_hidden = self.driver.execute_script("""
                return window.console.log.toString() === 'function () {}';
            """)
            
            # 檢查性能監控
            performance_hidden = self.driver.execute_script("""
                return !window.performance.memory;
            """)
            
            # 更新隱身狀態
            self.stealth_status.update({
                'webdriver_hidden': webdriver_hidden,
                'automation_hidden': automation_hidden,
                'devtools_hidden': devtools_hidden,
                'console_hidden': console_hidden,
                'performance_hidden': performance_hidden
            })
            
            # 記錄驗證結果
            self.stealth_history.append({
                'timestamp': time.time(),
                'status': self.stealth_status.copy()
            })
            
            # 限制歷史記錄大小
            if len(self.stealth_history) > 10:
                self.stealth_history.pop(0)
                
            self.logger.info("隱身效果驗證完成")
        except Exception as e:
            self.logger.error(f"驗證隱身效果失敗: {str(e)}")
            raise
            
    @handle_error()
    def _restore_webdriver(self) -> None:
        """恢復 WebDriver 特徵"""
        try:
            self.driver.execute_script("""
                delete Object.getOwnPropertyDescriptor(navigator, 'webdriver');
            """)
            self.stealth_status['webdriver'] = False
            self.logger.info("成功恢復 WebDriver 特徵")
        except Exception as e:
            self.logger.error(f"恢復 WebDriver 特徵失敗: {str(e)}")
            raise
            
    @handle_error()
    def _restore_automation(self) -> None:
        """恢復自動化標誌"""
        try:
            self.driver.execute_script("""
                const flags = arguments[0];
                for (const flag of flags) {
                    const parts = flag.split('.');
                    let obj = window;
                    for (let i = 0; i < parts.length - 1; i++) {
                        obj = obj[parts[i]];
                    }
                    delete Object.getOwnPropertyDescriptor(obj, parts[parts.length - 1]);
                }
            """, self.config['automation_flags'])
            self.stealth_status['automation'] = False
            self.logger.info("成功恢復自動化標誌")
        except Exception as e:
            self.logger.error(f"恢復自動化標誌失敗: {str(e)}")
            raise
            
    @handle_error()
    def _restore_devtools(self) -> None:
        """恢復開發者工具"""
        try:
            self.driver.execute_script("""
                const flags = arguments[0];
                for (const flag of flags) {
                    const parts = flag.split('.');
                    let obj = window;
                    for (let i = 0; i < parts.length - 1; i++) {
                        obj = obj[parts[i]];
                    }
                    delete Object.getOwnPropertyDescriptor(obj, parts[parts.length - 1]);
                }
            """, self.config['devtools_flags'])
            self.stealth_status['devtools'] = False
            self.logger.info("成功恢復開發者工具")
        except Exception as e:
            self.logger.error(f"恢復開發者工具失敗: {str(e)}")
            raise
            
    @handle_error()
    def _restore_console(self) -> None:
        """恢復控制台日誌"""
        try:
            self.driver.execute_script("""
                window.console = window.originalConsole;
            """)
            self.stealth_status['console'] = False
            self.logger.info("成功恢復控制台日誌")
        except Exception as e:
            self.logger.error(f"恢復控制台日誌失敗: {str(e)}")
            raise
            
    @handle_error()
    def _restore_performance(self) -> None:
        """恢復性能監控"""
        try:
            self.driver.execute_script("""
                const flags = arguments[0];
                for (const flag of flags) {
                    const parts = flag.split('.');
                    let obj = window;
                    for (let i = 0; i < parts.length - 1; i++) {
                        obj = obj[parts[i]];
                    }
                    delete Object.getOwnPropertyDescriptor(obj, parts[parts.length - 1]);
                }
            """, self.config['performance_flags'])
            self.stealth_status['performance'] = False
            self.logger.info("成功恢復性能監控")
        except Exception as e:
            self.logger.error(f"恢復性能監控失敗: {str(e)}")
            raise
            
    @handle_error()
    def get_stealth_status(self) -> Dict[str, bool]:
        """
        獲取隱身狀態
        
        Returns:
            隱身狀態字典
        """
        return self.stealth_status.copy()
        
    @handle_error()
    def get_stealth_history(self) -> List[Dict[str, Any]]:
        """
        獲取隱身歷史
        
        Returns:
            隱身歷史列表
        """
        return self.stealth_history.copy()
        
    @handle_error()
    def save_stealth_status(self, file_path: str) -> None:
        """
        保存隱身狀態到文件
        
        Args:
            file_path: 文件路徑
        """
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump({
                    'stealth_status': self.stealth_status,
                    'stealth_history': self.stealth_history,
                    'config': self.config
                }, f, ensure_ascii=False, indent=2)
            self.logger.info(f"隱身狀態已保存到: {file_path}")
        except Exception as e:
            self.logger.error(f"保存隱身狀態失敗: {str(e)}")
            raise
            
    @handle_error()
    def load_stealth_status(self, file_path: str) -> None:
        """
        從文件加載隱身狀態
        
        Args:
            file_path: 文件路徑
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            self.stealth_status = data.get('stealth_status', {})
            self.stealth_history = data.get('stealth_history', [])
            self.config.update(data.get('config', {}))
            
            self.logger.info(f"已從 {file_path} 加載隱身狀態")
        except Exception as e:
            self.logger.error(f"加載隱身狀態失敗: {str(e)}")
            raise 