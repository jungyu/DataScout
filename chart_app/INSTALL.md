# DataScout Chart App 安裝指南

## 環境需求

- Python 3.8+ 
- pip 21.0+

## 安裝步驟

### 1. 創建虛擬環境 (推薦)

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows
```

### 2. 安裝依賴項

我們提供了兩個選項來安裝依賴項，以解決可能的套件衝突問題：

#### 選項 1: 標準安裝

這將安裝所有依賴項，但可能會遇到解決衝突的提示：

```bash
pip install -r requirements.txt
```

#### 選項 2: 分步安裝 (推薦)

這種方法可以避免套件衝突：

```bash
# 安裝主要 Web 框架
pip install fastapi uvicorn jinja2 python-multipart

# 安裝數據處理套件
pip install pandas numpy openpyxl xlrd

# 安裝解析與圖形處理套件
pip install beautifulsoup4==4.9.3
pip install matplotlib pillow

# 安裝其他工具
pip install requests python-dateutil pytz tqdm
```

### 3. 設置數據目錄

確保以下目錄存在：

```bash
mkdir -p data/csv data/json data/excel
mkdir -p static/uploads/csv static/uploads/json static/uploads/excel
```

### 4. 啟動應用程式

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

現在，您可以在瀏覽器中訪問 `http://localhost:8000` 來使用應用程式。

## 常見問題

### 依賴衝突

如果您遇到依賴衝突問題，請嘗試：

1. 使用上面的"分步安裝"方法
2. 或者使用 `--no-dependencies` 選項：

```bash
pip install -r requirements.txt --no-dependencies
```

然後手動安裝缺少的套件。

### 無法導入模組

如果遇到 `ModuleNotFoundError`，請確保您已經啟動了虛擬環境，並且安裝了所有必要的套件。

### 上傳檔案錯誤

如果檔案上傳功能失敗，請確保：

1. 上傳目錄有正確的寫入權限
2. Python 有足夠的記憶體來處理大文件
