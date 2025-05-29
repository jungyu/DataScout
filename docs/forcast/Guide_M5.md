# M5 Forecasting Competition 學習指南

## 目錄

1. [關於本指南](#關於本指南)
2. [競賽綜覽](#競賽綜覽)
3. [核心挑戰解析](#核心挑戰解析)
4. [學習資源指南](#學習資源指南)
5. [系統化學習路徑](#系統化學習路徑)
6. [SOTA 方法解析](#sota-方法解析)
7. [算法比較表](#算法比較表)
8. [高級主題](#高級主題)

## 關於本指南

此指南針對想要深入學習時間序列預測的開發者與研究者，以 M5 Forecasting Competition 為核心學習案例。本指南提供完整的學習路徑、資源推薦和實戰策略。

**適合對象**：

- 機器學習工程師
- 數據科學家
- 時間序列預測研究者
- 競賽愛好者

**學習目標**：

- 掌握大規模層次性時間序列預測
- 理解 SOTA 方法的核心技術
- 具備實際項目開發能力

---

## 競賽綜覽

### 競賽背景

M5 Forecasting Competition 是時間序列預測領域的重要競賽，於 2020 年在 Kaggle 平台舉辦。競賽由國際預測學會 (International Institute of Forecasters) 主辦，旨在推進預測方法的發展。

### 數據特點

- **數據來源**：Walmart 真實銷售數據
- **時間跨度**：2011年1月29日至2016年6月19日（1913天）
- **預測目標**：預測未來28天的日銷售量
- **評估指標**：WRMSSE (Weighted Root Mean Squared Scaled Error) 和 RMSSE

### M5 會議與學術影響

M5 競賽促成了時間序列預測領域的重要學術發展，產生了大量高質量研究成果。

---

## 核心挑戰解析

### 1. 大規模層次性結構

- **42,840 個底層時間序列**：每個代表特定商品在特定商店的日銷售量
- **層次性結構**：從單一商品到總體銷售的12層聚合結構
- **約束條件**：下層預測聚合必須等於上層預測

### 2. 豐富的相關特徵

- **歷史銷售數據**：1,913 天的日銷售記錄
- **價格信息**：商品價格變化記錄
- **日曆特徵**：節假日、特殊事件等時間相關信息
- **靜態特徵**：商品類別、商店信息、地理位置等

### 3. 複雜的數據特性

- **間歇性需求**：大量零銷售和不規則購買模式
- **多重季節性**：週級、月級、年級等多個時間週期
- **促銷效應**：價格變動對銷售的影響
- **層次依賴**：不同層次間的複雜相關性

### 4. 特殊的評估指標

- **WRMSSE**：考慮了時間序列層次結構和不同序列重要性的加權評估
- **尺度不變性**：消除了不同時間序列間尺度差異的影響
- **健壯性**：對異常值和間歇性需求具有較好的抗干擾能力

---

## 學習資源指南

### 1. 學術文獻深度研究 📚

#### International Journal of Forecasting (IJF) 特刊

**核心論文清單**：

- **"The M5 Accuracy competition: Results, findings and conclusions"** - Makridakis et al.
- **"The M5 uncertainty competition: Results, findings and conclusions"** - Makridakis et al.
- **"Hierarchical forecasting at scale"** - Olivares et al.
- **"Demand forecasting with deep learning and ensemble methods"** - Arora et al.
- **"M5 forecasting: Lessons learned and future directions"** - Petropoulos et al.

**學術搜索策略**：

- 在 ScienceDirect 搜尋：`"M5 Competition" AND "forecasting"`
- 在 Google Scholar 搜尋：`"M5 forecasting" OR "Walmart sales prediction"`
- 關注 International Journal of Forecasting 期刊的相關專輯

#### 頂級會議與前沿研究

**重要學術會議**：

- **International Symposium on Forecasting (ISF)**：年度預測領域頂級會議
- **ICML/NeurIPS 時間序列workshop**：機器學習在時間序列的應用
- **ICLR 時間序列相關論文**：深度學習最新進展
- **KDD 時間序列track**：工業應用導向的研究

### 2. Kaggle 平台深度資源 🏆

#### 競賽頁面完整探索

| 頁面 | 重點內容 | 學習建議 |
|------|----------|----------|
| **Overview** | 競賽背景、任務定義 | 理解商業問題本質 |
| **Data** | 數據結構、特徵說明 | 熟悉數據schema |
| **Evaluation** | WRMSSE 計算公式、權重機制 | 手動實現評估指標 |
| **Timeline** | 競賽階段、關鍵日期 | 理解數據切分邏輯 |

#### 頂級解決方案深度解析

**第一名解決方案 - Uber Technologies**：

- **核心架構**：遞歸神經網路 + 特徵工程 + 層次協調
- **創新點**：深度學習與傳統機器學習的有效結合
- **關鍵洞察**：不同商品類別需要不同的建模策略

**第二名解決方案 - LYFT**：

- **核心架構**：LightGBM ensemble + 智能特徵選擇
- **創新點**：高效的時序交叉驗證框架
- **技術亮點**：基於業務邏輯的特徵設計

#### 精選 Kaggle Notebooks

**探索分析類（EDA）**：

- `"M5 EDA and baseline"` by Chris Deotte
- `"Walmart sales comprehensive EDA"`
- `"Calendar effects and seasonality"`

**特徵工程類**：

- `"M5 feature engineering guide"`
- `"Advanced lag features for M5"`
- `"Price and promotion analysis"`

**模型實現類**：

- `"LightGBM baseline with feature engineering"`
- `"XGBoost advanced parameter tuning"`
- `"LSTM for time series forecasting"`

### 3. 開源工具與庫詳解 🛠️

#### 主流機器學習框架

##### LightGBM

```python
import lightgbm as lgb

# M5 專用配置
params = {
    'objective': 'regression',
    'metric': 'rmse',
    'boosting_type': 'gbdt',
    'num_leaves': 31,
    'learning_rate': 0.05,
    'feature_fraction': 0.9,
    'bagging_fraction': 0.8,
    'bagging_freq': 5,
    'verbose': 0
}
```

**關鍵優勢**：

- **速度性能**：比 XGBoost 快 10 倍以上
- **記憶體效率**：處理大規模特徵集合
- **類別特徵**：原生支持，無需編碼
- **並行化**：高效的特徵並行和數據並行

##### XGBoost

```python
import xgboost as xgb

xgb_params = {
    'max_depth': 6,
    'eta': 0.1,
    'subsample': 0.8,
    'colsample_bytree': 0.8,
    'objective': 'reg:squarederror'
}
```

**與 LightGBM 的差異**：

- **穩定性**：在某些情況下更加穩定
- **調參空間**：更多的超參數選項
- **社群支持**：更成熟的生態系統

#### 專業時間序列工具

##### MLForecast

```python
from mlforecast import MLForecast
from mlforecast.lag_transforms import RollingMean

fcst = MLForecast(
    models={'lgb': LGBMRegressor()},
    freq='D',
    lags=[7, 14, 21, 28],
    lag_transforms={7: [RollingMean(window_size=7)]}
)
```

**核心優勢**：

- **自動化特徵工程**：滯後特徵、滾動統計自動生成
- **大規模處理**：高效處理數萬個時間序列
- **內置變換**：差分、標準化等預處理自動化
- **並行計算**：多核心並行加速

##### HierarchicalForecast

```python
from hierarchicalforecast import HierarchicalReconciliation
from hierarchicalforecast.methods import BottomUp, MinTrace

reconciler = HierarchicalReconciliation(
    reconcilers=[BottomUp(), MinTrace()]
)
```

**專業功能**：

- **多種協調方法**：Bottom-up, Top-down, MinTrace, Optimal
- **約束保證**：確保層次一致性
- **性能優化**：大規模層次結構高效處理
- **靈活配置**：支持複雜層次結構定義

### 4. 實踐學習資源 💻

#### GitHub 開源項目

1. **M5-Competition-Solutions**
   - 內容：各種獲獎方案的完整實現
   - 價值：學習不同技術路線

2. **Time-Series-Forecasting-Collections**
   - 內容：時間序列預測算法的系統性實現
   - 適用：算法比較和基準測試

3. **Hierarchical-Forecasting-Tutorials**
   - 內容：層次性預測的理論與實踐教程
   - 重點：理解層次性預測理論

#### 在線課程與教程

**Coursera 課程**：

- "Time Series Analysis and Forecasting" - 基礎理論
- "Machine Learning for Trading" - 實踐應用

**YouTube 資源**：

- **Rob Hyndman's Channel**：時間序列預測專家講座
- **Kaggle Learn 頻道**：官方教程

#### 實踐項目建議

1. **複現第一名方案**：理解端到端流程
2. **自建特徵工程管道**：提升工程能力
3. **算法性能基準測試**：深化演算法理解
4. **層次預測方法比較**：比較不同協調方法

### 5. 理論基礎強化 📖

#### 必讀經典書籍

##### 《Forecasting: Principles and Practice》(FPP3)

- **作者**：Rob Hyndman & George Athanasopoulos
- **在線免費**：<https://otexts.com/fpp3/>
- **M5 相關章節**：第9章(ARIMA)、第10章(動態回歸)、第11章(層次預測)
- **實用性**：豐富的R代碼示例

##### 《The Elements of Statistical Learning》

- **價值**：機器學習理論基礎
- **相關章節**：決策樹、提升算法、交叉驗證

##### 《Pattern Recognition and Machine Learning》

- **重點**：貝葉斯方法、不確定性量化
- **應用**：理解預測區間的計算

#### 核心概念深化

**時間序列分析**：

- **平穩性**：ADF 檢驗、差分變換
- **自相關**：ACF/PACF 分析、滯後選擇
- **季節性**：季節分解、STL 分解

**機器學習**：

- **交叉驗證**：時間序列特有的驗證策略
- **特徵選擇**：避免過擬合的特徵篩選
- **超參數調優**：時間序列場景下的調參策略

**評估指標**：

- **MASE**：平均絕對標度誤差
- **WRMSSE**：加權均方根標度誤差
- **預測區間**：不確定性量化方法

### 學習資源使用策略

#### 初學者路線

1. **理論基礎** → FPP3 前6章
2. **實踐入門** → Kaggle EDA notebooks
3. **技能建設** → 複現簡單方案
4. **進階學習** → 研讀獲獎方案

#### 進階者路線

1. **深度方案分析** → IJF 特刊論文
2. **技術創新** → 改進現有方法
3. **工具開發** → 構建自己的工具庫
4. **貢獻開源** → 改進現有實現

---

## 系統化學習路徑

### 階段一：基礎認知 (1-2週)

#### 1. 競賽背景研習

- 閱讀 M5 競賽頁面的所有信息
- 理解評估指標 WRMSSE 的計算方法
- 分析數據結構和層次性關係

#### 2. 數據探索實踐

- 運行高評價的 EDA Notebooks
- 親自分析數據分佈和特性
- 識別關鍵的數據模式

### 階段二：基礎建模 (2-3週)

#### 3. 簡單模型構建

- 使用基本特徵（時間戳、簡單滯後）訓練 LightGBM/XGBoost
- 實現基礎的交叉驗證框架
- 建立可重現的實驗環境

#### 4. 評估指標實作

- 實現 WRMSSE 計算函數
- 理解層次性約束的數學原理
- 驗證評估結果的正確性

### 階段三：核心技能掌握 (4-6週)

#### 5. 深度特徵工程

- **滯後特徵**：不同時間窗口的歷史銷售量
- **滾動統計**：移動平均、標準差、分位數等
- **時間特徵**：週、月、季節、節假日效應
- **價格促銷特徵**：價格變化、促銷標誌、促銷持續時間
- **層次特徵**：不同層次的匯總統計

#### 6. 模型優化技術

- 損失函數與 WRMSSE 對齊
- 超參數調優策略
- 特徵選擇與正則化
- 零銷售與缺貨處理

### 階段四：高級應用 (4-8週)

#### 7. 頂級解決方案深度分析

- 研讀 IJF 特刊中的獲獎論文
- 分析不同技術路線的優劣
- 理解組合模型的設計思路

#### 8. 完整方案實踐

- 嘗試複現頂級方案的關鍵組件
- 開發自己的創新特徵
- 實現端到端的預測系統

---

## SOTA 方法解析

### 競賽對預測領域的影響

M5 競賽的獲獎方案展現了時間序列預測的前沿技術，主要包括以下幾個關鍵技術方向：

#### 1. 廣泛而深入的特徵工程

- **時間相關特徵**：年、月、日、星期幾、一年中的第幾天等
- **滯後特徵**：過去 7 天、14 天、28 天、365 天前的銷售量
- **滾動統計特徵**：不同時間窗口的均值、方差、分位數等
- **價格促銷特徵**：價格變化、促銷標誌、促銷持續時間
- **交叉特徵**：不同維度特徵的組合

#### 2. 基於樹的模型

- **主流選擇**：LightGBM 和 XGBoost
- **優勢**：處理缺失值和類別特徵、訓練速度快、可解釋性強
- **調優重點**：防止過擬合、處理時間序列的時序性

#### 3. 層次性預測策略

- **主流策略**：自底向上 (Bottom-Up)
- **協調方法**：MinTrace、OLS 等後處理協調技術
- **約束保持**：確保不同層次預測的一致性

#### 4. 其他關鍵技術

- **損失函數與指標匹配**：優化與 WRMSSE 相關的損失函數
- **時序交叉驗證**：避免未來數據洩漏的驗證策略
- **零銷售處理**：區分真實零需求與缺貨導致的零銷售
- **組合建模**：多模型ensemble提升預測穩定性

### SOTA 核心總結

- 極致的特徵工程
- 基於樹的梯度提升算法
- 自底向上的層次性策略
- 專用的損失函數設計

---

## 算法比較表

| 算法 | 核心概念 | 主要優勢 | M5表現 | 適用場景 |
|------|----------|----------|---------|----------|
| **ARIMAX** | ARIMA模型的擴展，增加外部變數 | 理論基礎扎實、可解釋性強 | 中等 | 需要解釋模型參數意義，時間序列模式相對簡單 |
| **XGBoost/LightGBM** | 高效的梯度提升決策樹框架 | 處理非線性關係、特徵工程友好 | 極佳 | 有豐富外部變數，可投入時間進行特徵工程 |
| **MLForecast** | 專注於大規模時間序列預測的框架 | 自動化特徵生成、高效處理多序列 | 優秀 | 需要同時預測大量時間序列 |
| **Prophet** | Facebook開發的可分解模型 | 易於使用、處理節假日效應 | 良好 | 具有明顯季節性和節假日效應的商業時間序列 |
| **NeuralProphet** | Prophet的神經網路擴展 | 結合傳統統計與深度學習 | 良好 | 需要Prophet易用性但要處理更複雜模式 |
| **LSTM/GRU** | 循環神經網路變體 | 捕捉長期依賴、處理複雜模式 | 中等 | 數據量大，模式極其複雜 |

### 選擇建議

- **明顯季節性和趨勢**：Prophet
- **複雜特徵工程需求**：LightGBM/XGBoost
- **大規模多序列**：MLForecast
- **複雜非線性模式**：LSTM/GRU
- **快速原型開發**：Prophet/NeuralProphet
- **需要解釋性**：ARIMAX

---

## 高級主題

### 深度學習與時間序列

- **Transformer 架構**：在時間序列預測中的應用
- **注意力機制**：捕捉長距離依賴關係
- **多任務學習**：同時優化多個相關預測任務

### 層次預測進階技術

- **層次協調方法**：MinT, OLS 等方法的原理與應用
- **稀疏協調**：處理大規模層次結構的高效方法
- **概率協調**：在不確定性量化中的應用

### 實際部署考量

- **模型效率優化**：大規模時間序列的快速預測
- **在線學習**：模型的增量更新策略
- **監控與維護**：生產環境中的模型健康度監控

### 相關競賽與持續學習

- **M 系列其他競賽**：M4、M6 等競賽的特性差異
- **工業應用場景**：零售、製造、金融等領域的預測挑戰
- **新興技術趨勢**：時間序列預測的最新發展方向

---

*本指南將持續更新，歡迎貢獻改進建議！*
