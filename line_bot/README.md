# DataScout LINE Bot

DataScout LINE Bot 是 DataScout 爬蟲框架的 LINE 機器人介面，允許使用者通過 LINE 平台便捷地操控爬蟲任務、追蹤狀態並獲取結果。

## 功能特色

- 🔄 **爬蟲控制**：啟動、排程和取消爬蟲任務
- 📊 **狀態監控**：實時追蹤任務狀態與進度
- 📋 **結果處理**：查看和匯出不同格式的爬蟲結果
- 📸 **圖像分析**：使用 Google Gemini AI 分析上傳的圖片內容
- 🔍 **文字提取**：從圖片中識別與提取文字內容
- 👥 **多用戶支援**：支援多用戶訪問，具有身份驗證機制
- 🔒 **權限控制**：區分普通用戶和管理員權限
- ⏱️ **頻率限制**：防止濫用的請求頻率控制

## 可用指令

### 基本指令
- 「開始」 - 開始使用機器人
- 「說明」 - 顯示幫助訊息

### 爬蟲操作
- 「爬蟲 [URL] [選項]」 - 啟動爬蟲任務
- 「排程 [URL] [選項] [時間]」 - 排程爬蟲任務
- 「取消 [任務ID]」 - 取消爬蟲任務

### 狀態查詢
- 「狀態 [任務ID]」 - 查詢特定任務狀態
- 「列表」 - 列出所有進行中的任務
- 「歷史」 - 顯示歷史任務

### 結果處理
- 「結果 [任務ID]」 - 獲取任務結果
- 「匯出 [任務ID] [格式]」 - 匯出特定格式的結果

### 圖像處理
- 「圖片」 - 顯示圖像分析功能說明
- 直接發送圖片 - 自動分析圖片內容並提供互動按鈕
- 發送圖片時添加說明 - 使用自定義提示詞引導分析

### 管理員指令
- 「系統」 - 查看系統狀態
- 「所有任務」 - 列出所有任務
- 「終止 [任務ID]」 - 強制終止任務

## 安裝與設定

### 環境需求

- Python 3.8+
- DataScout 爬蟲框架
- LINE Channel Access Token 和 Channel Secret

### 安裝步驟

1. 安裝所需依賴：
   ```bash
   pip install -r line_bot/requirements.txt
   ```

2. 配置環境變數：
   - 複製 `line_bot.env.example` 為 `.env`
   - 編輯 `.env` 文件，填入 LINE Channel Access Token、Channel Secret 和其他配置

3. 啟動機器人：
   ```bash
   python line_bot/bot.py
   ```

## 基本用法

1. 開始使用機器人：在 LINE 中輸入「開始」
2. 啟動爬蟲任務：「爬蟲 https://example.com headless=true」
3. 查看任務狀態：「狀態 [任務ID]」
4. 獲取爬蟲結果：「結果 [任務ID]」

## 配置選項

在 `.env` 文件中可以配置以下選項：

- `LINE_CHANNEL_ACCESS_TOKEN`：LINE Channel Access Token
- `LINE_CHANNEL_SECRET`：LINE Channel Secret
- `ADMIN_USER_IDS`：管理員用戶 ID 列表
- `AUTHORIZED_USERS`：授權用戶 ID 列表
- `REQUIRE_AUTH`：是否啟用授權檢查
- `GEMINI_API_KEY`：Google Gemini API 金鑰，用於圖像分析功能

## 架構設計

DataScout LINE Bot 採用模組化設計，主要包含以下元件：

- **Bot 核心**：處理 LINE API 互動
- **指令處理器**：負責解析和處理用戶指令
- **任務管理器**：管理爬蟲任務的狀態和執行
- **中介軟體**：處理身份驗證和請求限制
- **格式化工具**：格式化輸出結果和狀態訊息

## 注意事項

- 爬蟲活動應遵守目標網站的使用條款和相關法規
- 避免頻繁請求以防止被封鎖
- 妥善保管 Channel Access Token 和 Channel Secret，避免未授權訪問

## 授權條款

參見 DataScout 專案的授權條款 