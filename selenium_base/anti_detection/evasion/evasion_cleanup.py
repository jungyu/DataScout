#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
規避腳本清理模組

此模組提供規避腳本清理功能，包括：
1. 腳本還原
2. 腳本移除
3. 腳本重置
"""

from typing import Dict, List, Optional

from selenium.webdriver.remote.webdriver import WebDriver

from .base_error import AntiDetectionError, handle_error

class EvasionCleanup:
    """規避腳本清理類"""
    
    @staticmethod
    @handle_error()
    def cleanup_webgl(driver: WebDriver) -> None:
        """
        清理 WebGL 腳本
        
        Args:
            driver: WebDriver 實例
        """
        driver.execute_script("""
            const canvas = document.createElement('canvas');
            const gl = canvas.getContext('webgl');
            if (gl) {
                gl.getParameter = function(parameter) {
                    return gl.getParameter.original.call(gl, parameter);
                };
            }
        """)
        
    @staticmethod
    @handle_error()
    def cleanup_canvas(driver: WebDriver) -> None:
        """
        清理 Canvas 腳本
        
        Args:
            driver: WebDriver 實例
        """
        driver.execute_script("""
            const canvas = document.createElement('canvas');
            const ctx = canvas.getContext('2d');
            if (ctx) {
                ctx.fillText = ctx.fillText.original;
                ctx.getImageData = ctx.getImageData.original;
            }
        """)
        
    @staticmethod
    @handle_error()
    def cleanup_audio(driver: WebDriver) -> None:
        """
        清理 Audio 腳本
        
        Args:
            driver: WebDriver 實例
        """
        driver.execute_script("""
            if (window.AudioContext) {
                AudioContext.prototype.createBuffer = AudioContext.prototype.createBuffer.original;
            }
        """)
        
    @staticmethod
    @handle_error()
    def cleanup_font(driver: WebDriver) -> None:
        """
        清理字體腳本
        
        Args:
            driver: WebDriver 實例
        """
        driver.execute_script("""
            if (window.matchMedia) {
                matchMedia = matchMedia.original;
            }
        """)
        
    @staticmethod
    @handle_error()
    def cleanup_plugin(driver: WebDriver) -> None:
        """
        清理插件腳本
        
        Args:
            driver: WebDriver 實例
        """
        driver.execute_script("""
            if (navigator.plugins) {
                Object.defineProperty(navigator, 'plugins', {
                    get: function() {
                        return navigator.plugins.original;
                    }
                });
            }
        """)
        
    @staticmethod
    @handle_error()
    def cleanup_timezone(driver: WebDriver) -> None:
        """
        清理時區腳本
        
        Args:
            driver: WebDriver 實例
        """
        driver.execute_script("""
            Date.prototype.getTimezoneOffset = Date.prototype.getTimezoneOffset.original;
        """)
        
    @staticmethod
    @handle_error()
    def cleanup_language(driver: WebDriver) -> None:
        """
        清理語言腳本
        
        Args:
            driver: WebDriver 實例
        """
        driver.execute_script("""
            Object.defineProperty(navigator, 'language', {
                get: function() {
                    return navigator.language.original;
                }
            });
        """)
        
    @staticmethod
    @handle_error()
    def cleanup_screen(driver: WebDriver) -> None:
        """
        清理屏幕腳本
        
        Args:
            driver: WebDriver 實例
        """
        driver.execute_script("""
            Object.defineProperties(window.screen, {
                width: {
                    get: function() {
                        return window.screen.width.original;
                    }
                },
                height: {
                    get: function() {
                        return window.screen.height.original;
                    }
                },
                colorDepth: {
                    get: function() {
                        return window.screen.colorDepth.original;
                    }
                }
            });
        """)
        
    @classmethod
    @handle_error()
    def cleanup_all(cls, driver: WebDriver) -> None:
        """
        清理所有腳本
        
        Args:
            driver: WebDriver 實例
        """
        cls.cleanup_webgl(driver)
        cls.cleanup_canvas(driver)
        cls.cleanup_audio(driver)
        cls.cleanup_font(driver)
        cls.cleanup_plugin(driver)
        cls.cleanup_timezone(driver)
        cls.cleanup_language(driver)
        cls.cleanup_screen(driver)
        
    @classmethod
    @handle_error()
    def cleanup_script(cls, driver: WebDriver, name: str) -> None:
        """
        清理指定腳本
        
        Args:
            driver: WebDriver 實例
            name: 腳本名稱
        """
        cleanup_method = getattr(cls, f'cleanup_{name}', None)
        if cleanup_method:
            cleanup_method(driver)
        else:
            raise AntiDetectionError(f"未知的腳本名稱: {name}") 