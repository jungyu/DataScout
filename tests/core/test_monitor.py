"""
任務監控模組測試

測試以下功能：
1. 任務狀態監控
2. 進度追蹤
3. 資源監控
4. 錯誤處理
5. 檢查點管理
"""

import os
import time
import json
import pytest
import signal
from unittest.mock import MagicMock, patch
from datetime import datetime
from datascout_core.core.monitor import TaskMonitor
from datascout_core.core.exceptions import MonitorError

@pytest.fixture
def base_config():
    """基礎配置"""
    return {
        'check_interval': 1,
        'max_retries': 3,
        'retry_interval': 1,
        'memory_limit': 90,
        'cpu_limit': 90,
        'disk_limit': 90,
        'log_interval': 1,
        'checkpoint_dir': 'test_checkpoints'
    }

@pytest.fixture
def monitor(base_config):
    """監控實例"""
    monitor = TaskMonitor(base_config)
    yield monitor
    monitor.stop()
    if os.path.exists('test_checkpoints'):
        for file in os.listdir('test_checkpoints'):
            os.remove(os.path.join('test_checkpoints', file))
        os.rmdir('test_checkpoints')

def test_init(monitor, base_config):
    """測試初始化"""
    assert monitor.config == base_config
    assert monitor.task_id is None
    assert monitor.status == 'stopped'
    assert monitor.progress == 0
    assert monitor.retry_count == 0
    assert monitor.error_count == 0

def test_start_stop(monitor):
    """測試開始和停止"""
    monitor.start('test_task')
    assert monitor.task_id == 'test_task'
    assert monitor.status == 'running'
    assert monitor.start_time is not None
    
    monitor.stop()
    assert monitor.status == 'stopped'

def test_start_already_running(monitor):
    """測試重複開始"""
    monitor.start('test_task')
    with pytest.raises(MonitorError, match='監控已在運行'):
        monitor.start('test_task2')

def test_signal_handling(monitor):
    """測試信號處理"""
    monitor.start('test_task')
    
    # 模擬SIGINT信號
    monitor._handle_signal(signal.SIGINT, None)
    assert monitor.status == 'stopped'
    
    monitor.start('test_task2')
    
    # 模擬SIGTERM信號
    monitor._handle_signal(signal.SIGTERM, None)
    assert monitor.status == 'stopped'

def test_progress_update(monitor):
    """測試進度更新"""
    monitor.start('test_task')
    
    monitor.update_progress(50)
    assert monitor.progress == 50
    
    monitor.update_progress(150)  # 超過100%
    assert monitor.progress == 100
    
    monitor.update_progress(-10)  # 小於0
    assert monitor.progress == 0

def test_error_handling(monitor):
    """測試錯誤處理"""
    monitor.start('test_task')
    
    monitor.add_error()
    assert monitor.error_count == 1
    
    # 設置最大錯誤次數為2
    monitor.config['max_errors'] = 2
    
    monitor.add_error()
    assert monitor.error_count == 2
    assert monitor.status == 'stopped'  # 應該自動停止

def test_retry_handling(monitor):
    """測試重試處理"""
    monitor.start('test_task')
    
    monitor.add_retry()
    assert monitor.retry_count == 1
    
    # 設置最大重試次數為2
    monitor.config['max_retries'] = 2
    
    monitor.restart()
    assert monitor.retry_count == 2
    
    monitor.restart()
    assert monitor.status == 'stopped'  # 應該自動停止

@patch('psutil.Process')
def test_resource_monitoring(mock_process, monitor):
    """測試資源監控"""
    # 模擬進程
    process_mock = MagicMock()
    mock_process.return_value = process_mock
    
    # 模擬內存使用超過限制
    process_mock.memory_percent.return_value = 95
    monitor.config['memory_action'] = 'stop'
    
    monitor.start('test_task')
    time.sleep(1.1)  # 等待檢查循環
    
    assert monitor.status == 'stopped'
    
    # 模擬CPU使用超過限制
    process_mock.cpu_percent.return_value = 95
    monitor.config['cpu_action'] = 'restart'
    
    monitor.start('test_task2')
    time.sleep(1.1)  # 等待檢查循環
    
    assert monitor.retry_count == 1

def test_checkpoint_management(monitor):
    """測試檢查點管理"""
    monitor.start('test_task')
    
    # 保存檢查點
    test_data = {'key': 'value'}
    monitor.save_checkpoint(test_data)
    
    assert os.path.exists('test_checkpoints/test_task.json')
    
    # 加載檢查點
    loaded_data = monitor.load_checkpoint()
    assert loaded_data == test_data
    
    # 清除檢查點
    monitor.clear_checkpoint()
    assert not os.path.exists('test_checkpoints/test_task.json')

def test_checkpoint_not_started(monitor):
    """測試未開始任務的檢查點操作"""
    with pytest.raises(MonitorError, match='任務未開始'):
        monitor.save_checkpoint({})
    
    with pytest.raises(MonitorError, match='任務未開始'):
        monitor.load_checkpoint()
    
    with pytest.raises(MonitorError, match='任務未開始'):
        monitor.clear_checkpoint()

def test_context_manager(monitor):
    """測試上下文管理器"""
    with monitor as m:
        m.start('test_task')
        assert m.status == 'running'
    
    assert monitor.status == 'stopped'

def test_get_status(monitor):
    """測試獲取狀態"""
    monitor.start('test_task')
    monitor.update_progress(50)
    monitor.add_error()
    monitor.add_retry()
    
    status = monitor.get_status()
    
    assert status['task_id'] == 'test_task'
    assert status['status'] == 'running'
    assert status['progress'] == 50
    assert status['retry_count'] == 1
    assert status['error_count'] == 1
    assert status['start_time'] is not None
    assert status['duration'] >= 0 