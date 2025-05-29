正在獲取 AAPL 從 2015-01-01 到 2025-01-01 的歷史數據...
YF.download() has changed argument auto_adjust default to True
[*********************100%***********************]  1 of 1 completed
數據獲取成功！
Price           Close       High  ...       Open     Volume
Date                              ...                      
2015-01-02  24.288576  24.757330  ...  24.746222  212818400
2015-01-05  23.604334  24.137514  ...  24.057537  257142000
2015-01-06  23.606552  23.866477  ...  23.668756  263188400
2015-01-07  23.937569  24.037539  ...  23.815381  160423600
2015-01-08  24.857311  24.915073  ...  24.266371  237458000

[5 rows x 5 columns]
Price            Close        High  ...        Open    Volume
Date                                ...                      
2024-12-24  257.578674  257.588630  ...  254.875189  23234700
2024-12-26  258.396667  259.474086  ...  257.568678  27237100
2024-12-27  254.974930  258.077462  ...  257.209530  42355300
2024-12-30  251.593094  252.889969  ...  251.623020  35557500
2024-12-31  249.817383  252.670501  ...  251.832526  39480700

[5 rows x 5 columns]

模擬情緒數據的一部分：
Price           Close  Price_Change  Sentiment
Date                                          
2015-01-02  24.288576           NaN   0.565699
2015-01-05  23.604334     -0.684242   0.559035
2015-01-06  23.606552      0.002218  -0.995701
2015-01-07  23.937569      0.331017  -0.177628
2015-01-08  24.857311      0.919743   0.930955
Price            Close  Price_Change  Sentiment
Date                                           
2024-12-24  257.578674      2.922958   0.999164
2024-12-26  258.396667      0.817993   1.000000
2024-12-27  254.974930     -3.421738   0.999779
2024-12-30  251.593094     -3.381836  -1.000000
2024-12-31  249.817383     -1.775711  -1.000000

情緒數據統計：
平均值: 0.0690
標準差: 0.8842
最小值: -1.0000
最大值: 1.0000
移除缺失值前: 2516 行
移除缺失值後: 2483 行
移除了 33 行數據

最終特徵數據集 (部分欄位)：
Price           Close  Sentiment  ...  Sentiment_MA_5  Target
Date                              ...                        
2015-02-20  28.883059  -0.521842  ...        0.513987       1
2015-02-23  29.663681   0.111057  ...        0.352023       0
2015-02-24  29.478559   0.999561  ...        0.378710       0
2015-02-25  28.724707  -0.949501  ...        0.005559       1
2015-02-26  29.088251  -0.999649  ...       -0.272075       0

[5 rows x 7 columns]
Price            Close  Sentiment  ...  Sentiment_MA_5  Target
Date                               ...                        
2024-12-24  257.578674   0.999164  ...        0.599833       1
2024-12-26  258.396667   1.000000  ...        0.599833       0
2024-12-27  254.974930   0.999779  ...        0.999789       0
2024-12-30  251.593094  -1.000000  ...        0.599789       0
2024-12-31  249.817383  -1.000000  ...        0.199789       0

[5 rows x 7 columns]

特徵維度: (2483, 37)
目標維度: (2483,)
特徵列名: ['Sentiment', 'Close_Lag1', 'Open_Lag1', 'High_Lag1', 'Low_Lag1', 'MA_5', 'MA_10', 'MA_20', 'Close_Vol_5', 'Daily_Range', 'Daily_Range_Lag1', 'Volume_Lag1', 'Volume_MA_5', 'Sentiment_Lag1', 'Sentiment_MA_5', 'Sentiment_Change_1d', 'RSI_14', 'MACD_12_26_9', 'MACDh_12_26_9', 'MACDs_12_26_9', 'BBL_20_2.0', 'BBM_20_2.0', 'BBU_20_2.0', 'BBB_20_2.0', 'BBP_20_2.0', 'STOCHk_14_3_3', 'STOCHd_14_3_3', 'WILLR_14', 'Price_Position_BB', 'Price_MA_Ratio_5', 'Price_MA_Ratio_20', 'Volume_Price_Trend', 'DayOfWeek', 'Month', 'Quarter', 'IsMonthEnd', 'IsQuarterEnd']

訓練集大小: 1981 樣本
測試集大小: 502 樣本
訓練集時間範圍: 2015-02-20 00:00:00 到 2022-12-30 00:00:00
測試集時間範圍: 2023-01-03 00:00:00 到 2024-12-31 00:00:00

訓練集目標分佈: 下跌 (0): 948, 上漲 (1): 1033
測試集目標分佈: 下跌 (0): 220, 上漲 (1): 282

