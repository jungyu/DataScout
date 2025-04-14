"""
儀表板測試模組

測試以下功能：
1. 任務狀態監控
2. 資源使用監控
3. 性能分析
4. 數據更新
5. 歷史記錄
"""

import os
import json
import time
import pytest
import tempfile
from datetime import datetime
from unittest.mock import MagicMock, patch
from datascout_core.core.dashboard import Dashboard
from datascout_core.core.exceptions import DashboardError

@pytest.fixture
def base_config():
    """基礎配置"""
    return {
        'data_queue_size': 100,
        'update_interval': 0.1,
        'max_history_size': 10,
        'output_dir': 'test_dashboard'
    }

@pytest.fixture
def dashboard(base_config):
    """儀表板實例"""
    dashboard = Dashboard(base_config)
    yield dashboard
    dashboard.stop()
    if os.path.exists(base_config['output_dir']):
        for file in os.listdir(base_config['output_dir']):
            os.remove(os.path.join(base_config['output_dir'], file))
        os.rmdir(base_config['output_dir'])

def test_dashboard_init(base_config):
    """測試儀表板初始化"""
    dashboard = Dashboard(base_config)
    assert dashboard.config == base_config
    assert dashboard.data_queue.maxsize == base_config['data_queue_size']
    assert dashboard.update_interval == base_config['update_interval']
    assert dashboard.max_history_size == base_config['max_history_size']
    assert dashboard.output_dir == base_config['output_dir']
    assert not dashboard.running
    assert dashboard.data['tasks'] == {}
    assert dashboard.data['resources'] == {}
    assert dashboard.data['performance'] == {}
    assert dashboard.history['tasks'] == []
    assert dashboard.history['resources'] == []
    assert dashboard.history['performance'] == []
    assert os.path.exists(base_config['output_dir'])

def test_dashboard_start_stop(dashboard):
    """測試儀表板啟動和停止"""
    dashboard.start()
    assert dashboard.running
    assert dashboard.update_thread.is_alive()
    
    dashboard.stop()
    assert not dashboard.running
    assert not dashboard.update_thread.is_alive()

def test_dashboard_start_already_running(dashboard):
    """測試重複啟動儀表板"""
    dashboard.start()
    with pytest.raises(DashboardError):
        dashboard.start()

def test_dashboard_update_task_status(dashboard):
    """測試更新任務狀態"""
    task_id = 'test_task'
    status = {
        'name': 'test_task',
        'status': 'running',
        'progress': 50,
        'start_time': datetime.now().isoformat()
    }
    
    dashboard.update_task_status(task_id, status)
    time.sleep(0.2)  # 等待更新循環處理數據
    
    assert task_id in dashboard.data['tasks']
    assert dashboard.data['tasks'][task_id] == status
    assert len(dashboard.history['tasks']) == 1
    assert task_id in dashboard.history['tasks'][0]

def test_dashboard_update_resource_usage(dashboard):
    """測試更新資源使用情況"""
    resource_data = {
        'cpu_percent': 50.0,
        'memory_percent': 60.0,
        'disk_percent': 70.0,
        'timestamp': datetime.now().isoformat()
    }
    
    dashboard.update_resource_usage(resource_data)
    time.sleep(0.2)  # 等待更新循環處理數據
    
    assert dashboard.data['resources'] == resource_data
    assert len(dashboard.history['resources']) == 1
    assert dashboard.history['resources'][0] == resource_data

def test_dashboard_update_performance_metrics(dashboard):
    """測試更新性能指標"""
    metrics = {
        'task_completion_rate': 0.8,
        'average_task_duration': 10.5,
        'error_rate': 0.05,
        'timestamp': datetime.now().isoformat()
    }
    
    dashboard.update_performance_metrics(metrics)
    time.sleep(0.2)  # 等待更新循環處理數據
    
    assert dashboard.data['performance'] == metrics
    assert len(dashboard.history['performance']) == 1
    assert dashboard.history['performance'][0] == metrics

def test_dashboard_system_resources(dashboard):
    """測試系統資源更新"""
    dashboard.start()
    time.sleep(0.2)  # 等待更新循環處理數據
    
    assert 'cpu_percent' in dashboard.data['resources']
    assert 'memory_percent' in dashboard.data['resources']
    assert 'disk_percent' in dashboard.data['resources']
    assert 'timestamp' in dashboard.data['resources']
    
    assert len(dashboard.history['resources']) > 0
    assert 'cpu_percent' in dashboard.history['resources'][0]
    assert 'memory_percent' in dashboard.history['resources'][0]
    assert 'disk_percent' in dashboard.history['resources'][0]
    assert 'timestamp' in dashboard.history['resources'][0]
    
    dashboard.stop()

def test_dashboard_history_limit(dashboard):
    """測試歷史記錄限制"""
    # 添加超過限制的數據
    for i in range(15):
        dashboard.update_task_status(f'task_{i}', {'status': 'completed'})
        dashboard.update_resource_usage({'cpu_percent': i})
        dashboard.update_performance_metrics({'completion_rate': i/10})
    
    time.sleep(0.2)  # 等待更新循環處理數據
    
    assert len(dashboard.history['tasks']) <= dashboard.max_history_size
    assert len(dashboard.history['resources']) <= dashboard.max_history_size
    assert len(dashboard.history['performance']) <= dashboard.max_history_size

