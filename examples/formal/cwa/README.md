# 中央氣象局 API 使用指南

本專案提供與中央氣象局 API 互動的 Python 程式，支援多種氣象資料的查詢功能。

## 安裝

1. 複製專案到本地：
```bash
git clone [repository_url]
cd [project_directory]
```

2. 安裝依賴套件：
```bash
pip install -r requirements.txt
```

3. 設定 API 金鑰：
   - 複製 `.env.example` 為 `.env`
   - 在 `.env` 檔案中設定您的 API 金鑰：
     ```
     CWA_API_KEY=your_api_key_here
     ```

## 基本使用方式

使用以下命令執行不同的查詢功能：

```bash
# 地震資料查詢
python -m examples.formal.cwa -method earthquake

# 雨量資料查詢
python -m examples.formal.cwa -method rainfall

# 颱風資料查詢
python -m examples.formal.cwa -method typhoon

# 天氣預報查詢
python -m examples.formal.cwa -method forecast

# 氣象觀測查詢
python -m examples.formal.cwa -method observation

# 全台各鄉鎮天氣預報查詢
python -m examples.formal.cwa -method township_forecast
```

## 通用參數

所有查詢功能都支援以下參數：

- `-limit`：限制返回的資料筆數（預設：5）
- `-time_range`：時間範圍，格式為 `YYYY-MM-DD YYYY-MM-DD`

## 地震資料查詢

### 參數
- `-area`：地區名稱，可指定多個，例如：`-area 臺北市 新北市`

### 範例
```bash
# 查詢最近地震
python -m examples.formal.cwa -method earthquake

# 查詢特定地區的地震
python -m examples.formal.cwa -method earthquake -area 臺北市

# 查詢特定時間範圍的地震
python -m examples.formal.cwa -method earthquake -time_range 2024-04-01 2024-04-15
```

## 雨量資料查詢

### 參數
- `-station`：測站編號，可指定多個
- `-monthly`：是否取得每月統計值

### 範例
```bash
# 查詢所有測站的雨量
python -m examples.formal.cwa -method rainfall

# 查詢特定測站的雨量
python -m examples.formal.cwa -method rainfall -station 466881

# 查詢每月統計值
python -m examples.formal.cwa -method rainfall -monthly
```

## 颱風資料查詢

### 參數
- `-typhoon_no`：颱風編號
- `-forecast`：是否取得預報資料
- `-forecast_hours`：預報時距（小時），可指定多個，預設為 6,12,24,48,72

### 範例
```bash
# 查詢目前活動中的颱風
python -m examples.formal.cwa -method typhoon

# 查詢特定編號的颱風
python -m examples.formal.cwa -method typhoon -typhoon_no 2313

# 查詢颱風預報
python -m examples.formal.cwa -method typhoon -forecast
```

## 天氣預報查詢

### 參數
- `-location`：縣市名稱
- `-element`：天氣因子名稱

### 範例
```bash
# 查詢所有縣市的天氣預報
python -m examples.formal.cwa -method forecast

# 查詢特定縣市的天氣預報
python -m examples.formal.cwa -method forecast -location 臺北市

# 查詢特定天氣因子的預報
python -m examples.formal.cwa -method forecast -element 溫度
```

## 氣象觀測查詢

### 參數
- `-station_name`：測站名稱
- `-county`：縣市名稱

### 範例
```bash
# 查詢所有測站的觀測資料
python -m examples.formal.cwa -method observation

# 查詢特定測站的觀測資料
python -m examples.formal.cwa -method observation -station_name 臺北

# 查詢特定縣市的觀測資料
python -m examples.formal.cwa -method observation -county 臺北市
```

## 全台各鄉鎮天氣預報查詢

### API 端點
```
https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-D0047-093
```

### 參數
- `-location_id`：鄉鎮市區預報資料之資料項編號
- `-location_ids`：鄉鎮市區預報資料之資料項編號列表，最多五個
- `-location_name`：鄉鎮市區名稱
- `-location_names`：鄉鎮市區名稱列表
- `-elements`：天氣預報天氣因子列表
- `-time_from`：時間區段起始時間，格式為「yyyy-MM-ddThh:mm:ss」
- `-time_to`：時間區段結束時間，格式為「yyyy-MM-ddThh:mm:ss」
- `-days`：要查詢的天數，預設為 7 天

### 可用天氣因子
- 天氣現象 (Wx)
- 降雨機率 (PoP)
- 最低溫度 (MinT)
- 最高溫度 (MaxT)
- 體感溫度 (CI)
- 相對濕度 (RH)
- 風向 (WD)
- 風速 (WS)
- 風級 (Wx)
- 舒適度指數 (CI)
- 紫外線指數 (UVI)
- 天氣描述 (WeatherDescription)

### 範例
```bash
# 查詢臺北市的天氣預報（預設）
python -m examples.formal.cwa -method township_forecast

# 查詢特定鄉鎮市區的天氣預報
python -m examples.formal.cwa -method township_forecast -location_id F-D0047-001

# 查詢特定鄉鎮市區名稱的天氣預報
python -m examples.formal.cwa -method township_forecast -location_name "臺北市"

# 查詢特定時間範圍的天氣預報
python -m examples.formal.cwa -method township_forecast -time_from "2024-04-15T00:00:00" -time_to "2024-04-16T00:00:00"

# 查詢特定天氣因子的預報
python -m examples.formal.cwa -method township_forecast -elements 溫度 降雨機率

# 查詢多個鄉鎮市區的天氣預報
python -m examples.formal.cwa -method township_forecast -location_ids F-D0047-001 F-D0047-002
```

## 注意事項

1. 請確保已正確設定 API 金鑰
2. 時間範圍格式必須符合要求
3. 部分參數可能需要特定的格式或值
4. API 可能有呼叫頻率限制 