開始超參數優化...
Fitting 3 folds for each of 50 candidates, totalling 150 fits
最佳參數: {'subsample': 0.9, 'num_leaves': 100, 'n_estimators': 300, 'min_child_samples': 20, 'max_depth': 7, 'learning_rate': 0.2, 'colsample_bytree': 0.8}
最佳CV分數 (ROC-AUC): 0.510681833879071

=== 模型評估結果 ===
訓練集準確率: 1.0000
測試集準確率: 0.4582
訓練集 ROC-AUC: 1.0000
測試集 ROC-AUC: 0.5250

測試集詳細分類報告:
              precision    recall  f1-score   support

           0       0.44      0.85      0.58       220
           1       0.57      0.15      0.24       282

    accuracy                           0.46       502
   macro avg       0.50      0.50      0.41       502
weighted avg       0.51      0.46      0.39       502


模型已保存至: /Users/aaron/Projects/DataScout/data/models/lightgbm_stock_model.pkl

前10重要特徵:
                feature  importance
9           Daily_Range         353
14       Sentiment_MA_5         319
12          Volume_MA_5         318
29     Price_MA_Ratio_5         307
31   Volume_Price_Trend         299
11          Volume_Lag1         299
0             Sentiment         280
15  Sentiment_Change_1d         280
8           Close_Vol_5         280
23           BBB_20_2.0         279

=== 回測分析 ===
買入持有策略總收益: 1.0233 (102.33%)
機器學習策略總收益: 0.3213 (32.13%)
買入持有策略年化波動率: 0.2135
機器學習策略年化波動率: 0.1028
買入持有策略夏普比率: 1.7673
機器學習策略夏普比率: 1.4139
買入持有策略最大回撤: -0.1661 (-16.61%)
機器學習策略最大回撤: -0.0884 (-8.84%)

=== 未來預測 ===
基於最新數據預測明日趨勢:
預測結果: 上漲
上漲概率: 0.7031
預測信心度: 高

=== 分析完成 ===
所有輸出文件已保存至 /Users/aaron/Projects/DataScout/data/output/
模型文件已保存至 /Users/aaron/Projects/DataScout/data/models/

注意: 此模型僅供學習和研究用途，不構成投資建議。實際投資需謹慎考慮風險。
aaron@AarondeMacBook-Air forcasting % cd /Users/aaron/Project
s/DataScout/forcasting && python demo.py
🚀 股價預測系統演示
==================================================
可用的演示:
  1: 基本用法
  2: 步驟化使用
  3: 多股票預測
  4: 自定義配置
  5: 模型持久化
  all: 運行所有演示

請選擇要運行的演示 (默認: 1): all

==================== 基本用法 ====================
=== 基本用法演示 ===
2025-05-29 10:50:12,680 - StockPredictor - INFO - 開始運行完整的股價預測流程...
2025-05-29 10:50:12,683 - StockPredictor - INFO - 正在獲取 AAPL 從 2015-01-01 到 2025-01-01 的數據...
YF.download() has changed argument auto_adjust default to True
[*********************100%***********************]  1 of 1 completed
2025-05-29 10:50:13,321 - StockPredictor - INFO - 成功獲取 2516 行數據
2025-05-29 10:50:13,321 - StockPredictor - INFO - 開始特徵工程...
2025-05-29 10:50:13,358 - StockPredictor - ERROR - 流程執行失敗: Cannot set a DataFrame with multiple columns to the single column Volume_Price_Trend
演示 基本用法 失敗: Cannot set a DataFrame with multiple columns to the single column Volume_Price_Trend

==================== 步驟化使用 ====================

=== 步驟化使用演示 ===
1. 獲取數據...
2025-05-29 10:50:13,361 - StockPredictor - INFO - 正在獲取 MSFT 從 2015-01-01 到 2025-01-01 的數據...
[*********************100%***********************]  1 of 1 completed
2025-05-29 10:50:13,695 - StockPredictor - INFO - 成功獲取 2516 行數據
獲取了 2516 行數據
2. 特徵工程...
2025-05-29 10:50:13,696 - StockPredictor - INFO - 開始特徵工程...
演示 步驟化使用 失敗: Cannot set a DataFrame with multiple columns to the single column Volume_Price_Trend

==================== 多股票預測 ====================

=== 多股票預測演示 ===

正在處理 AAPL...
2025-05-29 10:50:13,724 - StockPredictor - INFO - 開始運行完整的股價預測流程...
2025-05-29 10:50:13,724 - StockPredictor - INFO - 正在獲取 AAPL 從 2015-01-01 到 2025-01-01 的數據...
[*********************100%***********************]  1 of 1 completed
2025-05-29 10:50:13,755 - StockPredictor - INFO - 成功獲取 2516 行數據
2025-05-29 10:50:13,755 - StockPredictor - INFO - 開始特徵工程...
2025-05-29 10:50:13,776 - StockPredictor - ERROR - 流程執行失敗: Cannot set a DataFrame with multiple columns to the single column Volume_Price_Trend
處理 AAPL 時出錯: Cannot set a DataFrame with multiple columns to the single column Volume_Price_Trend

