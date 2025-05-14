# DataScout Telegram Bot

DataScout Telegram Bot 是 DataScout 爬蟲框架的 Telegram 機器人介面，允許使用者通過 Telegram 平台便捷地操控爬蟲任務、追蹤狀態並獲取結果。

## 功能特色

- 🔄 **爬蟲控制**：啟動、排程和取消爬蟲任務
- 📊 **狀態監控**：實時追蹤任務狀態與進度
- 📋 **結果處理**：查看和匯出不同格式的爬蟲結果
- 👥 **多用戶支援**：支援多用戶訪問，具有身份驗證機制
- 🔒 **權限控制**：區分普通用戶和管理員權限
- ⏱️ **頻率限制**：防止濫用的請求頻率控制

## 可用指令

### 基本指令
- `/start` - 開始使用機器人
- `/help` - 顯示幫助訊息

### 爬蟲操作
- `/crawl [URL] [選項]` - 啟動爬蟲任務
- `/schedule [URL] [選項] [時間]` - 排程爬蟲任務
- `/cancel [任務ID]` - 取消爬蟲任務

### 狀態查詢
- `/status [任務ID]` - 查詢特定任務狀態
- `/list` - 列出所有進行中的任務
- `/history` - 顯示歷史任務

### 結果處理
- `/result [任務ID]` - 獲取任務結果
- `/export [任務ID] [格式]` - 匯出特定格式的結果

### 管理員指令
- `/system` - 查看系統狀態
- `/alltasks` - 列出所有任務
- `/kill [任務ID]` - 強制終止任務

## 安裝與設定

### 環境需求

- Python 3.8+
- DataScout 爬蟲框架
- 有效的 Telegram Bot Token

### 安裝步驟

1. 安裝所需依賴：
   ```bash
   pip install -r telegram_bot/requirements.txt
   ```

2. 配置環境變數：
   - 複製 `telegram_bot.env.example` 為 `.env`
   - 編輯 `.env` 文件，填入 Telegram Bot Token 和其他配置

3. 啟動機器人：
   ```bash
   python run_telegram_bot.py
   ```

## 基本用法

1. 開始使用機器人：在 Telegram 中輸入 `/start`
2. 啟動爬蟲任務：`/crawl https://example.com headless=true`
3. 查看任務狀態：`/status [任務ID]`
4. 獲取爬蟲結果：`/result [任務ID]`

## 配置選項

在 `.env` 文件中可以配置以下選項：

- `DATASCOUT_BOT_TOKEN`：Telegram Bot Token
- `ADMIN_USER_IDS`：管理員用戶 ID 列表
- `AUTHORIZED_USERS`：授權用戶 ID 列表
- `REQUIRE_AUTH`：是否啟用授權檢查

## 架構設計

DataScout Telegram Bot 採用模組化設計，主要包含以下元件：

- **Bot 核心**：處理 Telegram API 互動
- **指令處理器**：負責解析和處理用戶指令
- **任務管理器**：管理爬蟲任務的狀態和執行
- **中介軟體**：處理身份驗證和請求限制
- **格式化工具**：格式化輸出結果和狀態訊息

## 注意事項

- 爬蟲活動應遵守目標網站的使用條款和相關法規
- 避免頻繁請求以防止被封鎖
- 妥善保管 Bot Token 和授權資訊，避免未授權訪問

## 授權條款

參見 DataScout 專案的授權條款
