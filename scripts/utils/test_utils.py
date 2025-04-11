#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
測試工具類
提供測試過程中的各種工具方法
"""

import os
import sys
import pytest
import subprocess
from pathlib import Path
from typing import List, Dict, Any

class TestUtils:
    """測試工具類"""
    
    def __init__(self):
        """初始化"""
        self.project_root = Path(__file__).parent.parent.parent
        self.test_dir = self.project_root / "tests"
        self.report_dir = self.project_root / "reports"
        self.coverage_dir = self.report_dir / "coverage"
    
    def setup_test_env(self) -> None:
        """設置測試環境"""
        # 創建報告目錄
        self.report_dir.mkdir(parents=True, exist_ok=True)
        self.coverage_dir.mkdir(parents=True, exist_ok=True)
        
        # 設置環境變量
        os.environ["PYTHONPATH"] = str(self.project_root)
        os.environ["TESTING"] = "true"
    
    def run_tests(self) -> None:
        """執行測試"""
        # 構建測試命令
        cmd = [
            sys.executable, "-m", "pytest",
            str(self.test_dir),
            "--cov=src",
            "--cov-report=html",
            "--cov-report=term",
            f"--cov-report-dir={self.coverage_dir}",
            "-v"
        ]
        
        # 執行測試
        subprocess.check_call(cmd)
    
    def generate_report(self) -> None:
        """生成測試報告"""
        # 構建報告命令
        cmd = [
            sys.executable, "-m", "pytest",
            str(self.test_dir),
            "--cov=src",
            "--cov-report=html",
            f"--cov-report-dir={self.coverage_dir}",
            "--junitxml=reports/junit.xml"
        ]
        
        # 生成報告
        subprocess.check_call(cmd)
    
    def run_specific_tests(self, test_paths: List[str]) -> None:
        """
        執行指定的測試
        
        Args:
            test_paths: 測試路徑列表
        """
        # 構建測試命令
        cmd = [
            sys.executable, "-m", "pytest",
            *test_paths,
            "--cov=src",
            "--cov-report=term",
            "-v"
        ]
        
        # 執行測試
        subprocess.check_call(cmd)
    
    def run_with_markers(self, markers: List[str]) -> None:
        """
        執行帶有特定標記的測試
        
        Args:
            markers: 標記列表
        """
        # 構建測試命令
        cmd = [
            sys.executable, "-m", "pytest",
            str(self.test_dir),
            "-m", " or ".join(markers),
            "--cov=src",
            "--cov-report=term",
            "-v"
        ]
        
        # 執行測試
        subprocess.check_call(cmd)
    
    def cleanup_test_env(self) -> None:
        """清理測試環境"""
        # 刪除臨時文件
        temp_dir = self.project_root / "temp"
        if temp_dir.exists():
            import shutil
            shutil.rmtree(temp_dir)
        
        # 重置環境變量
        if "TESTING" in os.environ:
            del os.environ["TESTING"] 