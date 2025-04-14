"""
爬蟲核心功能測試模組

此模組提供以下測試：
- 爬蟲初始化測試
- 商品搜尋測試
- 商品詳情測試
- 錯誤處理測試
"""

import pytest
from unittest.mock import MagicMock, patch, Mock
from datetime import datetime

from src.core.shopee_crawler import ShopeeCrawler
from src.core.exceptions import CrawlerException
from config import BaseConfig

@pytest.fixture
def config():
    """建立測試用的配置物件"""
    return BaseConfig()

@pytest.fixture
def crawler(config):
    """建立測試用的爬蟲物件"""
    return ShopeeCrawler(config)

def test_init(crawler, config):
    """測試爬蟲初始化"""
    assert crawler.config == config
    assert crawler.browser_profile is not None
    assert crawler.request_controller is not None
    assert crawler.browser_fingerprint is not None

def test_search_products(crawler):
    """測試商品搜尋功能"""
    with patch.object(crawler, 'navigate') as mock_navigate:
        with patch.object(crawler, 'wait_for_element') as mock_wait:
            mock_wait.return_value = Mock()
            result = crawler.search_products("測試商品")
            assert isinstance(result, list)
            mock_navigate.assert_called_once()
            mock_wait.assert_called()

def test_get_product_details(crawler):
    """測試商品詳情爬取功能"""
    with patch.object(crawler, 'navigate') as mock_navigate:
        with patch.object(crawler, 'wait_for_element') as mock_wait:
            mock_wait.return_value = Mock()
            result = crawler.get_product_details("https://shopee.tw/test")
            assert isinstance(result, dict)
            mock_navigate.assert_called_once()
            mock_wait.assert_called()

def test_check_and_handle_captcha(crawler):
    """測試驗證碼處理功能"""
    with patch.object(crawler, 'wait_for_element') as mock_wait:
        mock_wait.return_value = None
        result = crawler.check_and_handle_captcha()
        assert result is False
        mock_wait.assert_called_once()

def test_search_products_error(crawler):
    """測試商品搜尋錯誤"""
    # 模擬瀏覽器操作失敗
    with patch.object(crawler.browser_profile, "get_page") as mock_get_page:
        mock_get_page.side_effect = Exception("搜尋失敗")
        
        # 檢查錯誤
        with pytest.raises(CrawlerException) as exc_info:
            crawler.search_products("測試")
        
        # 檢查錯誤訊息
        assert "搜尋失敗" in str(exc_info.value)

def test_get_product_details_error(crawler):
    """測試商品詳情爬取錯誤"""
    # 模擬瀏覽器操作失敗
    with patch.object(crawler.browser_profile, "get_page") as mock_get_page:
        mock_get_page.side_effect = Exception("詳情爬取失敗")
        
        # 檢查錯誤
        with pytest.raises(CrawlerException) as exc_info:
            crawler.get_product_details("123456")
        
        # 檢查錯誤訊息
        assert "詳情爬取失敗" in str(exc_info.value)

def test_parse_search_results(crawler):
    """測試搜尋結果解析"""
    # 模擬 HTML 內容
    mock_html = """
    <div class="product-card">
        <div class="product-id">123456</div>
        <div class="product-name">測試商品1</div>
        <div class="product-price">100</div>
        <div class="product-rating">4.5</div>
        <div class="product-sold">1000</div>
    </div>
    """
    
    # 模擬頁面物件
    mock_page = MagicMock()
    mock_page.get_attribute.return_value = mock_html
    
    # 執行解析
    results = crawler._parse_search_results(mock_page)
    
    # 檢查結果
    assert len(results) == 1
    assert results[0]["id"] == "123456"
    assert results[0]["name"] == "測試商品1"
    assert results[0]["price"] == 100
    assert results[0]["rating"] == 4.5
    assert results[0]["sold"] == 1000

def test_parse_product_details(crawler):
    """測試商品詳情解析"""
    # 模擬 HTML 內容
    mock_html = """
    <div class="product-detail">
        <div class="product-id">123456</div>
        <div class="product-name">測試商品</div>
        <div class="product-price">100</div>
        <div class="product-rating">4.5</div>
        <div class="product-sold">1000</div>
        <div class="product-description">測試描述</div>
        <div class="product-specifications">
            <div class="spec-item">
                <span class="spec-name">顏色</span>
                <span class="spec-value">紅色</span>
            </div>
            <div class="spec-item">
                <span class="spec-name">尺寸</span>
                <span class="spec-value">M</span>
            </div>
        </div>
        <div class="product-images">
            <img src="http://example.com/image1.jpg">
            <img src="http://example.com/image2.jpg">
        </div>
    </div>
    """
    
    # 模擬頁面物件
    mock_page = MagicMock()
    mock_page.get_attribute.return_value = mock_html
    
    # 執行解析
    details = crawler._parse_product_details(mock_page)
    
    # 檢查結果
    assert details["id"] == "123456"
    assert details["name"] == "測試商品"
    assert details["price"] == 100
    assert details["rating"] == 4.5
    assert details["sold"] == 1000
    assert details["description"] == "測試描述"
    assert details["specifications"]["顏色"] == "紅色"
    assert details["specifications"]["尺寸"] == "M"
    assert len(details["images"]) == 2 