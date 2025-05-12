# Neural Prophet 入門指引

Neural Prophet 是一款結合了神經網路與傳統時間序列演算法的現代化預測框架，基於 PyTorch 建構，受 Facebook Prophet 啟發並加以擴展。本指引將介紹 Neural Prophet 的基礎知識、應用場景、數據準備方法與結果解讀技巧，幫助您快速掌握這個強大的預測工具。

## 1. Neural Prophet 定位與應用

### 1.1 概念介紹

Neural Prophet 是一個開源的人機協作預測框架，專為時間序列分析與預測設計。它結合了 Facebook Prophet 的可解釋性與 PyTorch 深度學習的彈性，使用神經網路增強了傳統時間序列建模方法。其名稱 "Neural Prophet" 體現了它的核心理念：在 Prophet 的基礎上加入神經網路元素，同時保持模型的可解釋性。

Neural Prophet 的主要特點包括：

- **易於使用**：簡潔的 API 設計，讓使用者能快速上手並構建模型
- **可解釋性**：保留了時間序列分解的能力，可視化各組件如趨勢、季節性等
- **彈性**：支持多種模型組件，如自迴歸、趨勢變點、多重季節性等
- **基於神經網路**：使用 PyTorch 實現，支持深度學習特性與 GPU 加速
- **人機協作**：設計理念注重迭代式模型建構，便於人工干預與調整
- **高級特性**：支持多時間序列建模、不確定性估計、正則化等

相較於傳統的 Prophet，Neural Prophet 在處理自迴歸和多時間序列方面提供了更強的能力，同時支持更複雜的模型結構，適合處理較高頻率、長期的時間序列數據。

### 1.2 適用場景

Neural Prophet 適用於多種時間序列預測場景，特別是在以下情況下表現出色：

1. **高頻率時間序列**：
   - 每小時、每分鐘或更高頻率的數據採集
   - 日內模式顯著的零售、能源、交通等領域數據

2. **具有多重季節性的數據**：
   - 同時存在日、週、月、年等多重週期性模式的數據
   - 電力消耗、網站流量、銷售額等具有複雜季節性的指標

3. **需要納入外部因素的預測**：
   - 受外部可預知事件影響的時間序列（如節假日、促銷活動）
   - 依賴於其他時間序列或已知未來因素的預測任務

4. **多時間序列協同建模**：
   - 多個相關產品的銷售預測
   - 多地區或多設備的同類指標預測

5. **需要不確定性量化的場景**：
   - 風險評估與決策支持
   - 預測區間與極端情景分析

6. **迭代改進的預測專案**：
   - 需要人工審核與調整的預測系統
   - 需要逐步完善模型的持續性預測任務

Neural Prophet 適合中長期預測（數小時至數年），對於極短期（幾分鐘內）或極長期（數十年）的預測可能需要結合其他專門工具。

## 2. Neural Prophet 模型原理

### 2.1 模型架構

Neural Prophet 採用模組化設計，將時間序列分解為多個可解釋的組件，同時使用神經網路增強特定部分的表達能力。其核心架構包括：

1. **趨勢組件 (Trend)**：
   - 建模時間序列的長期發展趨勢
   - 支持線性趨勢與分段線性趨勢（具有變點）
   - 可配置變點數量或自動變點檢測

2. **季節性組件 (Seasonality)**：
   - 使用傅立葉級數捕捉重複週期模式
   - 可同時建模多個季節性周期（年、月、週、日等）
   - 支持條件季節性（如特定季節僅在特定條件下出現）

3. **自迴歸模組 (AR-Net)**：
   - 建模目標變量的時間依賴關係
   - 基於神經網路實現，允許捕捉更複雜的模式
   - 可配置滯後期數與結構複雜度

4. **時間協變量 (Covariates)**：
   - **未來已知變量**：如節假日、促銷活動等已知未來值的變量
   - **滯後協變量**：外部影響因素的歷史觀測值
   - 均可透過線性層或神經網路進行建模

5. **事件模組 (Events)**：
   - 特殊事件的影響建模（如國家假日）
   - 自定義重複事件（如促銷、體育賽事）

全局架構可表示為：