def test_dashboard_data_persistence(dashboard):
    """測試數據持久化"""
    # 添加測試數據
    task_id = 'test_task'
    status = {'status': 'running'}
    resource_data = {'cpu_percent': 50.0}
    metrics = {'completion_rate': 0.8}
    
    dashboard.update_task_status(task_id, status)
    dashboard.update_resource_usage(resource_data)
    dashboard.update_performance_metrics(metrics)
    
    time.sleep(0.2)  # 等待更新循環處理數據
    
    # 檢查文件是否創建
    current_data_file = os.path.join(dashboard.output_dir, 'current_data.json')
    history_data_file = os.path.join(dashboard.output_dir, 'history_data.json')
    
    assert os.path.exists(current_data_file)
    assert os.path.exists(history_data_file)
    
    # 檢查文件內容
    with open(current_data_file, 'r') as f:
        current_data = json.load(f)
        assert task_id in current_data['tasks']
        assert current_data['resources'] == resource_data
        assert current_data['performance'] == metrics
    
    with open(history_data_file, 'r') as f:
        history_data = json.load(f)
        assert len(history_data['tasks']) > 0
        assert len(history_data['resources']) > 0
        assert len(history_data['performance']) > 0

def test_dashboard_get_task_status(dashboard):
    """測試獲取任務狀態"""
    task_id = 'test_task'
    status = {'status': 'running'}
    
    dashboard.update_task_status(task_id, status)
    time.sleep(0.2)  # 等待更新循環處理數據
    
    assert dashboard.get_task_status(task_id) == status
    assert dashboard.get_task_status('nonexistent') is None

def test_dashboard_get_all_tasks_status(dashboard):
    """測試獲取所有任務狀態"""
    task1_id = 'task1'
    task2_id = 'task2'
    status1 = {'status': 'running'}
    status2 = {'status': 'completed'}
    
    dashboard.update_task_status(task1_id, status1)
    dashboard.update_task_status(task2_id, status2)
    time.sleep(0.2)  # 等待更新循環處理數據
    
    all_tasks = dashboard.get_all_tasks_status()
    assert task1_id in all_tasks
    assert task2_id in all_tasks
    assert all_tasks[task1_id] == status1
    assert all_tasks[task2_id] == status2

def test_dashboard_get_resource_usage(dashboard):
    """測試獲取資源使用情況"""
    resource_data = {'cpu_percent': 50.0}
    dashboard.update_resource_usage(resource_data)
    time.sleep(0.2)  # 等待更新循環處理數據
    
    assert dashboard.get_resource_usage() == resource_data

def test_dashboard_get_performance_metrics(dashboard):
    """測試獲取性能指標"""
    metrics = {'completion_rate': 0.8}
    dashboard.update_performance_metrics(metrics)
    time.sleep(0.2)  # 等待更新循環處理數據
    
    assert dashboard.get_performance_metrics() == metrics

def test_dashboard_get_task_history(dashboard):
    """測試獲取任務歷史記錄"""
    task_id = 'test_task'
    status1 = {'status': 'running'}
    status2 = {'status': 'completed'}
    
    dashboard.update_task_status(task_id, status1)
    time.sleep(0.1)
    dashboard.update_task_status(task_id, status2)
    time.sleep(0.2)  # 等待更新循環處理數據
    
    history = dashboard.get_task_history(task_id)
    assert len(history) == 2
    assert task_id in history[0]
    assert task_id in history[1]
    assert history[0][task_id] == status1
    assert history[1][task_id] == status2

def test_dashboard_get_resource_history(dashboard):
    """測試獲取資源使用歷史記錄"""
    resource_data1 = {'cpu_percent': 50.0}
    resource_data2 = {'cpu_percent': 60.0}
    
    dashboard.update_resource_usage(resource_data1)
    time.sleep(0.1)
    dashboard.update_resource_usage(resource_data2)
    time.sleep(0.2)  # 等待更新循環處理數據
    
    history = dashboard.get_resource_history()
    assert len(history) == 2
    assert history[0] == resource_data1
    assert history[1] == resource_data2

def test_dashboard_get_performance_history(dashboard):
    """測試獲取性能指標歷史記錄"""
    metrics1 = {'completion_rate': 0.8}
    metrics2 = {'completion_rate': 0.9}
    
    dashboard.update_performance_metrics(metrics1)
    time.sleep(0.1)
    dashboard.update_performance_metrics(metrics2)
    time.sleep(0.2)  # 等待更新循環處理數據
    
    history = dashboard.get_performance_history()
    assert len(history) == 2
    assert history[0] == metrics1
    assert history[1] == metrics2

def test_dashboard_clear_history(dashboard):
    """測試清除歷史記錄"""
    # 添加測試數據
    dashboard.update_task_status('task1', {'status': 'running'})
    dashboard.update_resource_usage({'cpu_percent': 50.0})
    dashboard.update_performance_metrics({'completion_rate': 0.8})
    time.sleep(0.2)  # 等待更新循環處理數據
    
    # 清除歷史記錄
    dashboard.clear_history()
    
    assert dashboard.history['tasks'] == []
    assert dashboard.history['resources'] == []
    assert dashboard.history['performance'] == []

def test_dashboard_context_manager(base_config):
    """測試上下文管理器"""
    with Dashboard(base_config) as dashboard:
        assert dashboard.running
        assert dashboard.update_thread.is_alive()
    
    assert not dashboard.running
    assert not dashboard.update_thread.is_alive()

def test_dashboard_queue_full(dashboard):
    """測試隊列滿時的行為"""
    # 設置較小的隊列大小
    dashboard.data_queue = queue.Queue(maxsize=1)
    
    # 添加兩個數據，第二個應該被丟棄
    dashboard.update_task_status('task1', {'status': 'running'})
    dashboard.update_task_status('task2', {'status': 'running'})
    
    time.sleep(0.2)  # 等待更新循環處理數據
    
    assert len(dashboard.data['tasks']) == 1
    assert 'task1' in dashboard.data['tasks']
    assert 'task2' not in dashboard.data['tasks'] 