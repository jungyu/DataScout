# Chart App 重構測試計劃

## 測試目標

確保重構後的 Chart App 保持功能完整性，並驗證模組化設計的正確性。

## 測試環境

- Node.js v16+
- npm v8+
- Jest 測試框架
- 瀏覽器: Chrome, Firefox, Safari

## 測試範圍

1. **單元測試** - 測試各個模組的獨立功能
2. **整合測試** - 測試模組間的交互
3. **功能測試** - 測試完整應用功能
4. **瀏覽器相容性測試** - 檢驗主流瀏覽器上的表現

## 測試項目明細

### 1. 單元測試

#### 1.1 狀態管理模組 (state-manager.js)

- 測試初始狀態設定
- 測試狀態獲取與設置功能
- 測試狀態重置功能
- 測試數據統計功能

#### 1.2 應用初始化模組 (app-initializer.js)

- 測試 URL 參數處理
- 測試頁面初始化流程
- 測試應用程式狀態初始化

#### 1.3 UI 控制模組 (ui-controller.js)

- 測試事件監聽設定
- 測試 UI 元素更新
- 測試範例檔案列表生成

#### 1.4 資料載入模組 (data-loader.js)

- 測試資料格式轉換
- 測試檔案載入流程
- 測試資料驗證功能

#### 1.5 圖表管理模組 (chart-manager.js)

- 測試圖表創建功能
- 測試主題更新功能
- 測試資料更新功能
- 測試統計資訊功能

#### 1.6 依賴檢查模組 (dependency-checker.js)

- 測試 Chart.js 檢測
- 測試插件檢測
- 測試 Canvas 支援檢測

### 2. 整合測試

- 測試狀態管理與 UI 控制的整合
- 測試資料載入與圖表管理的整合
- 測試初始化流程與其他模組的整合
- 測試完整的應用程式流程

### 3. 功能測試

- 測試圖表類型切換
- 測試圖表主題切換
- 測試檔案上傳功能
- 測試範例資料載入
- 測試匯出功能
- 測試擷取圖表功能

### 4. 瀏覽器相容性測試

- Chrome 最新版
- Firefox 最新版
- Safari 最新版
- Edge 最新版
- 行動裝置瀏覽器 (iOS Safari, Android Chrome)

## 測試數據準備

準備以下測試資料:
1. 各種格式的正確資料檔案 (JSON, CSV, Excel)
2. 格式錯誤的資料檔案
3. 不同圖表類型所需的特殊格式資料

## 測試腳本範例

```javascript
// state-manager.js 測試範例
describe('StateManager 測試', () => {
  beforeEach(() => {
    // 重置應用程式狀態
    resetAppState();
  });
  
  test('初始化狀態應包含預設值', () => {
    const appState = getAppState();
    expect(appState.currentChartType).toBe('radar');
    expect(appState.currentDataType).toBe('json');
  });
  
  test('設置狀態值應成功更新', () => {
    setStateValue('currentChartType', 'bar');
    const appState = getAppState();
    expect(appState.currentChartType).toBe('bar');
  });
});
```

## 測試流程

1. **設定測試環境**
   ```bash
   npm install
   ```

2. **運行單元測試**
   ```bash
   npm test
   ```
   
3. **運行覆蓋率測試**
   ```bash
   npm run test:coverage
   ```
   
4. **運行 E2E 測試**
   ```bash
   npm run test:e2e
   ```

## 測試報告

測試報告將包含以下內容:
1. 測試摘要 (通過/失敗數量)
2. 覆蓋率報告
3. 失敗測試的詳細資訊
4. 效能指標

## 預期結果

- 所有單元測試通過率 > 95%
- 代碼覆蓋率 > 85%
- 功能測試通過率 = 100%
- 瀏覽器相容性測試通過率 > 90%

---

## 執行測試指南

### 初始設定

1. 確保已安裝所有依賴:
   ```bash
   cd /Users/aaron/Projects/DataScout/chart_app
   npm install
   ```

2. 建置專案:
   ```bash
   npm run build
   ```

### 運行測試

1. 單元測試:
   ```bash
   npm test
   ```

2. 瀏覽器功能測試:
   ```bash
   npm run serve
   # 在瀏覽器中打開 http://localhost:8080 進行手動測試
   ```

### 驗收條件

1. 圖表功能與重構前完全相同
2. 無主控台錯誤
3. 所有測試都通過
4. 代碼結構符合模組化設計規範