```
y(t) = trend(t) + seasonality(t) + AR(y[t-1:t-n]) + future_regressors(t) + lagged_regressors([t-1:t-m]) + event_effects(t)
```

其中各組件可以是加法關係或乘法關係（透過 `seasonality_mode` 參數設置）。

### 2.2 模型訓練機制

Neural Prophet 利用 PyTorch 作為後端，實現端到端的模型訓練：

1. **損失函數**：
   - 默認使用均方誤差 (MSE) 作為損失函數
   - 支持分位數回歸進行不確定性估計
   - 可添加正則化項控制過擬合

2. **優化算法**：
   - 使用 Adam 優化器進行參數更新
   - 支持學習率調度與早停機制
   - 可配置批量大小與訓練輪次

3. **訓練流程**：
   - 資料預處理（標準化、缺失值處理等）
   - 時間窗口滑動進行自迴歸訓練
   - 模型擬合與參數更新
   - 驗證與早停判斷

4. **正則化技術**：
   - 各組件支持獨立正則化控制
   - 可用於控制模型複雜度與避免過擬合
   - 透過參數如 `seasonality_reg`、`trend_reg` 等設置

5. **全局模型**：
   - 支持多時間序列聯合建模
   - 允許組件參數共享或局部化
   - 實現 "全局+局部" 的混合參數化策略

### 2.3 與 Prophet 比較

Neural Prophet 在 Prophet 的基礎上進行了多項增強，同時保持了概念上的一致性：

| 特性 | Neural Prophet | Prophet |
|------|---------------|---------|
| 後端技術 | PyTorch (神經網路) | Stan (貝葉斯統計) |
| 自迴歸能力 | 原生支持 (AR-Net) | 不支持 |
| 外部因素 | 同時支持未來與滯後變量 | 僅支持未來已知變量 |
| 季節性 | 傅立葉項 | 傅立葉項 |
| 趨勢模型 | 分段線性，支持自動變點 | 分段線性，支持自動變點與飽和趨勢 |
| 不確定性估計 | 分位數回歸 | 貝葉斯抽樣 |
| 多時間序列 | 原生支持全局模型 | 需單獨建模 |
| 計算效率 | 通常更快且支持 GPU 加速 | CPU 計算，對大數據集較慢 |
| 正則化方式 | L1、L2 正則化 | 先驗尺度 |

Neural Prophet 以 `TorchProphet` 類提供了與 Prophet 相容的接口，便於現有 Prophet 用戶快速過渡與比較結果。

## 3. 數據準備與收集

### 3.1 數據要求與格式

Neural Prophet 對輸入數據有特定的格式要求，了解這些要求有助於正確準備數據：

1. **基本數據格式**：
   - 需要 Pandas DataFrame 格式
   - 必須包含兩個基本列：日期列 (`ds`) 與目標值列 (`y`)
   - 日期列需為 Pandas datetime 格式
   - 目標列為數值型，建議進行預處理以移除極端值

2. **時間頻率要求**：
   - 需要固定的時間間隔（如小時、日、週等）
   - 可以有缺失值，但過多缺失可能影響模型質量
   - 自迴歸模型對時間頻率要求更嚴格，應避免不規律間隔

3. **數據量建議**：
   - 至少包含兩個完整週期（如兩年數據）以充分捕捉季節性
   - 對於高頻數據，需要足夠的樣本量（如數千個數據點）
   - 數據越多，模型通常表現越好，特別是自迴歸部分

4. **額外變量**：
   - **未來變量**：與 `ds` 對齊的 DataFrame 列，包含已知未來值
   - **滯後變量**：與 `ds` 對齊的歷史觀察值，用於建立依賴關係
   - **事件數據**：特殊日期的標記，可通過 DataFrame 提供

5. **多時間序列格式**：
   - 需添加 ID 列標識不同時間序列
   - 預設列名為 'ID'，可自訂

### 3.2 數據前處理建議

為獲得最佳預測效果，推薦進行以下數據預處理步驟：

1. **數據清洗**：
   - 檢測並處理異常值（可使用統計方法或領域知識）
   - 確保時間戳的一致性與連續性
   - 移除或修正明顯錯誤的數據點

