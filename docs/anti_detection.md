# 爬蟲反偵測機制說明

## 常見的爬蟲偵測方式

1. User-Agent 檢查
   - 網站會檢查請求標頭中的 User-Agent 是否來自正常瀏覽器
   - 若使用預設的 WebDriver User-Agent，容易被識別為爬蟲

2. WebDriver 特徵檢測
   - 檢查 navigator.webdriver 屬性
   - 檢查瀏覽器特定的自動化控制接口
   
3. 行為模式分析
   - 點擊與操作過於規律
   - 請求速度異常快
   - 缺乏正常使用者的隨機性

## 解決方案

### 1. User-Agent 偽裝
```python
options = webdriver.ChromeOptions()
options.add_argument('user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36')
```

### 2. 移除 WebDriver 特徵
```python
options.add_argument('--disable-blink-features=AutomationControlled')
options.add_experimental_option('excludeSwitches', ['enable-automation'])
options.add_experimental_option('useAutomationExtension', False)
```

### 3. 模擬真實使用者行為
- 加入隨機等待時間
- 模擬滑鼠移動軌跡
- 隨機調整視窗大小
- 增加頁面滾動行為

### 4. 使用代理伺服器
```python
options.add_argument('--proxy-server=http://proxy_ip:port')
```

## 注意事項

1. 不同網站可能採用不同的偵測機制，需要針對性調整
2. 建議在程式中加入錯誤處理機制
3. 遵守網站的 robots.txt 規則
4. 適當的請求間隔，避免對目標網站造成負擔
