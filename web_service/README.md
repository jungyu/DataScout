# DataScout Web Service

提供 DataScout 專案的 Web 服務和儀表板功能。使用 FastAPI 框架構建，提供高效、可靠的 API 服務和數據視覺化界面。

## 功能特點

- 基於 FastAPI 構建的高效 Web 服務
- 使用 Jinja2 模板引擎處理前端頁面渲染
- 支持多种图表类型的数据可视化
- 支持文件上传和数据处理功能
- 提供 OLAP 操作 API

## 目錄結構

```
web_service/
├── app/                     # 應用主包
│   ├── __init__.py
│   ├── main.py              # FastAPI 主程式
│   ├── apis/                # API 路由與邏輯
│   ├── models/              # 資料模型
│   └── core/                # 核心功能和配置
├── static/                  # 前端編譯後的檔案
├── templates/               # Jinja2 模板
├── tests/                   # 測試目錄
├── scripts/                 # 腳本和工具
├── pyproject.toml           # 現代 Python 專案配置
├── requirements.txt         # 依賴管理
└── requirements-dev.txt     # 開發環境依賴
```

## 快速開始

### 開發環境設置

1. 克隆儲存庫

```bash
git clone https://github.com/your-username/datascout.git
cd datascout
```

2. 啟動 Web Service (後端)

```bash
cd web_service
./scripts/start_dev.sh
```

此腳本會自動:
- 創建 Python 虛擬環境
- 安裝所需依賴
- 構建前端資源 (如果需要)
- 啟動 FastAPI 開發伺服器

3. 啟動 Web Frontend (前端) - 可選

如果您需要同時進行前端開發，可以在另一個終端中運行:

```bash
cd web_frontend
./scripts/start_dev.sh
```

此腳本會:
- 檢查並安裝所需的 Node.js 依賴
- 同時運行 Webpack 監視模式 (處理 JS) 和 Tailwind CSS 監視模式 (處理 CSS)
- 自動刷新頁面以反映前端代碼變更

4. 前後端整合開發模式

為同時開發前端和後端，建議開啟兩個終端視窗:

##### 前端開發終端

```bash
cd web_frontend
./scripts/start_dev.sh
```

##### 後端開發終端

```bash
cd web_service
./scripts/start_dev.sh
```

當系統詢問時選擇「是」來構建前端資源:

```text
檢查是否需要構建前端資源...
是否構建前端資源? (y/n): y
```

5. 構建前端生產版本

若需要為生產環境構建前端資源:

```bash
cd web_frontend
./scripts/build_frontend.sh --output ../web_service/static
```

這會將編譯好的前端檔案直接輸出到後端的靜態資源目錄。

6. 訪問應用

- API 文檔: http://localhost:8000/api/docs
- 儀表板: http://localhost:8000/

### 常見問題排解

1. **前端資源未載入**
   - 確保已正確構建前端資源
   - 檢查 web_service/static 目錄中是否有 JS/CSS 文件

2. **依賴安裝失敗**
   - 對於前端：檢查 Node.js 版本 (推薦 v16+)
   - 對於後端：確保 Python 3.8+ 及 pip 已安裝

3. **端口衝突**
   - 如果 8000 端口被占用，可在 start_dev.sh 中修改端口號

4. **模板未找到**
   - 確保 templates 目錄中有所需的 HTML 模板文件

## API 端點

| 端點 | 方法 | 描述 |
|------|------|------|
| `/api/chart-data` | GET | 獲取儀表板數據 |
| `/api/data-files` | GET | 獲取可用數據文件列表 |
| `/api/file-data` | GET | 獲取特定文件的數據 |
| `/api/upload-file` | POST | 上傳數據文件 |
| `/api/chart-from-json` | POST | 從 JSON 數據生成圖表 |
| `/api/olap-operation` | POST | 執行 OLAP 操作 |
| `/health` | GET | 健康檢查端點 |

## 技術堆疊

- **後端框架**: FastAPI
- **模板引擎**: Jinja2
- **資料處理**: Pandas, NumPy
- **文件處理**: OpenPyXL
- **前端資源**: 來自 web_frontend 目錄

## 開發指南

### 安裝開發依賴

```bash
pip install -r requirements-dev.txt
```

### 運行測試

```bash
pytest
```

### 代碼格式化

```bash
black app tests
isort app tests
```

### 靜態類型檢查

```bash
mypy app
```

## 部署

### 使用 Docker

```bash
docker build -t datascout-web-service .
docker run -p 8000:8000 datascout-web-service
```

### 使用 Gunicorn 部署

```bash
gunicorn app.main:app -k uvicorn.workers.UvicornWorker -w 4 --bind 0.0.0.0:8000
```

## 授權

[MIT](LICENSE)
