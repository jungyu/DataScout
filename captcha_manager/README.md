# Captcha Manager 模組

## 專案概述

Captcha Manager 模組提供了驗證碼識別和處理的功能，支援多種驗證碼類型，包括圖片驗證碼、滑動驗證碼等。本模組整合了多種驗證碼識別技術，提供統一的接口來處理驗證碼。

## 環境設置

### 1. 創建虛擬環境

```bash
# 進入 captcha_manager 目錄
cd captcha_manager

# 創建虛擬環境
python -m venv venv

# 啟動虛擬環境
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

### 2. 安裝依賴

```bash
# 安裝依賴套件
pip install -r requirements.txt

# 安裝 Tesseract OCR（用於文字識別）
# macOS
brew install tesseract
# Ubuntu
sudo apt-get install tesseract-ocr
```

### 3. 環境變數設置

在專案根目錄創建 `.env` 文件，添加以下配置：

```env
# Captcha 配置
TESSERACT_PATH=/usr/local/bin/tesseract
CAPTCHA_TIMEOUT=30
CAPTCHA_RETRY=3

# API 配置（可選）
API_KEY=your_api_key
API_URL=your_api_url
```

## 目錄結構

```
captcha_manager/
├── core/           # 核心組件
├── solvers/        # 驗證碼解析器
├── models/         # 模型文件
├── utils/          # 工具函數
└── tests/          # 測試用例
```

## 使用方式

### 基本使用

```python
from captcha_manager import CaptchaSolver

# 創建驗證碼解析器
solver = CaptchaSolver()

# 處理圖片驗證碼
result = solver.solve_image_captcha(
    image_path='captcha.png',
    captcha_type='text'
)

# 處理滑動驗證碼
result = solver.solve_slider_captcha(
    background_image='bg.png',
    slider_image='slider.png'
)
```

### 測試用例

```python
import pytest
from captcha_manager import CaptchaSolver

def test_image_captcha():
    solver = CaptchaSolver()
    result = solver.solve_image_captcha('test_captcha.png')
    assert result is not None
```

## 主要功能

1. 圖片驗證碼
   - 文字識別
   - 圖片預處理
   - 噪點去除
   - 字符分割

2. 滑動驗證碼
   - 缺口定位
   - 軌跡生成
   - 滑動模擬
   - 結果驗證

3. 點選驗證碼
   - 目標識別
   - 點擊模擬
   - 結果驗證

4. 語音驗證碼
   - 語音識別
   - 文字轉換
   - 結果驗證

## 注意事項

1. 確保在執行前已啟動虛擬環境
2. 檢查環境變數是否正確設置
3. 確保所有依賴都已正確安裝
4. 注意驗證碼識別的使用限制

## 依賴套件說明

- `opencv-python`: 圖像處理
- `numpy`: 數值計算
- `pillow`: 圖像處理
- `pytesseract`: OCR 文字識別
- `python-dotenv`: 環境變數管理
- `aiohttp`: 非同步 HTTP 客戶端
- `httpx`: 現代 HTTP 客戶端
- `pytest`: 測試框架
- `pytest-asyncio`: 非同步測試支援 