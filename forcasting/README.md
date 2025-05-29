# 股價預測系統

基於 LightGBM 的專業股價預測系統，適用於量化交易研究和機器學習實踐。

## 功能特點

- 🚀 **自動化數據獲取**：使用 yfinance 獲取實時股價數據
- 🔧 **智能特徵工程**：包含技術指標、滯後特徵、滾動統計等
- 🤖 **機器學習預測**：使用 LightGBM 進行二元分類預測
- 📊 **完整評估體系**：準確率、ROC AUC、特徵重要性等
- 💰 **回測分析**：完整的交易策略回測和績效評估
- 🎯 **風險管理**：內置風險控制和信心度評估

## 項目結構

```
forcasting/
├── stock_predictor.py    # 主程式（面向對象版本）
├── lightgbm.py          # 原始腳本版本
├── config.py            # 配置文件
├── utils.py             # 工具函數
├── requirements.txt     # 依賴包列表
└── README.md           # 說明文件
```

## 安裝依賴

```bash
pip install -r requirements.txt
```

## 快速開始

### 方法一：使用專業版本（推薦）

```python
from stock_predictor import StockPredictor

# 創建預測器
predictor = StockPredictor()

# 運行完整流程
results = predictor.run_full_pipeline(
    symbol='AAPL',
    optimize_params=False
)
```

### 方法二：運行原始腳本

```bash
python lightgbm.py
```

### 方法三：步驟化使用

```python
from stock_predictor import StockPredictor

predictor = StockPredictor()

# 1. 獲取數據
predictor.fetch_data('AAPL')

# 2. 特徵工程
predictor.engineer_features()

# 3. 準備特徵
predictor.prepare_features()

# 4. 分割數據
X_train, X_test, y_train, y_test = predictor.split_data()

# 5. 訓練模型
predictor.train_model(X_train, y_train)

# 6. 評估模型
results = predictor.evaluate_model(X_test, y_test)

# 7. 回測分析
backtest_results, metrics = predictor.run_backtest()

# 8. 預測未來
predictions = predictor.predict_future()
```

## 配置參數

可以通過修改 `config.py` 來調整各種參數：

```python
# 股票配置
STOCK_CONFIG = {
    'default_symbol': 'AAPL',
    'start_date': '2015-01-01',
    'end_date': '2025-01-01',
    'split_date': '2023-01-01'
}

# 模型配置
MODEL_CONFIG = {
    'lightgbm_params': {
        'objective': 'binary',
        'metric': 'binary_logloss',
        'num_leaves': 31,
        'learning_rate': 0.1,
        # ... 其他參數
    }
}
```

## 輸出文件

運行後會在以下位置生成輸出文件：

```
data/
├── output/
│   ├── confusion_matrix.png      # 混淆矩陣圖
│   ├── roc_curve.png            # ROC 曲線圖
│   ├── feature_importance.png   # 特徵重要性圖
│   ├── backtest_results.png     # 回測結果圖
│   ├── backtest_results.csv     # 回測數據
│   ├── feature_importance.csv   # 特徵重要性數據
│   └── stock_prediction.log     # 日誌文件
└── models/
    ├── lightgbm_stock_predictor.pkl  # 訓練好的模型
    └── feature_names.pkl            # 特徵名稱列表
```

## 主要特徵

### 價格特徵
- 滯後價格（1-5 天）
- 移動平均（5, 10, 20 天）
- 價格變化率
- 日內幅度

### 技術指標
- RSI（相對強弱指數）
- MACD（移動平均聚散指標）
- 布林帶
- 隨機指標（KD）
- 威廉指標

### 成交量特徵
- 滯後成交量
- 成交量移動平均
- 成交量價格趨勢

### 時間特徵
- 星期幾
- 月份
- 季度
- 月末/季末標記

### 情緒特徵（模擬）
- 基於價格變化的模擬情緒指標
- 情緒滯後值
- 情緒移動平均

## 模型評估指標

- **準確率**：預測正確的比例
- **ROC AUC**：接收者操作特徵曲線下面積
- **精確率/召回率**：分類質量評估
- **特徵重要性**：各特徵對預測的貢獻度

## 回測績效指標

- **總收益率**：策略總體收益
- **年化收益率**：年化後的收益率
- **夏普比率**：風險調整後收益
- **最大回撤**：最大虧損幅度
- **勝率**：獲利交易佔比

## 注意事項

⚠️ **重要聲明**：

1. 此系統僅供學習和研究用途
2. 不構成任何投資建議
3. 實際投資需謹慎考慮風險
4. 歷史數據不代表未來表現
5. 建議在使用前充分了解相關風險

## 自定義擴展

### 添加新的股票代號

```python
predictor.run_full_pipeline(symbol='TSLA')  # 特斯拉
predictor.run_full_pipeline(symbol='GOOGL') # 谷歌
```

### 調整預測時間範圍

```python
# 修改 config.py 中的日期設置
STOCK_CONFIG = {
    'start_date': '2020-01-01',  # 較短的訓練期間
    'split_date': '2024-01-01'   # 較近的分割點
}
```

### 添加新的技術指標

在 `utils.py` 的 `FeatureEngineer` 類中添加：

```python
def create_custom_indicators(self, df):
    # 添加自定義技術指標
    df.ta.cci(high='High', low='Low', close='Close', length=20, append=True)
    df.ta.atr(high='High', low='Low', close='Close', length=14, append=True)
    return df
```

## 故障排除

### 常見問題

1. **數據獲取失敗**
   - 檢查網絡連接
   - 確認股票代號正確
   - 檢查日期範圍設置

2. **模型訓練緩慢**
   - 減少數據範圍
   - 關閉超參數優化
   - 減少特徵數量

3. **圖片無法顯示**
   - 確保有 GUI 環境
   - 檢查 matplotlib 配置
   - 圖片已保存到文件中

## 技術支持

如有問題或建議，請參考：

- 查看日誌文件：`data/output/stock_prediction.log`
- 檢查數據質量和特徵分佈
- 調整模型參數和特徵工程方法

## 更新日誌

### v2.0.0 (2025-01-29)
- 重構為面向對象架構
- 添加完整的回測系統
- 增強特徵工程能力
- 改進模型評估方法
- 添加配置管理系統

### v1.0.0 (2025-01-01)
- 初始版本
- 基礎 LightGBM 預測功能
- 簡單特徵工程
- 基本評估指標