2. **缺失值處理**：
   - Neural Prophet 內建缺失值處理機制，主要通過線性插值與移動平均
   - 對關鍵時間點，建議事先進行更精確的缺失值處理
   - 自迴歸模型對缺失值更敏感，可考慮設置 `impute_missing=True`

3. **時間特徵工程**：
   - 考慮添加與時間相關的特徵（如月份、星期幾、是否假日等）
   - 識別特殊事件並準備事件數據表
   - 若存在明確的季節性變化，確保數據跨越足夠多的週期

4. **轉換與標準化**：
   - 考慮對非平穩時間序列進行轉換（如對數變換、差分）
   - Neural Prophet 預設會對 `y` 進行最小-最大標準化
   - 可通過 `normalize='standardize'` 選擇 Z-分數標準化
   - 外部變量預設會自動標準化（二元特徵除外）

5. **數據分割**：
   - 保留一部分最近數據作為測試集，評估模型預測能力
   - 使用 `NeuralProphet.split_df()` 方法進行時間序列切分
   - 考慮使用交叉驗證進行更穩健的評估

### 3.3 資料準備範例

以下是準備數據並載入 Neural Prophet 的基本流程：

```python
import pandas as pd
import numpy as np
from neuralprophet import NeuralProphet

# 載入數據
df = pd.read_csv('your_data.csv')

# 轉換時間格式
df['ds'] = pd.to_datetime(df['date_column'])
df = df[['ds', 'target_column']].rename(columns={'target_column': 'y'})

# 處理異常值（範例：移除極端值）
q_low = df['y'].quantile(0.001)
q_high = df['y'].quantile(0.999)
df = df[(df['y'] >= q_low) & (df['y'] <= q_high)]

# 準備外部變量（如果有）
df['special_event'] = df['ds'].apply(lambda x: 1 if x.month == 12 and x.day == 25 else 0)

# 建立事件資料框
holidays = pd.DataFrame({
    'holiday': 'chinese_new_year',
    'ds': pd.to_datetime(['2022-02-01', '2023-01-22', '2024-02-10']),
    'lower_window': -1,
    'upper_window': 1,
})

# 分割訓練/測試集
train_df = df[df['ds'] <= '2023-12-31']
test_df = df[df['ds'] > '2023-12-31']

# 初始化並訓練模型
m = NeuralProphet(
    seasonality_mode='multiplicative',
    yearly_seasonality=10,
    weekly_seasonality=True,
    daily_seasonality=False
)

# 添加特殊事件
m.add_events(['chinese_new_year'])
m.add_country_holidays(country_name='TW')

# 添加外部變量（如果有）
m.add_future_regressor('special_event')

# 擬合模型
metrics = m.fit(train_df, freq='D')
```

## 4. 模型配置與訓練

### 4.1 基本模型設置

Neural Prophet 提供了豐富的參數設置，讓用戶能夠根據具體問題靈活配置模型：

1. **初始化主要參數**：

```python
m = NeuralProphet(
    growth="linear",              # 趨勢類型：linear（線性）或 off（無趨勢）
    changepoints=None,            # 趨勢變點位置（自動或手動指定）
    n_changepoints=10,            # 自動檢測的變點數量
    changepoints_range=0.8,       # 尋找變點的時間範圍（0-1）
    trend_reg=0,                  # 趨勢正則化強度
    yearly_seasonality="auto",    # 年度季節性：auto, True, False 或具體傅立葉項數
    weekly_seasonality="auto",    # 週季節性
    daily_seasonality="auto",     # 日季節性
    seasonality_reg=0,            # 季節性正則化強度
    seasonality_mode="additive",  # 季節性模式：additive 或 multiplicative
)
```

2. **添加自迴歸組件**：

```python
m = NeuralProphet(
    n_lags=14,                    # 自迴歸滯後數量
    ar_reg=0.1,                   # 自迴歸正則化強度
    n_forecasts=1,                # 一次預測的步數
)
```

3. **配置神經網路結構**：

```python
m = NeuralProphet(
    n_hidden_layers=0,            # 隱藏層數量（0表示線性模型）
    d_hidden=None,                # 隱藏層維度
)
```

