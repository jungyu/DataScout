# 使用指南

## 概述

本指南提供系統的使用說明，包括安裝、配置、運行和測試等步驟。

## 安裝

### 環境要求

- Python 3.8 或更高版本
- pip 包管理器

### 安裝步驟

1. 克隆項目到本地：

   ```bash
   git clone https://github.com/yourusername/yourproject.git
   cd yourproject
   ```

2. 安裝依賴：

   ```bash
   pip install -r requirements.txt
   ```

3. 運行安裝腳本：

   ```bash
   python scripts/setup.py
   ```

## 配置

### 配置文件

系統使用以下配置文件：

- `config/storage.json`: 存儲配置
- `config/logging.json`: 日誌配置
- `config/security.json`: 安全配置

### 配置示例

#### 存儲配置

```json
{
  "mode": "local",
  "local": {
    "path": "data",
    "backup_path": "backups"
  },
  "mongodb": {
    "uri": "",
    "database": "",
    "collection": ""
  },
  "notion": {
    "token": "",
    "database_id": "",
    "parent_page_id": ""
  }
}
```

#### 日誌配置

```json
{
  "level": "INFO",
  "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
  "file": "logs/app.log"
}
```

#### 安全配置

```json
{
  "encryption_key": "",
  "jwt_secret": "",
  "allowed_origins": []
}
```

## 運行

### 主程序

運行主程序：

```bash
python src/main.py
```

### 腳本

#### 安裝腳本

```bash
python scripts/setup.py
```

#### 測試腳本

```bash
python scripts/test.py
```

## 測試

### 運行測試

使用 `pytest` 運行測試：

```bash
pytest
```

### 生成測試報告

生成測試報告：

```bash
pytest --cov=src --cov-report=html
```

## 錯誤處理

系統使用 `ErrorHandler` 處理錯誤，並通過 `Logger` 記錄錯誤信息。錯誤狀態通過 `_update_status` 追蹤。

## 日誌記錄

系統使用 `Logger` 記錄日誌，日誌文件位於 `logs/app.log`。

## 備份和恢復

系統支持數據備份和恢復，使用 `StorageHandler` 的 `create_backup` 和 `restore_backup` 方法。