"""
調度器測試模組

測試以下功能：
1. 任務管理
2. 任務執行
3. 任務依賴
4. 任務重試
5. 報告生成
"""

import os
import json
import time
import pytest
import tempfile
from datetime import datetime
from unittest.mock import MagicMock, patch
from datascout_core.core.scheduler import Scheduler, Task
from datascout_core.core.exceptions import SchedulerError

@pytest.fixture
def base_config():
    """基礎配置"""
    return {
        'max_workers': 2,
        'task_queue_size': 10,
        'max_retries': 2,
        'retry_interval': 0.1,
        'checkpoint_dir': 'test_checkpoints',
        'report_dir': 'test_reports',
        'report_type': 'json',
        'report_config': {
            'indent': 2
        }
    }

@pytest.fixture
def scheduler(base_config):
    """調度器實例"""
    scheduler = Scheduler(base_config)
    yield scheduler
    scheduler.stop()
    if os.path.exists(base_config['checkpoint_dir']):
        for file in os.listdir(base_config['checkpoint_dir']):
            os.remove(os.path.join(base_config['checkpoint_dir'], file))
        os.rmdir(base_config['checkpoint_dir'])
    if os.path.exists(base_config['report_dir']):
        for file in os.listdir(base_config['report_dir']):
            os.remove(os.path.join(base_config['report_dir'], file))
        os.rmdir(base_config['report_dir'])

@pytest.fixture
def mock_task_func():
    """模擬任務函數"""
    def func(*args, **kwargs):
        if kwargs.get('fail', False):
            raise Exception('任務失敗')
        return {'result': 'success', 'args': args, 'kwargs': kwargs}
    return func

def test_task_init():
    """測試任務初始化"""
    task = Task('test_task', lambda x: x)
    assert task.name == 'test_task'
    assert task.status == 'pending'
    assert task.priority == 0
    assert task.dependencies == []
    assert task.retry_count == 0
    assert task.start_time is None
    assert task.end_time is None
    assert task.result is None
    assert task.error is None

def test_task_to_dict():
    """測試任務轉換為字典"""
    task = Task('test_task', lambda x: x)
    task_dict = task.to_dict()
    assert task_dict['name'] == 'test_task'
    assert task_dict['status'] == 'pending'
    assert task_dict['priority'] == 0
    assert task_dict['dependencies'] == []
    assert task_dict['retry_count'] == 0
    assert task_dict['start_time'] is None
    assert task_dict['end_time'] is None
    assert task_dict['error'] is None

def test_scheduler_init(base_config):
    """測試調度器初始化"""
    scheduler = Scheduler(base_config)
    assert scheduler.config == base_config
    assert scheduler.task_queue.maxsize == base_config['task_queue_size']
    assert len(scheduler.tasks) == 0
    assert len(scheduler.workers) == 0
    assert not scheduler.running
    assert os.path.exists(base_config['checkpoint_dir'])
    assert os.path.exists(base_config['report_dir'])

def test_scheduler_start_stop(scheduler):
    """測試調度器啟動和停止"""
    scheduler.start()
    assert scheduler.running
    assert len(scheduler.workers) == scheduler.config['max_workers']
    
    scheduler.stop()
    assert not scheduler.running
    assert len(scheduler.workers) == 0

def test_scheduler_start_already_running(scheduler):
    """測試重複啟動調度器"""
    scheduler.start()
    with pytest.raises(SchedulerError):
        scheduler.start()

def test_scheduler_add_task(scheduler, mock_task_func):
    """測試添加任務"""
    task = Task('test_task', mock_task_func)
    scheduler.add_task(task)
    assert task.id in scheduler.tasks
    assert scheduler.tasks[task.id] == task

def test_scheduler_add_duplicate_task(scheduler, mock_task_func):
    """測試添加重複任務"""
    task = Task('test_task', mock_task_func)
    scheduler.add_task(task)
    with pytest.raises(SchedulerError):
        scheduler.add_task(task)

def test_scheduler_remove_task(scheduler, mock_task_func):
    """測試移除任務"""
    task = Task('test_task', mock_task_func)
    scheduler.add_task(task)
    scheduler.remove_task(task.id)
    assert task.id not in scheduler.tasks

def test_scheduler_remove_nonexistent_task(scheduler):
    """測試移除不存在的任務"""
    with pytest.raises(SchedulerError):
        scheduler.remove_task('nonexistent')

def test_scheduler_remove_running_task(scheduler, mock_task_func):
    """測試移除運行中的任務"""
    task = Task('test_task', mock_task_func)
    scheduler.add_task(task)
    task.status = 'running'
    with pytest.raises(SchedulerError):
        scheduler.remove_task(task.id)

def test_scheduler_get_task(scheduler, mock_task_func):
    """測試獲取任務"""
    task = Task('test_task', mock_task_func)
    scheduler.add_task(task)
    assert scheduler.get_task(task.id) == task
    assert scheduler.get_task('nonexistent') is None

