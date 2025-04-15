# 農產品交易行情 API 範例

這個範例展示了如何使用農產品交易行情 API 來查詢農產品的交易行情資料。

## API 文件
- API 文件網址: [https://data.moa.gov.tw/apidocs.aspx#](https://data.moa.gov.tw/apidocs.aspx#)

## 功能特點

- 查詢特定日期的交易行情
- 查詢特定農產品的交易行情
- 查詢特定市場的交易行情
- 查詢特定時間範圍的交易行情
- 查詢病蟲害診斷服務問答集
- 查詢特定植物分類的病蟲害診斷服務問答集
- 查詢特定品名的病蟲害診斷服務問答集
- 分析病蟲害診斷服務問答集資料
- 查詢溯源農糧產品追溯系統-產品資訊
- 查詢溯源農糧產品追溯系統-生產者資訊

## 安裝需求

- Python 3.7+
- httpx
- python-dotenv

## 使用方法

1. 安裝依賴套件：

```bash
pip install httpx python-dotenv
```

2. 複製 `.env.example` 為 `.env` 並設置您的 API 金鑰（如果需要）：

```bash
cp examples/formal/moa/.env.example examples/formal/moa/.env
```

3. 編輯 `.env` 文件，設置您的 API 金鑰：

```
MOA_API_KEY=your_api_key_here
```

4. 執行程式：

```bash
# 農產品交易行情查詢
python -m examples.formal.moa -method agri_products

# 病蟲害診斷服務查詢
python -m examples.formal.moa -method pest_disease

# 溯源農糧產品追溯系統查詢
python -m examples.formal.moa -method traceability
```

## 通用參數

所有查詢功能都支援以下參數：

- `-analyze`：分析資料並顯示統計結果

## 農產品交易行情查詢

### 參數
- `-date`：交易日期，格式為 `YYYY.MM.DD`
- `-date_range`：日期範圍，格式為 `YYYY.MM.DD YYYY.MM.DD`
- `-crop`：農產品名稱
- `-market`：市場名稱
- `-recent`：最近幾天的交易行情，預設為 7 天

### 範例
```bash
# 查詢今天的農產品交易行情
python -m examples.formal.moa -method agri_products

# 查詢特定日期的農產品交易行情
python -m examples.formal.moa -method agri_products -date 2024.04.10

# 查詢特定日期範圍的農產品交易行情
python -m examples.formal.moa -method agri_products -date_range 2025.04.01 2025.04.10

# 查詢特定農產品的交易行情
python -m examples.formal.moa -method agri_products -crop 康乃馨

# 查詢特定市場的交易行情
python -m examples.formal.moa -method agri_products -market 台北市場

# 查詢最近幾天的交易行情
python -m examples.formal.moa -method agri_products -recent 3

# 分析交易行情資料
python -m examples.formal.moa -method agri_products -analyze
```

## 病蟲害診斷服務查詢

### 參數
- `-plant_type`：植物分類
- `-product`：品名
- `-search`：是否搜尋病蟲害診斷服務問答集

### 範例
```bash
# 查詢所有病蟲害診斷服務問答集
python -m examples.formal.moa -method pest_disease

# 查詢特定植物分類的病蟲害診斷服務問答集
python -m examples.formal.moa -method pest_disease -plant_type 果樹

# 查詢特定品名的病蟲害診斷服務問答集
python -m examples.formal.moa -method pest_disease -product 梨

# 搜尋病蟲害診斷服務問答集
python -m examples.formal.moa -method pest_disease -search -plant_type 果樹 -product 梨

# 分析病蟲害診斷服務問答集
python -m examples.formal.moa -method pest_disease -analyze
```

## 溯源農糧產品追溯系統查詢

### 參數
- `-trace_code`：追溯編號
- `-product_name`：產品名稱
- `-producer`：生產者
- `-address`：聯絡地址

### 範例
```bash
# 查詢所有溯源農糧產品追溯系統-產品資訊
python -m examples.formal.moa -method traceability

# 查詢特定追溯編號的產品資訊
python -m examples.formal.moa -method traceability -trace_code 123456

# 查詢特定產品名稱的產品資訊
python -m examples.formal.moa -method traceability -product_name 稻米

# 查詢特定生產者的生產者資訊
python -m examples.formal.moa -method traceability -producer 張三

# 查詢特定地址的生產者資訊
python -m examples.formal.moa -method traceability -address 台北市

# 分析生產者資料
python -m examples.formal.moa -method traceability -analyze
```

## API 說明

### 農產品交易行情

- **URL**: `/api/v1/AgriProductsTransType`
- **方法**: GET
- **參數**:
  - `Start_time`: 交易日期(起)
  - `End_time`: 交易日期(迄)
  - `CropCode`: 農產品代碼
  - `CropName`: 農產品名稱
  - `MarketName`: 市場名稱
  - `Page`: 頁碼控制
  - `TcType`: 農產品種類代碼

### 病蟲害診斷服務問答集

- **URL**: `/api/v1/PestDiseaseDiagnosisServiceType`
- **方法**: GET
- **參數**:
  - `Type`: 植物分類
  - `ProductName`: 品名
  - `Page`: 頁碼控制

### 溯源農糧產品追溯系統-產品資訊

- **URL**: `/api/v1/TWAgriProductsTraceabilityType_ProductInfo`
- **方法**: GET
- **參數**:
  - `TraceCode`: 追溯編號
  - `Product`: 產品名稱

### 溯源農糧產品追溯系統-生產者資訊

- **URL**: `/api/v1/TWAgriProductsTraceabilityType_ProducerInfo`
- **方法**: GET
- **參數**:
  - `TraceCode`: 追溯編號
  - `Producer`: 生產者
  - `Address`: 聯絡地址
  - `Page`: 頁碼控制

### 回應格式

#### 農產品交易行情

```json
{
  "RS": "OK",
  "Data": [
    {
      "TransDate": "114.04.10",
      "TcType": "N06",
      "CropCode": "FA100",
      "CropName": "康乃馨-紅",
      "MarketCode": "105",
      "MarketName": "台北市場",
      "Upper_Price": 53,
      "Middle_Price": 53,
      "Lower_Price": 53,
      "Avg_Price": 53,
      "Trans_Quantity": 19
    }
  ]
}
```

#### 病蟲害診斷服務問答集

```json
{
  "RS": "OK",
  "Data": [
    {
      "Type": "果樹",
      "ProductName": "梨",
      "Question": "梨(高接)於幼果果實底端處有黑色之斑點。   梨(高接)於花朵上有褐色之斑點。",
      "Answer": "經組織分離產胞鑑定是為黑斑病。   經組織分離產胞鑑定是為灰黴病。",
      "Provision": "可用23.7%依普同水懸劑1000倍或50%保粒快得寧可濕性粉劑1000倍，任選其中一種藥劑輪流防治，每隔七天一次，連續五次，採收前6天停止施藥。   目前沒有推薦防治藥劑。"
    }
  ]
}
```

#### 溯源農糧產品追溯系統-產品資訊

```json
{
  "RS": "OK",
  "Data": [
    {
      "TraceCode": "123456",
      "Product": "稻米",
      "Place": "台北市",
      "Mark": "有機認證",
      "Url": "https://example.com",
      "Status": "使用中",
      "ModifyDate": "2024-04-10"
    }
  ]
}
```

#### 溯源農糧產品追溯系統-生產者資訊

```json
{
  "RS": "OK",
  "Data": [
    {
      "TraceCode": "123456",
      "Producer": "張三",
      "Address": "台北市",
      "Mark": "有機認證",
      "Url": "https://example.com",
      "Description": "生產者簡介",
      "Status": "使用中",
      "ModifyDate": "2024-04-10"
    }
  ]
}
```

## 範例程式碼

### 農產品交易行情

```python
from examples.formal.moa.config import MOAConfig
from examples.formal.moa.client import MOAClient
from examples.formal.moa.services.agri_products_service import AgriProductsService

# 建立配置
config = MOAConfig()

# 建立客戶端
client = MOAClient(config)

# 建立農產品交易行情服務
agri_products_service = AgriProductsService(client)

# 查詢今天的交易行情
data = await agri_products_service.get_trans_by_date("2024.04.10")

# 顯示結果
agri_products_service.display_trans_summary(data)

# 分析資料
analysis = agri_products_service.analyze_trans_data(data)
agri_products_service.display_analysis(analysis)
```

### 病蟲害診斷服務問答集

```python
from examples.formal.moa.config import MOAConfig
from examples.formal.moa.client import MOAClient
from examples.formal.moa.services.pest_disease_service import PestDiseaseService

# 建立配置
config = MOAConfig()

# 建立客戶端
client = MOAClient(config)

# 建立病蟲害診斷服務
pest_disease_service = PestDiseaseService(client)

# 查詢病蟲害診斷服務問答集
data = await pest_disease_service.search_diagnosis(
    plant_type="果樹",
    product_name="梨"
)

# 顯示結果
pest_disease_service.display_diagnosis(data)

# 分析資料
analysis = pest_disease_service.analyze_diagnosis_data(data)
pest_disease_service.display_analysis(analysis)
```

### 溯源農糧產品追溯系統

```python
from examples.formal.moa.config import MOAConfig
from examples.formal.moa.client import MOAClient
from examples.formal.moa.services.traceability_service import TraceabilityService

# 建立配置
config = MOAConfig()

# 建立客戶端
client = MOAClient(config)

# 建立溯源農糧產品追溯系統服務
traceability_service = TraceabilityService(client)

# 查詢特定追溯編號的產品資訊
product_data = await traceability_service.get_product_by_trace_code("123456")
traceability_service.display_product_summary(product_data)

# 查詢特定追溯編號的生產者資訊
producer_data = await traceability_service.get_producer_by_trace_code("123456")
traceability_service.display_producer_summary(producer_data)

# 分析生產者資料
analysis = traceability_service.analyze_producer_data(producer_data)
traceability_service.display_producer_analysis(analysis)
```

## 注意事項

1. 日期格式為 `YYYY.MM.DD`
2. 所有參數都是選填的
3. 當回傳結果 `Next=true` 時，才需要傳入 `Page` 參數
4. 如果需要使用 API 金鑰，請在 `.env` 文件中設置 `MOA_API_KEY` 環境變數 