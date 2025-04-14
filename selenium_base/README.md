# DataScout Core

DataScout Core 是一個用於網路爬蟲任務管理的核心模組，提供任務調度、監控、報告和配置管理等功能。

## 功能特點

1. 任務管理
   - 任務創建和配置
   - 任務調度和執行
   - 任務依賴管理
   - 任務重試機制

2. 資源監控
   - CPU 使用率監控
   - 內存使用率監控
   - 磁盤使用率監控
   - 進程監控

3. 報告生成
   - 多格式報告支持（JSON、CSV、Excel、HTML）
   - 報告分析和統計
   - 報告導出功能

4. 配置管理
   - 配置驗證
   - 配置版本控制
   - 配置模板管理
   - 配置導入導出

## 專案結構

```
datascout_core/
├── __init__.py
├── core/
│   ├── __init__.py
│   ├── scheduler.py      # 任務調度器
│   ├── monitor.py        # 資源監控
│   ├── report.py         # 報告生成
│   ├── config.py         # 配置管理
│   └── schemas/          # 配置schema
│       └── config_schema.json
├── utils/
│   ├── __init__.py
│   ├── logger.py         # 日誌工具
│   └── helpers.py        # 輔助函數
└── tests/
    ├── __init__.py
    ├── test_scheduler.py
    ├── test_monitor.py
    ├── test_report.py
    └── test_config.py
```

## 安裝方式

```bash
pip install datascout-core
```

## 使用方式

1. 基本使用
```python
from selenium_base import Scheduler, Task

# 創建任務
task = Task(
    task_id="task1",
    name="示例任務",
    function="example_function",
    parameters={"param1": "value1"}
)

# 創建調度器
scheduler = Scheduler()

# 添加任務
scheduler.add_task(task)

# 啟動調度器
scheduler.start()
```

2. 配置管理
```python
from selenium_base import ConfigManager

# 創建配置管理器
config_manager = ConfigManager()

# 加載配置
config = config_manager.load_config("task_config")

# 保存配置
config_manager.save_config("task_config", config)
```

3. 報告生成
```python
from selenium_base import ReportFactory

# 創建報告
report = ReportFactory.create_report("json")

# 添加數據
report.add_data("key", "value")

# 保存報告
report.save("report.json")
```

## 配置說明

配置文件使用 JSON 格式，主要包含以下部分：

1. 任務配置
   - 任務ID和名稱
   - 執行函數和參數
   - 優先級和依賴關係
   - 重試策略

2. 資源限制
   - CPU 使用限制
   - 內存使用限制
   - 磁盤使用限制

3. 報告設置
   - 報告格式
   - 保存路徑
   - 包含內容

4. 日誌設置
   - 日誌級別
   - 日誌格式
   - 文件設置

## 開發指南

1. 環境設置
```bash
# 克隆專案
git clone https://github.com/yourusername/datascout-core.git

# 安裝依賴
pip install -r requirements.txt

# 安裝開發依賴
pip install -r requirements-dev.txt
```

2. 運行測試
```bash
pytest tests/
```

3. 代碼風格
- 遵循 PEP 8 規範
- 使用 Type Hints
- 編寫完整的文檔字符串

## 貢獻指南

1. Fork 專案
2. 創建功能分支
3. 提交更改
4. 發起 Pull Request

## 授權協議

MIT License 