"""
報告模組測試

測試以下功能：
1. 報告基類功能
2. 各種格式報告的保存和加載
3. 報告分析功能
4. 報告工廠功能
"""

import os
import json
import csv
import pytest
import pandas as pd
from datetime import datetime
from unittest.mock import MagicMock, patch
from datascout_core.core.report import (
    Report, JsonReport, CsvReport, ExcelReport, HtmlReport,
    ReportAnalyzer, ReportFactory
)
from datascout_core.core.exceptions import ReportError

@pytest.fixture
def base_config():
    """基礎配置"""
    return {
        'output_dir': 'test_output',
        'file_prefix': 'test_report',
        'encoding': 'utf-8'
    }

@pytest.fixture
def sample_data():
    """示例數據"""
    return [
        {'id': 1, 'name': '項目1', 'value': 100, 'category': 'A'},
        {'id': 2, 'name': '項目2', 'value': 200, 'category': 'B'},
        {'id': 3, 'name': '項目3', 'value': 300, 'category': 'A'},
        {'id': 4, 'name': '項目4', 'value': 400, 'category': 'C'},
        {'id': 5, 'name': '項目5', 'value': 500, 'category': 'B'}
    ]

@pytest.fixture
def report(base_config):
    """報告實例"""
    report = Report(base_config)
    yield report
    # 清理測試文件
    if os.path.exists(base_config['output_dir']):
        for file in os.listdir(base_config['output_dir']):
            os.remove(os.path.join(base_config['output_dir'], file))
        os.rmdir(base_config['output_dir'])

@pytest.fixture
def json_report(base_config):
    """JSON報告實例"""
    report = JsonReport(base_config)
    yield report
    # 清理測試文件
    if os.path.exists(base_config['output_dir']):
        for file in os.listdir(base_config['output_dir']):
            os.remove(os.path.join(base_config['output_dir'], file))
        os.rmdir(base_config['output_dir'])

@pytest.fixture
def csv_report(base_config):
    """CSV報告實例"""
    report = CsvReport(base_config)
    yield report
    # 清理測試文件
    if os.path.exists(base_config['output_dir']):
        for file in os.listdir(base_config['output_dir']):
            os.remove(os.path.join(base_config['output_dir'], file))
        os.rmdir(base_config['output_dir'])

@pytest.fixture
def excel_report(base_config):
    """Excel報告實例"""
    report = ExcelReport(base_config)
    yield report
    # 清理測試文件
    if os.path.exists(base_config['output_dir']):
        for file in os.listdir(base_config['output_dir']):
            os.remove(os.path.join(base_config['output_dir'], file))
        os.rmdir(base_config['output_dir'])

@pytest.fixture
def html_report(base_config):
    """HTML報告實例"""
    report = HtmlReport(base_config)
    yield report
    # 清理測試文件
    if os.path.exists(base_config['output_dir']):
        for file in os.listdir(base_config['output_dir']):
            os.remove(os.path.join(base_config['output_dir'], file))
        os.rmdir(base_config['output_dir'])

def test_report_init(report, base_config):
    """測試報告初始化"""
    assert report.config == base_config
    assert report.data == []
    assert 'created_at' in report.metadata
    assert report.metadata['version'] == '1.0.0'

def test_report_add_data(report, sample_data):
    """測試添加數據"""
    for item in sample_data:
        report.add_data(item)
    
    assert len(report.data) == len(sample_data)
    assert report.data == sample_data

def test_report_add_metadata(report):
    """測試添加元數據"""
    report.add_metadata('author', '測試用戶')
    report.add_metadata('description', '測試報告')
    
    assert report.metadata['author'] == '測試用戶'
    assert report.metadata['description'] == '測試報告'

def test_report_get_data(report, sample_data):
    """測試獲取數據"""
    for item in sample_data:
        report.add_data(item)
    
    data = report.get_data()
    assert data == sample_data

def test_report_get_metadata(report):
    """測試獲取元數據"""
    report.add_metadata('author', '測試用戶')
    
    metadata = report.get_metadata()
    assert metadata['author'] == '測試用戶'
    assert 'created_at' in metadata
    assert metadata['version'] == '1.0.0'

def test_report_clear(report, sample_data):
    """測試清空數據"""
    for item in sample_data:
        report.add_data(item)
    
    report.add_metadata('author', '測試用戶')
    
    assert len(report.data) == len(sample_data)
    assert 'author' in report.metadata
    
    report.clear()
    
    assert report.data == []
    assert 'author' not in report.metadata
    assert 'created_at' in report.metadata
    assert report.metadata['version'] == '1.0.0'