def test_scheduler_get_tasks(scheduler, mock_task_func):
    """測試獲取任務列表"""
    task1 = Task('task1', mock_task_func)
    task2 = Task('task2', mock_task_func)
    task3 = Task('task3', mock_task_func)
    
    scheduler.add_task(task1)
    scheduler.add_task(task2)
    scheduler.add_task(task3)
    
    task2.status = 'running'
    task3.status = 'completed'
    
    all_tasks = scheduler.get_tasks()
    assert len(all_tasks) == 3
    
    running_tasks = scheduler.get_tasks('running')
    assert len(running_tasks) == 1
    assert running_tasks[0] == task2
    
    completed_tasks = scheduler.get_tasks('completed')
    assert len(completed_tasks) == 1
    assert completed_tasks[0] == task3

def test_scheduler_execute_task(scheduler, mock_task_func):
    """測試執行任務"""
    task = Task('test_task', mock_task_func, args=(1,), kwargs={'key': 'value'})
    scheduler.add_task(task)
    
    scheduler.start()
    time.sleep(0.1)  # 等待任務執行
    scheduler.stop()
    
    assert task.status == 'completed'
    assert task.result['result'] == 'success'
    assert task.result['args'] == (1,)
    assert task.result['kwargs'] == {'key': 'value'}
    assert task.start_time is not None
    assert task.end_time is not None
    assert task.error is None

def test_scheduler_execute_failing_task(scheduler, mock_task_func):
    """測試執行失敗的任務"""
    task = Task('test_task', mock_task_func, kwargs={'fail': True})
    scheduler.add_task(task)
    
    scheduler.start()
    time.sleep(0.1)  # 等待任務執行
    scheduler.stop()
    
    assert task.status == 'failed'
    assert task.error is not None
    assert task.retry_count > 0

def test_scheduler_task_dependencies(scheduler, mock_task_func):
    """測試任務依賴"""
    task1 = Task('task1', mock_task_func)
    task2 = Task('task2', mock_task_func, dependencies=[task1.id])
    
    scheduler.add_task(task1)
    scheduler.add_task(task2)
    
    scheduler.start()
    time.sleep(0.1)  # 等待任務執行
    scheduler.stop()
    
    assert task1.status == 'completed'
    assert task2.status == 'completed'
    assert task1.start_time < task2.start_time

def test_scheduler_task_retry(scheduler, mock_task_func):
    """測試任務重試"""
    fail_count = 0
    def failing_func():
        nonlocal fail_count
        fail_count += 1
        if fail_count <= 2:
            raise Exception('任務失敗')
        return 'success'
    
    task = Task('test_task', failing_func)
    scheduler.add_task(task)
    
    scheduler.start()
    time.sleep(0.5)  # 等待任務執行和重試
    scheduler.stop()
    
    assert task.status == 'completed'
    assert task.retry_count == 2
    assert task.result == 'success'

def test_scheduler_checkpoint_management(scheduler, mock_task_func):
    """測試檢查點管理"""
    task = Task('test_task', mock_task_func)
    scheduler.add_task(task)
    
    # 執行任務
    scheduler.start()
    time.sleep(0.1)
    scheduler.stop()
    
    # 保存檢查點
    scheduler.save_checkpoints()
    assert os.path.exists(os.path.join(scheduler.checkpoint_dir, f'{task.id}.json'))
    
    # 清除檢查點
    scheduler.clear_checkpoints()
    assert not os.path.exists(os.path.join(scheduler.checkpoint_dir, f'{task.id}.json'))

def test_scheduler_report_generation(scheduler, mock_task_func):
    """測試報告生成"""
    task = Task('test_task', mock_task_func)
    scheduler.add_task(task)
    
    # 執行任務
    scheduler.start()
    time.sleep(0.1)
    scheduler.stop()
    
    # 檢查任務報告
    report_files = [f for f in os.listdir(scheduler.report_dir) if f.startswith(task.id)]
    assert len(report_files) > 0
    
    # 檢查摘要報告
    summary_file = scheduler.generate_summary_report()
    assert summary_file is not None
    assert os.path.exists(summary_file)
    
    with open(summary_file, 'r') as f:
        report_data = json.load(f)
        assert 'metadata' in report_data
        assert 'data' in report_data
        assert report_data['metadata']['total_tasks'] == 1
        assert report_data['metadata']['completed_tasks'] == 1

def test_scheduler_context_manager(base_config):
    """測試上下文管理器"""
    with Scheduler(base_config) as scheduler:
        assert scheduler.running
        assert len(scheduler.workers) == base_config['max_workers']
    
    assert not scheduler.running
    assert len(scheduler.workers) == 0

def test_scheduler_signal_handling(scheduler):
    """測試信號處理"""
    scheduler.start()
    assert scheduler.running
    
    # 模擬 SIGINT 信號
    scheduler._handle_signal(signal.SIGINT, None)
    assert not scheduler.running
    assert len(scheduler.workers) == 0 