#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
測試蝦皮驗證碼求解器
"""

import pytest
from unittest.mock import Mock, patch
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from src.captcha.solvers.shopee_solver import ShopeeSolver
from src.captcha.types import CaptchaConfig, CaptchaResult


@pytest.fixture
def solver():
    """創建驗證碼求解器實例"""
    config = CaptchaConfig(
        type="slider",
        screenshot_dir="/tmp/captcha",
        max_retries=3,
        timeout=10
    )
    return ShopeeSolver(config)


@pytest.fixture
def mock_driver():
    """模擬WebDriver"""
    driver = Mock(spec=WebDriver)
    
    # 模擬action_chains
    action_chain = Mock()
    action_chain.move_to_element.return_value = action_chain
    action_chain.click_and_hold.return_value = action_chain
    action_chain.move_by_offset.return_value = action_chain
    action_chain.release.return_value = action_chain
    action_chain.perform.return_value = None
    
    driver.action_chains = action_chain
    return driver


@pytest.fixture
def mock_element():
    """模擬驗證碼元素"""
    element = Mock(spec=WebElement)
    element.size = {'width': 300, 'height': 150}
    return element


def test_init(solver):
    """測試初始化"""
    assert solver.shopee_config['slider_selector'] == '.shopee-slider__button'
    assert solver.shopee_config['timeout'] == 10
    assert solver.shopee_config['move_delay'] == 0.1


def test_generate_tracks(solver):
    """測試生成滑動軌跡"""
    distance = 100
    tracks = solver._generate_tracks(distance)
    
    assert isinstance(tracks, list)
    assert len(tracks) > 0
    assert sum(tracks) >= distance


def test_solve_success(solver, mock_driver, mock_element):
    """測試成功求解驗證碼"""
    # 模擬滑塊元素
    slider = Mock(spec=WebElement)
    slider.size = {'width': 40, 'height': 40}
    mock_driver.find_element.return_value = slider
    
    # 模擬滑軌元素
    track = Mock(spec=WebElement)
    track.size = {'width': 300, 'height': 40}
    mock_driver.find_element.return_value = track
    
    # 模擬成功元素
    success = Mock(spec=WebElement)
    mock_driver.find_element.return_value = success
    
    result = solver.solve(mock_driver, mock_element)
    
    assert isinstance(result, CaptchaResult)
    assert result.success is True
    assert "成功" in result.message
    assert isinstance(result.solution, dict)
    assert "distance" in result.solution
    assert "tracks" in result.solution


def test_solve_failure_timeout(solver, mock_driver, mock_element):
    """測試求解超時失敗"""
    mock_driver.find_element.side_effect = TimeoutException()
    
    result = solver.solve(mock_driver, mock_element)
    
    assert isinstance(result, CaptchaResult)
    assert result.success is False
    assert "超時" in result.error


def test_solve_failure_no_success(solver, mock_driver, mock_element):
    """測試滑動失敗"""
    # 模擬滑塊元素
    slider = Mock(spec=WebElement)
    slider.size = {'width': 40, 'height': 40}
    mock_driver.find_element.return_value = slider
    
    # 模擬滑軌元素
    track = Mock(spec=WebElement)
    track.size = {'width': 300, 'height': 40}
    mock_driver.find_element.return_value = track
    
    # 模擬找不到成功元素
    mock_driver.find_element.side_effect = NoSuchElementException()
    
    result = solver.solve(mock_driver, mock_element)
    
    assert isinstance(result, CaptchaResult)
    assert result.success is False
    assert "失敗" in result.message


def test_save_screenshot(solver, mock_driver):
    """測試保存截圖"""
    # 模擬驗證碼容器
    container = Mock(spec=WebElement)
    container.screenshot.return_value = True
    mock_driver.find_element.return_value = container
    
    filepath = solver._save_screenshot(mock_driver)
    
    assert isinstance(filepath, str)
    assert filepath.startswith("/tmp/captcha")
    assert filepath.endswith(".png") 