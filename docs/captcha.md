# 驗證碼處理指南

## 簡介
本文件說明如何在使用 Selenium 爬蟲時處理各種驗證碼（CAPTCHA）。本系統採用模組化設計,支援多種驗證碼類型。

## 系統架構

```
captcha/
├── __init__.py
├── captcha_manager.py        # 驗證碼管理器
├── solvers/                  # 驗證碼解決器
│   ├── __init__.py
│   ├── base_solver.py       # 基礎解決器抽象類
│   ├── text_solver.py       # 文字驗證碼解決器
│   ├── slider_solver.py     # 滑塊驗證碼解決器
│   ├── click_solver.py      # 點擊驗證碼解決器
│   ├── rotate_solver.py     # 旋轉驗證碼解決器
│   └── recaptcha_solver.py  # reCAPTCHA解決器
└── ml/
    ├── __init__.py
    └── model_loader.py      # 機器學習模型加載工具
```

## 使用方法

### 基本使用範例

```python
from selenium import webdriver
from captcha.captcha_manager import CaptchaManager

# 初始化 WebDriver
driver = webdriver.Chrome()

# 建立驗證碼管理器
captcha_manager = CaptchaManager(driver, config_path="config/captcha_config.json")

try:
    # 導航到目標網站
    driver.get("https://example.com/login")
    
    # 填寫登入表單
    driver.find_element_by_id("username").send_keys("test_user")
    driver.find_element_by_id("password").send_keys("test_password")
    
    # 自動檢測並解決驗證碼
    if captcha_manager.detect_and_solve():
        print("驗證碼已成功解決")
        driver.find_element_by_id("login-button").click()
    else:
        print("驗證碼解決失敗")

finally:
    driver.quit()
```

### 解決特定類型驗證碼

```python
# 解決文字驗證碼
success = captcha_manager.solve_specific('text')

# 解決滑塊驗證碼
success = captcha_manager.solve_specific('slider')

# 解決點擊驗證碼
success = captcha_manager.solve_specific('click')
```

## 配置說明

配置文件（config/captcha_config.json）支援以下選項：

```json
{
    "general": {
        "max_retries": 3,
        "save_samples": true,
        "sample_dir": "../captchas",
        "enable_machine_learning": false
    },
    "text_captcha": {
        "enabled": true,
        "tesseract_config": {
            "lang": "eng",
            "cmd_path": "/usr/local/bin/tesseract"
        }
    },
    "slider_captcha": {
        "enabled": true,
        "simulation": {
            "track_deviation": 0.2,
            "move_time": {"min": 800, "max": 2000}
        }
    }
}
```

## 支援的驗證碼類型

### 1. 文字驗證碼
- 支援多種OCR引擎
- 提供圖像預處理功能
- 可整合機器學習模型

### 2. 滑塊驗證碼
- 智能目標定位
- 人性化移動軌跡
- 多級容錯機制

### 3. 點擊驗證碼
- 物件識別
- 智能座標計算
- 模擬真實點擊

### 4. 旋轉驗證碼
- 自動方向識別
- 精確角度計算
- 平滑旋轉操作

### 5. reCAPTCHA
- 支援多家解決服務
- 音頻驗證替代方案
- 智能行為模擬

## 最佳實踐建議

1. **循序漸進**：從基本方案開始，視需求增加複雜度
2. **樣本收集**：保存成功和失敗案例以改進系統
3. **行為模擬**：重視操作的自然性
4. **錯誤處理**：實作完整的重試機制
5. **定期更新**：因應驗證碼系統的更新調整策略

## 常見問題處理

1. 驗證碼識別失敗
   - 調整預處理參數
   - 使用備用識別方案
   - 考慮第三方服務

2. 行為被判定為機器人
   - 增加操作隨機性
   - 調整延遲時間
   - 優化移動軌跡

## 延伸資源

- OpenCV 文檔：https://docs.opencv.org/
- Tesseract OCR：https://github.com/tesseract-ocr/tesseract
- Selenium 文檔：https://www.selenium.dev/documentation/