def test_report_to_dict(report, sample_data):
    """測試轉換為字典"""
    for item in sample_data:
        report.add_data(item)
    
    report.add_metadata('author', '測試用戶')
    
    report_dict = report.to_dict()
    
    assert 'metadata' in report_dict
    assert 'data' in report_dict
    assert report_dict['metadata']['author'] == '測試用戶'
    assert report_dict['data'] == sample_data

def test_report_save_not_implemented(report):
    """測試保存未實現"""
    with pytest.raises(NotImplementedError):
        report.save('test.json')

def test_report_load_not_implemented(report):
    """測試加載未實現"""
    with pytest.raises(NotImplementedError):
        report.load('test.json')

def test_json_report_save_load(json_report, sample_data, base_config):
    """測試JSON報告保存和加載"""
    # 創建輸出目錄
    os.makedirs(base_config['output_dir'], exist_ok=True)
    
    # 添加數據和元數據
    for item in sample_data:
        json_report.add_data(item)
    
    json_report.add_metadata('author', '測試用戶')
    
    # 保存報告
    filepath = os.path.join(base_config['output_dir'], 'test.json')
    json_report.save(filepath)
    
    # 檢查文件是否存在
    assert os.path.exists(filepath)
    
    # 創建新報告並加載
    new_report = JsonReport(base_config)
    new_report.load(filepath)
    
    # 檢查數據和元數據
    assert new_report.data == sample_data
    assert new_report.metadata['author'] == '測試用戶'
    assert 'created_at' in new_report.metadata
    assert new_report.metadata['version'] == '1.0.0'

def test_csv_report_save_load(csv_report, sample_data, base_config):
    """測試CSV報告保存和加載"""
    # 創建輸出目錄
    os.makedirs(base_config['output_dir'], exist_ok=True)
    
    # 添加數據和元數據
    for item in sample_data:
        csv_report.add_data(item)
    
    csv_report.add_metadata('author', '測試用戶')
    
    # 保存報告
    filepath = os.path.join(base_config['output_dir'], 'test.csv')
    csv_report.save(filepath)
    
    # 檢查文件是否存在
    assert os.path.exists(filepath)
    assert os.path.exists(f"{os.path.splitext(filepath)[0]}_metadata.json")
    
    # 創建新報告並加載
    new_report = CsvReport(base_config)
    new_report.load(filepath)
    
    # 檢查數據和元數據
    assert len(new_report.data) == len(sample_data)
    assert all(key in new_report.data[0] for key in sample_data[0].keys())
    assert 'author' in new_report.metadata
    assert new_report.metadata['author'] == '測試用戶'

def test_excel_report_save_load(excel_report, sample_data, base_config):
    """測試Excel報告保存和加載"""
    # 創建輸出目錄
    os.makedirs(base_config['output_dir'], exist_ok=True)
    
    # 添加數據和元數據
    for item in sample_data:
        excel_report.add_data(item)
    
    excel_report.add_metadata('author', '測試用戶')
    
    # 保存報告
    filepath = os.path.join(base_config['output_dir'], 'test.xlsx')
    excel_report.save(filepath)
    
    # 檢查文件是否存在
    assert os.path.exists(filepath)
    
    # 創建新報告並加載
    new_report = ExcelReport(base_config)
    new_report.load(filepath)
    
    # 檢查數據和元數據
    assert len(new_report.data) == len(sample_data)
    assert all(key in new_report.data[0] for key in sample_data[0].keys())
    assert 'author' in new_report.metadata
    assert new_report.metadata['author'] == '測試用戶'

def test_html_report_save(html_report, sample_data, base_config):
    """測試HTML報告保存"""
    # 創建輸出目錄
    os.makedirs(base_config['output_dir'], exist_ok=True)
    
    # 添加數據和元數據
    for item in sample_data:
        html_report.add_data(item)
    
    html_report.add_metadata('author', '測試用戶')
    
    # 保存報告
    filepath = os.path.join(base_config['output_dir'], 'test.html')
    html_report.save(filepath)
    
    # 檢查文件是否存在
    assert os.path.exists(filepath)
    
    # 檢查HTML內容
    with open(filepath, 'r', encoding='utf-8') as f:
        html_content = f.read()
        assert '<!DOCTYPE html>' in html_content
        assert '<title>任務報告</title>' in html_content
        assert '項目1' in html_content
        assert '項目2' in html_content
        assert 'author' in html_content
        assert '測試用戶' in html_content

