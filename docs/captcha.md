# 驗證碼處理模組

## 概述

驗證碼處理模組（`src/captcha`）提供了一個完整的驗證碼解決方案，支持多種驗證碼類型的檢測、識別和處理。該模組採用模組化設計，可以輕鬆擴展以支持新的驗證碼類型。

## 目錄結構

```
src/captcha/
├── __init__.py              # 模組初始化文件
├── captcha_manager.py       # 驗證碼管理器
├── detection.py             # 驗證碼檢測器
├── config.py                # 配置管理
├── handlers/                # 驗證碼處理器
│   ├── recaptcha.py        # reCAPTCHA 處理器
│   ├── service.py          # 第三方服務處理器
│   ├── audio.py            # 音頻驗證碼處理器
│   └── image.py            # 圖像驗證碼處理器
├── utils/                   # 工具函數
│   ├── text.py             # 文本處理工具
│   ├── audio.py            # 音頻處理工具
│   ├── image.py            # 圖像處理工具
│   ├── logger.py           # 日誌工具
│   └── error.py            # 錯誤處理工具
├── solvers/                 # 驗證碼求解器
│   ├── base_solver.py      # 基礎求解器
│   ├── recaptcha_solver.py # reCAPTCHA 求解器
│   ├── text_solver.py      # 文本驗證碼求解器
│   ├── slider_solver.py    # 滑塊驗證碼求解器
│   ├── rotate_solver.py    # 旋轉驗證碼求解器
│   └── click_solver.py     # 點擊驗證碼求解器
├── ml/                     # 機器學習相關
│   └── model_loader.py     # 模型加載器
└── third_party/            # 第三方服務
    ├── config.py           # 第三方服務配置
    └── service_client.py   # 第三方服務客戶端
```

## 主要組件

### 1. 驗證碼管理器 (CaptchaManager)

驗證碼管理器是整個模組的核心，提供統一的接口來處理各種類型的驗證碼。

```python
from src.captcha import CaptchaManager

# 初始化驗證碼管理器
captcha_manager = CaptchaManager(
    driver=webdriver,
    timeout=10,
    screenshot_dir="captcha_screenshots",
    third_party_service={
        "api_key": "your_api_key",
        "service_url": "https://api.example.com"
    }
)

# 檢測驗證碼
detection_result = captcha_manager.detect_captcha()

# 解決驗證碼
success = captcha_manager.solve_captcha(detection_result)
```

### 2. 驗證碼類型

支持以下驗證碼類型：

- `RECAPTCHA`: Google reCAPTCHA
- `HCAPTCHA`: hCaptcha
- `IMAGE_CAPTCHA`: 傳統圖片驗證碼
- `SLIDER_CAPTCHA`: 滑塊驗證碼
- `ROTATE_CAPTCHA`: 旋轉驗證碼
- `CLICK_CAPTCHA`: 點擊驗證碼
- `TEXT_CAPTCHA`: 文字問答驗證碼
- `MANUAL`: 人工手動驗證
- `CUSTOM`: 自定義驗證函式
- `UNKNOWN`: 未知類型

### 3. 驗證碼處理器 (Handlers)

#### 3.1 reCAPTCHA 處理器

處理 Google reCAPTCHA 驗證碼：

```python
from src.captcha.handlers.recaptcha import RecaptchaHandler

handler = RecaptchaHandler(driver)
success = handler.solve()
```

#### 3.2 第三方服務處理器

使用第三方服務解決驗證碼：

```python
from src.captcha.handlers.service import ServiceHandler

handler = ServiceHandler(
    driver,
    api_key="your_api_key",
    service_url="https://api.example.com"
)
success = handler.solve()
```

### 4. 驗證碼求解器 (Solvers)

#### 4.1 文本驗證碼求解器

```python
from src.captcha.solvers.text_solver import TextSolver

solver = TextSolver(driver)
result = solver.solve()
```

#### 4.2 滑塊驗證碼求解器

```python
from src.captcha.solvers.slider_solver import SliderSolver

solver = SliderSolver(driver)
result = solver.solve()
```

#### 4.3 點擊驗證碼求解器

```python
from src.captcha.solvers.click_solver import ClickSolver

solver = ClickSolver(driver)
result = solver.solve()
```

### 5. 工具函數 (Utils)

#### 5.1 圖像處理

```python
from src.captcha.utils.image import process_image

processed_image = process_image(image_data)
```

#### 5.2 音頻處理

```python
from src.captcha.utils.audio import process_audio

audio_text = process_audio(audio_data)
```

#### 5.3 文本處理

```python
from src.captcha.utils.text import clean_text

cleaned_text = clean_text(text)
```

### 6. 機器學習模型 (ML)

使用預訓練模型進行驗證碼識別：

```python
from src.captcha.ml.model_loader import ModelLoader

model = ModelLoader.load_model("model_name")
prediction = model.predict(image_data)
```

### 7. 第三方服務集成

配置和使用第三方驗證碼解決服務：

```python
from src.captcha.third_party.config import ThirdPartyServiceConfig
from src.captcha.third_party.service_client import ThirdPartyServiceClient

config = ThirdPartyServiceConfig(
    api_key="your_api_key",
    service_url="https://api.example.com"
)
client = ThirdPartyServiceClient(config)
result = client.solve_captcha(captcha_data)
```

## 配置選項

### 1. 基本配置

```python
config = {
    "timeout": 10,                    # 超時時間（秒）
    "screenshot_dir": "screenshots",  # 截圖保存目錄
    "retry_count": 3,                # 重試次數
    "retry_delay": 1,                # 重試延遲（秒）
    "log_level": "INFO"              # 日誌級別
}
```

### 2. 第三方服務配置

```python
third_party_config = {
    "api_key": "your_api_key",
    "service_url": "https://api.example.com",
    "timeout": 30,
    "max_retries": 3
}
```

## 錯誤處理

模組提供了完整的錯誤處理機制：

```python
from src.captcha.utils.error import CaptchaError

try:
    result = captcha_manager.solve_captcha()
except CaptchaError as e:
    print(f"驗證碼處理失敗: {e}")
```

## 最佳實踐

1. 使用適當的超時設置
2. 實現錯誤重試機制
3. 保存驗證碼樣本以供分析
4. 使用日誌記錄關鍵操作
5. 定期更新模型和配置

## 注意事項

1. 確保網絡連接穩定
2. 遵守目標網站的驗證碼使用政策
3. 適當處理驗證碼失敗情況
4. 注意保護API密鑰等敏感信息
5. 定期檢查和更新第三方服務配置