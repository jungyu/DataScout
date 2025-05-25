# 驗證碼管理器

## 專案概述

驗證碼管理器是一個強大的驗證碼解決工具，提供多種驗證碼解決方案，支持圖片驗證碼、滑動驗證碼等。它支持異步操作、錯誤處理、日誌記錄等功能，使驗證碼解決變得簡單而高效。

## 安裝

```bash
# 開發模式安裝
pip install -e .

# 或直接安裝
pip install captcha_manager
```

## 使用方式

### 作為包使用

```python
from captcha_manager import CaptchaSolver, SolverConfig

# 創建配置
config = SolverConfig(
    type="image",
    timeout=30
)

# 創建驗證碼解決器
solver = CaptchaSolver(config)

# 解決驗證碼
async def main():
    # 從文件解決
    result = await solver.solve("path/to/captcha.png")
    print(f"驗證碼結果: {result}")
    
    # 從 URL 解決
    result = await solver.solve_url("https://example.com/captcha.png")
    print(f"驗證碼結果: {result}")

# 運行
import asyncio
asyncio.run(main())
```

### 命令行使用

```bash
# 解決本地驗證碼圖片
captcha-manager solve path/to/captcha.png --type image

# 解決 URL 驗證碼
captcha-manager solve-url https://example.com/captcha.png --type image
```

## 目錄結構

```
captcha_manager/
├── captcha_solver/  # 驗證碼解決器
├── examples/        # 使用範例
└── tests/          # 測試文件
```

## 主要功能

1. 驗證碼解決
   - 圖片驗證碼
   - 滑動驗證碼
   - 點選驗證碼
   - 自定義驗證碼

2. 異步支持
   - 異步操作
   - 並發處理
   - 超時控制

3. 工具支持
   - 日誌記錄
   - 配置管理
   - 錯誤處理

## 注意事項

1. 確保在虛擬環境中安裝
2. 檢查依賴版本兼容性
3. 注意異步操作的正確使用
4. 合理配置超時和重試策略

## 依賴套件

### 核心依賴
- aiohttp: 異步 HTTP 客戶端
- pydantic: 數據驗證
- loguru: 日誌管理
- playwright: 瀏覽器自動化
- pillow: 圖像處理
- numpy: 數值計算

### 開發依賴
- pytest: 測試框架
- black: 代碼格式化
- isort: 導入排序
- mypy: 類型檢查 