4. **設置訓練相關參數**：

```python
m = NeuralProphet(
    learning_rate=1.0,            # 學習率
    epochs=100,                   # 訓練輪次
    batch_size=32,                # 批量大小
    loss_func="MSE",              # 損失函數
    optimizer="AdamW",            # 優化器
)
```

5. **不確定性估計設置**：

```python
m = NeuralProphet(
    quantiles=[0.1, 0.5, 0.9],    # 預測分位數
)
```

### 4.2 添加組件與特性

Neural Prophet 支持多種組件的靈活添加：

1. **添加自定義季節性**：

```python
# 添加自定義季節性模式
m.add_seasonality(
    name='quarterly',             # 季節性名稱
    period=365.25/4,              # 週期長度（天）
    fourier_order=5               # 傅立葉項數量
)
```

2. **添加國家假日**：

```python
# 添加台灣假日
m.add_country_holidays(
    country_name='TW',           # 國家/地區代碼
    mode='additive'              # 假日效應模式
)
```

3. **添加自定義事件**：

```python
# 定義特殊事件
events_df = pd.DataFrame({
    'event': 'promotion',
    'ds': pd.to_datetime(['2023-01-15', '2023-02-20']),
    'lower_window': 0,           # 事件前影響天數
    'upper_window': 2,           # 事件後影響天數
})

# 添加事件到模型
m.add_events(
    ['promotion'],
    mode='multiplicative'
)
```

4. **添加未來已知變量**：

```python
# 添加未來可知的外部因素
m.add_future_regressor(
    'temperature',               # 變量名稱
    mode='multiplicative',       # 影響模式
    regularization=0.05          # 正則化強度
)
```

5. **添加滯後協變量**：

```python
# 添加滯後協變量（過去值會影響預測）
m.add_lagged_regressor(
    'web_traffic',               # 變量名稱
    n_lags=3,                    # 滯後期數
    regularization=0.1           # 正則化強度
)
```

### 4.3 訓練技巧與最佳實踐

要獲得最佳的 Neural Prophet 模型，可參考以下訓練技巧：

1. **模型複雜度選擇**：
   - 從簡單模型開始（如不使用隱藏層），逐步增加複雜度
   - 對於小數據集，優先使用線性模型避免過擬合
   - 僅在複雜性顯著提升效果時添加隱藏層

2. **調參策略**：
   - 優先調整基礎組件參數（如季節性、變點、正則化）
   - 使用交叉驗證尋找最佳參數設置
   - 逐步微調而非一次性大規模調整

3. **訓練加速技巧**：
   - 使用 GPU 加速訓練：`m = NeuralProphet(accelerator="gpu")`
   - 調整批量大小避免內存溢出
   - 使用早停機制：`m.fit(df, freq="D", early_stopping=True, early_stopping_patience=5)`

4. **處理長時間序列**：
   - 考慮增加變點數量捕捉更多趨勢變化
   - 使用更多傅立葉項捕捉複雜季節性
   - 調整訓練窗口適應數據特性

5. **避免過擬合**：
   - 使用適當的正則化強度 (`trend_reg`, `seasonality_reg`, `ar_reg`)
   - 減少隱藏層或降低複雜度
   - 監控訓練與驗證指標差距

6. **非平穩時間序列處理**：
   - 考慮對數轉換：`df['y'] = np.log(df['y'])`
   - 使用乘法季節性：`seasonality_mode="multiplicative"`
   - 考慮手動差分或使用自迴歸組件

完整訓練流程範例：

```python
# 初始化模型
m = NeuralProphet(
    yearly_seasonality=10,
    weekly_seasonality=5,
    daily_seasonality=False,
    seasonality_mode="multiplicative",
    n_changepoints=15,
    changepoint_range=0.9,
    trend_reg=0.1,
    seasonality_reg=0.5,
    n_lags=14,
    n_forecasts=7,
    learning_rate=0.01,
    epochs=200
)

# 添加組件
m.add_country_holidays(country_name="TW")
m.add_future_regressor('temperature')

# 設置交叉驗證
from neuralprophet.crossvalidation import CrossValidation
cv = CrossValidation(
    model=m,
    fold_pct=0.1,
    fold_overlap_pct=0.5,
    n_folds=3
)

# 執行交叉驗證
metrics = cv.cross_validate(df, freq="D", plotting_backend="plotly")

# 在完整數據上重新訓練最終模型
final_metrics = m.fit(df, freq="D", validation_df=valid_df)
```

