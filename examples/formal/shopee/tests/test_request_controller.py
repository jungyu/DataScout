"""
請求控制測試模組

此模組提供以下測試：
- 請求控制初始化測試
- 請求頻率限制測試
- 請求重試策略測試
- 請求標頭管理測試
- 請求日誌記錄測試
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta

from core.request_controller import RequestController
from config import BaseConfig

@pytest.fixture
def config():
    """建立測試用的配置物件"""
    return BaseConfig()

@pytest.fixture
def request_controller(config):
    """建立測試用的請求控制物件"""
    return RequestController(config)

def test_init(request_controller, config):
    """測試請求控制初始化"""
    assert request_controller.config == config
    assert request_controller.request_records is not None
    assert request_controller.headers is not None

def test_check_rate_limit(request_controller):
    """測試請求頻率限制"""
    # 模擬請求記錄
    request_controller.request_records = {
        "search": [
            datetime.now() - timedelta(seconds=30),
            datetime.now() - timedelta(seconds=20),
            datetime.now() - timedelta(seconds=10)
        ]
    }
    
    # 檢查頻率限制
    assert request_controller.check_rate_limit("search") is True
    
    # 模擬超過頻率限制
    request_controller.request_records["search"].append(datetime.now())
    assert request_controller.check_rate_limit("search") is False

def test_update_request_record(request_controller):
    """測試更新請求記錄"""
    # 更新請求記錄
    request_controller.update_request_record("search")
    
    # 檢查記錄
    assert "search" in request_controller.request_records
    assert len(request_controller.request_records["search"]) == 1
    assert isinstance(request_controller.request_records["search"][0], datetime)

def test_generate_headers(request_controller):
    """測試生成請求標頭"""
    # 生成標頭
    headers = request_controller.generate_headers()
    
    # 檢查標頭
    assert "User-Agent" in headers
    assert "Accept-Language" in headers
    assert "Accept-Encoding" in headers

def test_rotate_user_agent(request_controller):
    """測試輪換使用者代理"""
    # 模擬使用者代理列表
    request_controller.user_agents = ["agent1", "agent2", "agent3"]
    
    # 輪換使用者代理
    user_agent = request_controller.rotate_user_agent()
    
    # 檢查使用者代理
    assert user_agent in request_controller.user_agents

def test_rotate_referer(request_controller):
    """測試輪換參照頁面"""
    # 模擬參照頁面列表
    request_controller.referers = ["referer1", "referer2", "referer3"]
    
    # 輪換參照頁面
    referer = request_controller.rotate_referer()
    
    # 檢查參照頁面
    assert referer in request_controller.referers

def test_cleanup_old_records(request_controller):
    """測試清理舊記錄"""
    # 模擬舊記錄
    request_controller.request_records = {
        "search": [
            datetime.now() - timedelta(days=2),
            datetime.now() - timedelta(days=1),
            datetime.now()
        ]
    }
    
    # 清理舊記錄
    request_controller.cleanup_old_records()
    
    # 檢查記錄
    assert len(request_controller.request_records["search"]) == 1
    assert request_controller.request_records["search"][0] > datetime.now() - timedelta(days=1) 