正在處理 GOOGL...
2025-05-29 10:50:13,777 - StockPredictor - INFO - 開始運行完整的股價預測流程...
2025-05-29 10:50:13,777 - StockPredictor - INFO - 正在獲取 GOOGL 從 2015-01-01 到 2025-01-01 的數據...
[*********************100%***********************]  1 of 1 completed
2025-05-29 10:50:14,084 - StockPredictor - INFO - 成功獲取 2516 行數據
2025-05-29 10:50:14,084 - StockPredictor - INFO - 開始特徵工程...
2025-05-29 10:50:14,172 - StockPredictor - ERROR - 流程執行失敗: Cannot set a DataFrame with multiple columns to the single column Volume_Price_Trend
處理 GOOGL 時出錯: Cannot set a DataFrame with multiple columns to the single column Volume_Price_Trend

正在處理 MSFT...
2025-05-29 10:50:14,174 - StockPredictor - INFO - 開始運行完整的股價預測流程...
2025-05-29 10:50:14,174 - StockPredictor - INFO - 正在獲取 MSFT 從 2015-01-01 到 2025-01-01 的數據...
[*********************100%***********************]  1 of 1 completed
2025-05-29 10:50:14,203 - StockPredictor - INFO - 成功獲取 2516 行數據
2025-05-29 10:50:14,203 - StockPredictor - INFO - 開始特徵工程...
2025-05-29 10:50:14,224 - StockPredictor - ERROR - 流程執行失敗: Cannot set a DataFrame with multiple columns to the single column Volume_Price_Trend
處理 MSFT 時出錯: Cannot set a DataFrame with multiple columns to the single column Volume_Price_Trend

正在處理 TSLA...
2025-05-29 10:50:14,225 - StockPredictor - INFO - 開始運行完整的股價預測流程...
2025-05-29 10:50:14,225 - StockPredictor - INFO - 正在獲取 TSLA 從 2015-01-01 到 2025-01-01 的數據...
[*********************100%***********************]  1 of 1 completed
2025-05-29 10:50:14,568 - StockPredictor - INFO - 成功獲取 2516 行數據
2025-05-29 10:50:14,568 - StockPredictor - INFO - 開始特徵工程...
2025-05-29 10:50:14,589 - StockPredictor - ERROR - 流程執行失敗: Cannot set a DataFrame with multiple columns to the single column Volume_Price_Trend
處理 TSLA 時出錯: Cannot set a DataFrame with multiple columns to the single column Volume_Price_Trend

==================== 自定義配置 ====================

=== 自定義配置演示 ===
使用自定義配置運行...
2025-05-29 10:50:14,591 - StockPredictor - INFO - 開始運行完整的股價預測流程...
2025-05-29 10:50:14,591 - StockPredictor - INFO - 正在獲取 NVDA 從 2020-01-01 到 2024-12-31 的數據...
[*********************100%***********************]  1 of 1 completed
2025-05-29 10:50:14,974 - StockPredictor - INFO - 成功獲取 1257 行數據
2025-05-29 10:50:14,974 - StockPredictor - INFO - 開始特徵工程...
2025-05-29 10:50:14,991 - StockPredictor - ERROR - 流程執行失敗: Cannot set a DataFrame with multiple columns to the single column Volume_Price_Trend
演示 自定義配置 失敗: Cannot set a DataFrame with multiple columns to the single column Volume_Price_Trend

==================== 模型持久化 ====================

=== 模型持久化演示 ===
訓練新模型...
2025-05-29 10:50:14,992 - StockPredictor - INFO - 開始運行完整的股價預測流程...
2025-05-29 10:50:14,992 - StockPredictor - INFO - 正在獲取 AAPL 從 2015-01-01 到 2025-01-01 的數據...
[*********************100%***********************]  1 of 1 completed
2025-05-29 10:50:15,035 - StockPredictor - INFO - 成功獲取 2516 行數據
2025-05-29 10:50:15,035 - StockPredictor - INFO - 開始特徵工程...
2025-05-29 10:50:15,057 - StockPredictor - ERROR - 流程執行失敗: Cannot set a DataFrame with multiple columns to the single column Volume_Price_Trend
演示 模型持久化 失敗: Cannot set a DataFrame with multiple columns to the single column Volume_Price_Trend

==================================================
演示完成! 🎉

📊 查看輸出文件:
  - 圖表: /Users/aaron/Projects/DataScout/data/output/
  - 模型: /Users/aaron/Projects/DataScout/data/models/
  - 日誌: /Users/aaron/Projects/DataScout/data/output/stock_prediction.log

⚠️  免責聲明:
此系統僅供學習研究用途，不構成投資建議。
實際投資需謹慎考慮風險。