## 5. 預測與結果解讀

### 5.1 生成預測

使用訓練好的 Neural Prophet 模型進行預測需要以下步驟：

1. **建立未來數據框**：

```python
# 建立未來30天的預測數據框
future = m.make_future_dataframe(
    df,
    periods=30,                  # 預測期數
    n_historic_predictions=True  # 包含歷史預測
)

# 如添加了未來變量，需提供這些變量值
future['temperature'] = future_temp_values
```

2. **進行預測**：

```python
# 生成預測結果
forecast = m.predict(future)
```

3. **獲取預測值**：

```python
# 查看預測結果（包含所有組件）
print(forecast.head())

# 僅查看預測與實際值
print(forecast[['ds', 'y', 'yhat1']])

# 若設置了分位數，查看預測區間
if hasattr(m, 'quantiles'):
    print(forecast[['ds', 'yhat1', 'yhat1_10', 'yhat1_90']])  # 10%和90%分位數
```

### 5.2 組件分解與可視化

Neural Prophet 的一大優勢是可將預測分解為各組件，便於理解與解釋：

1. **基本預測圖表**：

```python
# 繪製預測結果（含歷史數據與預測）
fig_forecast = m.plot(forecast)

# 若使用Plotly繪圖後端（更互動）
fig_forecast = m.plot(forecast, plotting_backend="plotly")
```

2. **分解組件圖表**：

```python
# 繪製各組件貢獻
fig_comp = m.plot_components(forecast)

# 查看特定組件如季節性
fig_comp = m.plot_components(forecast, components=["yearly", "weekly"])
```

3. **參數可視化**：

```python
# 查看模型參數與學習到的權重
fig_param = m.plot_parameters()

# 查看特定參數組
fig_param = m.plot_parameters(components=["trend"])
```

4. **自定義可視化**：

```python
import matplotlib.pyplot as plt

# 繪製預測區間
plt.figure(figsize=(10, 6))
plt.plot(forecast['ds'], forecast['yhat1'], label='預測值')
plt.fill_between(
    forecast['ds'],
    forecast['yhat1_10'],
    forecast['yhat1_90'],
    alpha=0.3,
    label='90% 預測區間'
)
plt.plot(forecast['ds'], forecast['y'], 'k.', label='實際值')
plt.legend()
plt.title('預測結果與不確定性')
plt.show()
```

### 5.3 模型評估與解讀

評估 Neural Prophet 模型和理解預測結果的關鍵步驟：

1. **性能指標分析**：

```python
# 訓練過程中的性能指標
print(metrics.tail())

# 使用自定義評估指標
from neuralprophet.metrics import performance_metrics
perf = performance_metrics(forecast, metrics=['mae', 'rmse', 'mape'])
print(perf)
```

2. **殘差診斷**：

```python
# 計算並繪製殘差
forecast['residual'] = forecast['y'] - forecast['yhat1']

plt.figure(figsize=(10, 6))
plt.plot(forecast['ds'], forecast['residual'], '.')
plt.axhline(y=0, color='r', linestyle='-')
plt.title('預測殘差')
plt.show()

# 檢查殘差分布
plt.figure(figsize=(8, 6))
plt.hist(forecast['residual'].dropna(), bins=50)
plt.title('殘差分布')
plt.show()
```

3. **組件貢獻理解**：

解讀各組件對預測的貢獻：
- **趨勢**：反映長期走勢，分析變點位置了解關鍵轉折
- **季節性**：分析不同週期（年、週、日）的模式強度與變化
- **事件效應**：評估特殊事件的影響程度與持續時間
- **自迴歸**：了解時間序列的記憶效應與依賴長度
- **外部變量**：量化外部因素的影響與相對重要性

4. **預測不確定性解讀**：

如果設置了分位數，可以解讀預測區間：
- 區間寬度反映預測不確定性大小
- 不同時間點的區間變化揭示何時預測更可靠或更不確定
- 實際值落在預測區間內的比例應接近設定的置信水平

