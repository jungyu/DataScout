# Telegram Bot 快照文檔

## 目錄結構

```
telegram_bot/
├── README.md           # 專案說明文檔
├── requirements.txt    # 依賴套件列表
├── config.py          # 配置管理
├── exceptions.py      # 自定義異常
├── bot.py            # Bot 核心類別
├── __init__.py       # 套件初始化
├── commands/         # 命令處理器
├── data/            # 數據存儲
├── docs/            # 文檔
├── examples/        # 示例代碼
├── handlers/        # 處理器
│   └── base_handler.py  # 基礎處理器
├── middlewares/     # 中間件
└── utils/          # 工具函數
```

## 核心組件

### 1. 基礎層

#### 1.1 BaseTelegramHandler (`handlers/base_handler.py`)
- 職責：提供核心 Bot 功能
- 主要功能：
  - Bot 初始化和配置
  - 生命週期管理
  - 錯誤處理
  - 日誌記錄
- 關鍵方法：
  ```python
  async def initialize(self) -> None
  async def start(self) -> None
  async def stop(self) -> None
  def get_application(self) -> Application
  ```

#### 1.2 異常處理 (`exceptions.py`)
- 異常類層次：
  ```python
  BotError
  ├── BotInitializationError
  ├── BotConfigError
  ├── BotRuntimeError
  ├── HandlerError
  └── MiddlewareError
  ```

### 2. 業務層

#### 2.1 DataScoutBot (`bot.py`)
- 職責：實現特定業務邏輯
- 繼承關係：`DataScoutBot(BaseTelegramHandler)`
- 主要功能：
  - 命令註冊
  - 消息處理
  - 回調處理
  - 圖片處理
- 關鍵方法：
  ```python
  def _setup_bot(self)
  @classmethod
  def run(cls, config: Optional[Dict[str, Any]] = None)
  ```

#### 2.2 配置管理 (`config.py`)
- 環境變量：
  - `DATASCOUT_BOT_TOKEN`
  - `ADMIN_USER_IDS`
  - `AUTHORIZED_USERS`
  - `REQUIRE_AUTH`
  - `GEMINI_API_KEY`
- 配置選項：
  ```python
  {
      "token": str,
      "proxy_url": str,
      "connect_timeout": int,
      "read_timeout": int,
      "write_timeout": int
  }
  ```

### 3. 服務層

#### 3.1 TelegramService (`autoflow/services/telegram.py`)
- 職責：提供高級服務接口
- 主要功能：
  - 服務初始化
  - 消息發送
  - 狀態管理
  - AutoFlow 整合
- 關鍵方法：
  ```python
  async def initialize(self)
  async def start(self)
  async def stop(self)
  async def send_message(self, chat_id: int, text: str)
  def get_bot(self) -> DataScoutBot
  ```

## 使用模式

### 1. 獨立運行
```python
from telegram_bot.bot import DataScoutBot

bot = DataScoutBot(config={
    "token": "your_token",
    "proxy_url": "http://proxy.example.com:8080"
})
await bot.start()
```

### 2. 服務組件
```python
from autoflow.services.telegram import TelegramService

service = TelegramService(config={
    "token": "your_token",
    "proxy_url": "http://proxy.example.com:8080"
})
await service.start()
```

### 3. 流程組件
```python
from autoflow.flows.telegram_flow import TelegramFlow

flow = TelegramFlow(config={
    "token": "your_token",
    "proxy_url": "http://proxy.example.com:8080"
})
await flow.start()
```

## 依賴關係

### 主要依賴
```
python-telegram-bot>=20.0
python-dotenv>=0.19.0
```

### 可選依賴
```
google-generativeai>=0.3.0  # 用於圖像分析
```

## 錯誤處理流程

1. 初始化錯誤：
   ```python
   try:
       await bot.initialize()
   except BotInitializationError as e:
       logger.error(f"初始化失敗: {e}")
   ```

2. 運行時錯誤：
   ```python
   try:
       await bot.start()
   except BotRuntimeError as e:
       logger.error(f"運行錯誤: {e}")
   ```

3. 消息處理錯誤：
   ```python
   try:
       await service.send_message(chat_id, text)
   except BotError as e:
       logger.error(f"消息發送失敗: {e}")
   ```

## 日誌記錄

### 日誌格式
```
%(asctime)s - %(name)s - %(levelname)s - %(message)s
```

### 日誌級別
- INFO：正常操作
- ERROR：錯誤信息
- DEBUG：調試信息

## 配置示例

### 基本配置
```python
config = {
    "token": "your_token",
    "proxy_url": "http://proxy.example.com:8080"
}
```

### 完整配置
```python
config = {
    "token": "your_token",
    "proxy_url": "http://proxy.example.com:8080",
    "connect_timeout": 30,
    "read_timeout": 30,
    "write_timeout": 30,
    "allowed_updates": ["message", "callback_query"]
}
```

## 注意事項

1. 初始化順序：
   - 先初始化配置
   - 再初始化 Bot
   - 最後啟動服務

2. 錯誤處理：
   - 捕獲所有可能的異常
   - 記錄詳細的錯誤信息
   - 提供友好的錯誤提示

3. 資源管理：
   - 正確關閉 Bot 連接
   - 釋放所有資源
   - 處理中斷信號

4. 安全性：
   - 保護 Bot Token
   - 驗證用戶權限
   - 限制請求頻率 