def test_html_report_load_not_supported(html_report):
    """測試HTML報告加載不支持"""
    with pytest.raises(ReportError, match='HTML報告不支持加載'):
        html_report.load('test.html')

def test_report_empty_data_error(json_report, base_config):
    """測試空數據錯誤"""
    # 創建輸出目錄
    os.makedirs(base_config['output_dir'], exist_ok=True)
    
    # 嘗試保存空報告
    filepath = os.path.join(base_config['output_dir'], 'empty.json')
    with pytest.raises(ReportError, match='沒有數據可保存'):
        json_report.save(filepath)

def test_report_analyzer_init(report, sample_data):
    """測試報告分析器初始化"""
    for item in sample_data:
        report.add_data(item)
    
    analyzer = ReportAnalyzer(report)
    
    assert len(analyzer.data) == len(sample_data)
    assert all(key in analyzer.data.columns for key in sample_data[0].keys())

def test_report_analyzer_get_summary(report, sample_data):
    """測試報告分析器獲取摘要"""
    for item in sample_data:
        report.add_data(item)
    
    analyzer = ReportAnalyzer(report)
    summary = analyzer.get_summary()
    
    assert summary['total_records'] == len(sample_data)
    assert 'id' in summary['columns']
    assert 'name' in summary['columns']
    assert 'value' in summary['columns']
    assert 'category' in summary['columns']
    assert 'value' in summary['numeric_columns']
    assert 'category' in summary['categorical_columns']
    assert 'value_stats' in summary
    assert 'category_stats' in summary
    assert summary['value_stats']['mean'] == 300.0
    assert summary['category_stats']['unique_values'] == 3

def test_report_analyzer_filter_data(report, sample_data):
    """測試報告分析器過濾數據"""
    for item in sample_data:
        report.add_data(item)
    
    analyzer = ReportAnalyzer(report)
    
    # 過濾category為A的數據
    filtered_data = analyzer.filter_data({'category': 'A'})
    assert len(filtered_data) == 2
    assert all(item['category'] == 'A' for _, item in filtered_data.iterrows())
    
    # 過濾value大於300的數據
    filtered_data = analyzer.filter_data({'value': 300})
    assert len(filtered_data) == 2
    assert all(item['value'] > 300 for _, item in filtered_data.iterrows())
    
    # 過濾不存在的列
    filtered_data = analyzer.filter_data({'nonexistent': 'value'})
    assert len(filtered_data) == len(sample_data)

def test_report_analyzer_group_by(report, sample_data):
    """測試報告分析器分組統計"""
    for item in sample_data:
        report.add_data(item)
    
    analyzer = ReportAnalyzer(report)
    
    # 按category分組，計算value的平均值
    grouped_data = analyzer.group_by(['category'], {'value': ['mean']})
    assert len(grouped_data) == 3
    assert grouped_data.loc['A', ('value', 'mean')] == 200.0
    assert grouped_data.loc['B', ('value', 'mean')] == 350.0
    assert grouped_data.loc['C', ('value', 'mean')] == 400.0

def test_report_analyzer_sort_by(report, sample_data):
    """測試報告分析器排序"""
    for item in sample_data:
        report.add_data(item)
    
    analyzer = ReportAnalyzer(report)
    
    # 按value升序排序
    sorted_data = analyzer.sort_by(['value'])
    assert sorted_data.iloc[0]['value'] == 100
    assert sorted_data.iloc[-1]['value'] == 500
    
    # 按category升序，value降序排序
    sorted_data = analyzer.sort_by(['category', 'value'], [True, False])
    assert sorted_data.iloc[0]['category'] == 'A'
    assert sorted_data.iloc[0]['value'] == 300
    assert sorted_data.iloc[1]['value'] == 100

def test_report_factory_create_report(base_config):
    """測試報告工廠創建報告"""
    # 創建JSON報告
    json_report = ReportFactory.create_report('json', base_config)
    assert isinstance(json_report, JsonReport)
    
    # 創建CSV報告
    csv_report = ReportFactory.create_report('csv', base_config)
    assert isinstance(csv_report, CsvReport)
    
    # 創建Excel報告
    excel_report = ReportFactory.create_report('excel', base_config)
    assert isinstance(excel_report, ExcelReport)
    
    # 創建HTML報告
    html_report = ReportFactory.create_report('html', base_config)
    assert isinstance(html_report, HtmlReport)
    
    # 創建不支持的報告類型
    with pytest.raises(ReportError, match='不支持的報告類型'):
        ReportFactory.create_report('unsupported', base_config) 