5. **模型比較**：

```python
# 基準模型（如簡單時間序列模型）
from statsmodels.tsa.seasonal import seasonal_decompose
result = seasonal_decompose(df['y'], model='multiplicative')
result.plot()

# 與原始 Prophet 比較
from prophet import Prophet
prophet_model = Prophet()
prophet_model.fit(df)
prophet_forecast = prophet_model.predict(prophet_model.make_future_dataframe(periods=30))
```

### 5.4 結果應用與決策支持

Neural Prophet 預測結果可用於各類決策支持場景：

1. **確定性預測應用**：
   - 資源規劃與調度（如人員、庫存安排）
   - 預算制定與財務規劃
   - KPI 目標設定與監控

2. **預測區間的應用**：
   - 風險評估與極端情景分析
   - 容量規劃（考慮上限需求）
   - 安全庫存與緩衝設置

3. **組件分解的應用**：
   - 季節性分析用於優化營銷策略
   - 趨勢分析指導長期戰略決策
   - 事件影響評估改進促銷活動設計

4. **異常檢測**：
   - 利用預測區間識別異常值
   - 監控實際值與預測值差異作為預警系統

5. **假設情景模擬**：
   - 調整外部變量模擬不同情境
   - 使用學習的季節性和趨勢進行長期預測

## 6. 高級應用與最佳實踐

### 6.1 模型調優與優化

1. **超參數調優**：

```python
# 使用網格搜索優化參數
param_grid = {
    'n_changepoints': [5, 10, 20],
    'yearly_seasonality': [5, 10, 20],
    'learning_rate': [0.001, 0.01, 0.1]
}

# 使用交叉驗證
from neuralprophet.crossvalidation import CrossValidation

# 結果儲存
best_params = {}
best_mae = float('inf')

# 網格搜索
for n_cp in param_grid['n_changepoints']:
    for ys in param_grid['yearly_seasonality']:
        for lr in param_grid['learning_rate']:
            m = NeuralProphet(
                n_changepoints=n_cp,
                yearly_seasonality=ys,
                learning_rate=lr
            )
            
            cv = CrossValidation(m, fold_pct=0.1, n_folds=3)
            cv_results = cv.cross_validate(df, freq="D")
            mae = cv_results['mae'].mean()
            
            if mae < best_mae:
                best_mae = mae
                best_params = {'n_changepoints': n_cp, 'yearly_seasonality': ys, 'learning_rate': lr}

print(f"最佳參數: {best_params}, MAE: {best_mae}")
```

2. **特徵工程與選擇**：

```python
# 創建衍生特徵
df['day_of_week'] = df['ds'].dt.dayofweek
df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)

# 添加滯後特徵
for i in [1, 2, 3, 7]:
    df[f'lag_{i}'] = df['y'].shift(i)

# 添加移動平均特徵
df['ma7'] = df['y'].rolling(7).mean()
df['ma30'] = df['y'].rolling(30).mean()
```

3. **模型堆疊與組合**：

```python
# 訓練多個具有不同配置的模型
models = []
forecasts = []

# 不同配置
configs = [
    {'n_lags': 0, 'yearly_seasonality': 10},
    {'n_lags': 7, 'yearly_seasonality': 5},
    {'n_lags': 14, 'n_hidden_layers': 1}
]

# 訓練各個模型
for i, config in enumerate(configs):
    m = NeuralProphet(**config)
    metrics = m.fit(train_df, freq="D")
    models.append(m)
    
    # 生成預測
    future = m.make_future_dataframe(train_df, periods=30)
    forecast = m.predict(future)
    forecasts.append(forecast[['ds', 'yhat1']].rename(columns={'yhat1': f'yhat_{i}'}))

# 合併預測結果
combined = forecasts[0]
for i in range(1, len(forecasts)):
    combined = pd.merge(combined, forecasts[i], on='ds', how='left')

# 計算集成預測值（例如平均值）
combined['yhat_ensemble'] = combined[[f'yhat_{i}' for i in range(len(models))]].mean(axis=1)
```

