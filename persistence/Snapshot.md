# Persistence Module Snapshot

## 架構總覽

Persistence 模組採用高度模組化設計，分為核心組件（core）與多種存儲處理器（handlers），支援多種數據存儲後端，並提供統一的數據存取與管理接口。

## 目錄結構

```
persistence/
├── core/
│   ├── base.py
│   ├── config.py
│   ├── exceptions.py
│   ├── storage_interface.py
│   └── storage_factory.py
└── handlers/
    ├── local_handler.py
    ├── mongodb_handler.py
    ├── mysql_handler.py
    ├── postgresql_handler.py
    ├── redis_handler.py
    ├── elasticsearch_handler.py
    ├── clickhouse_handler.py
    ├── rabbitmq_handler.py
    ├── kafka_handler.py
    ├── sqlserver_handler.py
    ├── supabase_handler.py
    └── notion_handler.py
```

## 核心組件

- `base.py`：基礎存儲處理器類
- `config.py`：配置管理
- `exceptions.py`：異常處理
- `storage_interface.py`：存儲接口定義
- `storage_factory.py`：存儲處理器工廠

## 存儲處理器

- 本地文件：`local_handler.py`
- 關聯式資料庫：`mysql_handler.py`, `postgresql_handler.py`, `sqlserver_handler.py`
- NoSQL：`mongodb_handler.py`, `redis_handler.py`
- 分析型資料庫：`clickhouse_handler.py`
- 搜尋引擎：`elasticsearch_handler.py`
- 訊息佇列：`rabbitmq_handler.py`, `kafka_handler.py`
- 雲端服務：`supabase_handler.py`, `notion_handler.py`

## 設計特點

- 高度模組化與可擴展性
- 統一接口設計，易於切換存儲後端
- 完善的錯誤處理與日誌記錄
- 支援自定義擴展

## 主要類別與異常

- `StorageHandler`, `StorageConfig`
- `LocalStorageHandler`, `MongoDBHandler`, `NotionHandler` 等
- `PersistenceError`, `StorageError`, `ValidationError`, `ConfigError`

## 使用建議

- 使用 `StorageConfig` 統一管理配置
- 透過工廠模式或直接實例化 handler 切換存儲後端
- 善用異常類別進行錯誤處理
- 定期備份與監控存儲狀態

## 適用場景

- 多來源數據整合
- 跨平台數據同步
- 需支援多種存儲後端的應用

---

本文件可作為 Persistence 模組的架構快照與新手入門參考。 