### 6.2 多時間序列建模

Neural Prophet 支持共享參數的全局模型，適合處理相關的多時間序列：

1. **準備多時間序列數據**：

```python
# 準備具有ID列的多時間序列數據
df_multi = pd.DataFrame()

# 添加多個時間序列（例如不同產品或地區）
for i, product in enumerate(['A', 'B', 'C']):
    df_product = pd.DataFrame({
        'ds': pd.date_range('2020-01-01', '2023-01-01', freq='D'),
        'y': np.random.normal(loc=10*i, scale=1, size=1097) + np.sin(np.arange(1097)/7)*i,
        'ID': product
    })
    df_multi = pd.concat([df_multi, df_product])
```

2. **配置全局/局部參數**：

```python
# 初始化具有全局和局部組件的模型
m = NeuralProphet(
    n_forecasts=7,
    n_lags=14,
    yearly_seasonality=10,
    weekly_seasonality=5,
    global_normalization=True,
    global_trend=True,           # 共享趨勢
    global_seasonal=False,       # 單獨的季節性
    learning_rate=0.01
)

# 指定所有可能的 ID 值
m.set_ids(df_multi['ID'].unique())

# 訓練全局模型
metrics = m.fit(df_multi, freq='D')

# 預測
future = m.make_future_dataframe(df_multi, periods=30)
forecast = m.predict(future)
```

3. **檢查各時間序列預測**：

```python
# 查看各時間序列的預測結果
for id_value in df_multi['ID'].unique():
    forecast_id = forecast[forecast['ID'] == id_value]
    
    plt.figure(figsize=(10, 6))
    plt.scatter(forecast_id['ds'], forecast_id['y'], color='black', label='實際值')
    plt.plot(forecast_id['ds'], forecast_id['yhat1'], color='red', label='預測值')
    plt.title(f'時間序列 {id_value} 的預測結果')
    plt.legend()
    plt.show()
```

### 6.3 處理特定場景挑戰

1. **高波動數據處理**：

```python
# 對高波動數據使用對數轉換
df['y_log'] = np.log1p(df['y'])

# 訓練使用對數轉換後的數據
m = NeuralProphet(
    seasonality_mode="multiplicative",
    n_changepoints=25,           # 增加變點數量捕捉更多變化
    changepoint_range=0.95,      # 擴大變點搜索範圍
    yearly_seasonality=20,       # 增加傅立葉項以捕捉更細緻季節性
    weekly_seasonality=10,
    daily_seasonality=10
)

# 訓練模型
metrics = m.fit(df.rename(columns={'y_log': 'y'}), freq="D")

# 預測並還原轉換
forecast = m.predict(future)
forecast['yhat1_original'] = np.expm1(forecast['yhat1'])
```

2. **處理長期與短期季節性**：

```python
# 同時處理多種季節性
m = NeuralProphet()

# 添加各種週期性
m.add_seasonality(name='yearly', period=365.25, fourier_order=10)
m.add_seasonality(name='quarterly', period=365.25/4, fourier_order=5)
m.add_seasonality(name='monthly', period=30.5, fourier_order=3)
m.add_seasonality(name='weekly', period=7, fourier_order=3)
m.add_seasonality(name='daily', period=1, fourier_order=4)

# 增加頻率更高的季節性（例如小時週期）
m.add_seasonality(name='hourly', period=1/24, fourier_order=12)
```

3. **處理不規則間隔數據**：

```python
# 將不規則數據重採樣到固定頻率
df_irregular = pd.DataFrame({
    'ds': pd.to_datetime(['2023-01-01', '2023-01-02', '2023-01-05', '2023-01-10']),
    'y': [10, 12, 15, 11]
})

# 重採樣到固定頻率
df_regular = pd.DataFrame({
    'ds': pd.date_range(start=df_irregular['ds'].min(), 
                        end=df_irregular['ds'].max(), freq='D')
})
df_regular = df_regular.merge(df_irregular, on='ds', how='left')

# 填充缺失值（可選用更複雜的方法）
df_regular['y'].interpolate(method='linear', inplace=True)
```

## 7. 與其他工具比較與參考資源

### 7.1 Neural Prophet 與其他預測工具比較

Neural Prophet 與其他常用預測工具的優缺點對比：

| 工具 | 優點 | 缺點 | 適用場景 |
|-----|------|------|---------|
| Neural Prophet | 結合神經網路彈性與可解釋性<br>支持自迴歸<br>可視化組件<br>PyTorch後端加速 | 較新，文檔可能不夠完善<br>調參複雜度增加<br>需要一定數據量 | 具有複雜季節性與自相關性的中長期時間序列<br>需要解釋性的高頻數據 |
| Prophet | 可解釋性強<br>成熟穩定<br>易於使用<br>處理異常與缺失值能力強 | 無自迴歸支持<br>計算較慢<br>對高頻數據支持有限 | 有強季節性與趨勢的業務數據<br>具有異常值與缺失值的長期預測 |
| ARIMA/SARIMA | 統計基礎紮實<br>處理平穩時間序列效果好<br>預測區間有統計保證 | 需要平穩數據<br>不易擴展<br>不適合多變量分析 | 短期預測<br>簡單穩定的時間序列<br>統計推斷需求 |
| LSTM/GRU | 捕捉複雜非線性模式<br>處理長期依賴關係<br>支持多變量 | 黑盒模型<br>需要大量數據<br>可解釋性差 | 複雜非線性時間序列<br>長期依賴關係<br>大量數據可用 |
| XGBoost/LGBM | 處理非線性關係強<br>自動特徵選擇<br>訓練速度快 | 可解釋性較弱<br>不原生支持時間結構<br>需要手動特徵工程 | 特徵豐富的預測問題<br>不需要強解釋性<br>集成建模 |

### 7.2 使用場景選擇指南

在各種預測場景中選擇適合的工具：

1. **選擇 Neural Prophet 的場景**：
   - 需要兼顧彈性與可解釋性
   - 時間序列有明顯自相關性
   - 需要處理多重季節性與外部因素
   - 有一定計算資源與訓練數據量
   - 需要直觀組件可視化

2. **選擇 Prophet 的場景**：
   - 快速建模與基準線建立
   - 強調組件分解與解釋
   - 數據有異常值與缺失值
   - 非技術人員需要理解預測

3. **選擇統計方法的場景**：
   - 數據量較小但穩定
   - 需要嚴格統計推斷
   - 模型假設清晰明確
   - 計算資源有限

4. **選擇深度學習方法的場景**：
   - 大量訓練數據可用
   - 存在複雜非線性關係
   - 強調預測準確性而非解釋性
   - 有足夠計算資源

### 7.3 實用資源與參考

1. **官方資源**：
   - [Neural Prophet 官方文檔](https://neuralprophet.com/)
   - [GitHub 倉庫](https://github.com/ourownstory/neural_prophet)
   - [示例筆記本](https://github.com/ourownstory/neural_prophet/tree/main/examples)

2. **學習資源**：
   - [Neural Prophet 論文](https://arxiv.org/abs/2111.15397)
   - [PyTorch 時間序列教程](https://pytorch.org/tutorials/beginner/basics/intro.html)
   - [時間序列分析基礎](https://otexts.com/fpp3/)

3. **相關工具與庫**：
   - [PyTorch](https://pytorch.org/)
   - [Facebook Prophet](https://facebook.github.io/prophet/)
   - [pandas](https://pandas.pydata.org/)
   - [sktime](https://www.sktime.org/)

4. **討論社區**：
   - [Neural Prophet Slack 社區](https://join.slack.com/t/neuralprophet/shared_invite/zt-sgme2rw3-3dCH3YJ_wgg01IXHoYaeCg)
   - [GitHub Discussions](https://github.com/ourownstory/neural_prophet/discussions)
   - [Stack Overflow](https://stackoverflow.com/questions/tagged/neuralprophet)

---

Neural Prophet 結合了傳統時間序列分析的可解釋性與神經網路的彈性，為時間序列預測提供了強大而靈活的解決方案。本指引涵蓋了從基礎概念到高級應用的各個方面，幫助您快速上手並有效應用這一工具。隨著實踐經驗的積累，您可以逐步探索更多高級特性，以充分發揮 Neural Prophet 的潛力。
