# DataScout Chart App 重構指南

本文件提供了關於如何完成 DataScout chart_app JavaScript 重構工作的詳細步驟指南。

## 重構目標

1. 改善代碼組織結構，提高可維護性
2. 按功能分類模組
3. 減少模組間的耦合
4. 建立清晰的依賴關係
5. 優化未來擴展性

## 目錄結構

重構後，src/js 目錄的結構如下：

```
src/js/
├── adapters/       (Chart.js 適配器和渲染器)
├── core/           (核心應用功能)
├── data-handling/  (數據加載和處理)
├── utils/          (工具函數)
├── plugins/        (插件和擴展)
├── index.js        (集中模組導出)
├── main.js         (應用程式入口點)
└── README.md       (文檔)
```

## 重構步驟

### 步驟 1: 準備工作

1. 首先確保已安裝所有依賴：
   ```bash
   cd /Users/aaron/Projects/DataScout/chart_app
   npm install
   ```

2. 備份原始程式碼：
   ```bash
   mkdir -p backup/src
   cp -r src/js backup/src/
   ```

### 步驟 2: 創建目錄結構

執行以下腳本來創建所需的目錄結構：

```bash
mkdir -p src/js/core
mkdir -p src/js/adapters
mkdir -p src/js/data-handling
mkdir -p src/js/utils
```

### 步驟 3: 移動檔案到對應目錄

1. 運行重新組織程式碼的腳本：
   ```bash
   chmod +x scripts/restructure_js_files.sh
   ./scripts/restructure_js_files.sh
   ```

2. 修復導入路徑：
   ```bash
   chmod +x scripts/fix_import_paths.sh
   ./scripts/fix_import_paths.sh
   ```

### 步驟 4: 更新 webpack.config.js

確保 webpack 配置文件中的入口點引用了新的文件路徑：

```bash
vim webpack.config.js
```

### 步驟 5: 測試構建

1. 執行構建腳本：
   ```bash
   npm run build:js:prod
   ```

2. 解決構建過程中出現的任何錯誤。

### 步驟 6: 清理舊檔案

確認所有功能正常後，運行清理腳本：

```bash
chmod +x scripts/cleanup_js_root.sh
./scripts/cleanup_js_root.sh
```

## 重構後的維護指南

### 新增功能

添加新功能時，請遵循以下原則：

1. **Core 模組**：核心應用邏輯和狀態管理
2. **Adapters 模組**：與圖表庫的接口
3. **Data-handling 模組**：數據處理和轉換
4. **Utils 模組**：通用工具函數

### 導入規則

- 使用相對路徑導入模組
- 同一目錄的模組用 `./module.js`
- 跨目錄的模組用 `../directory/module.js`
- 避免循環依賴

### 命名規範

- 文件名使用 kebab-case：`file-name.js`
- 函數和變量使用 camelCase：`functionName`
- 類使用 PascalCase：`ClassName`
- 常量使用 UPPER_SNAKE_CASE：`MAX_VALUE`

## 測試

每次修改後，確保運行測試：

```bash
npm run test
```

## 文檔

重要的更改應該更新 README.md 和相關文檔。

---

完成本指南中的步驟後，您將擁有一個經過改進的、更具可維護性的代碼庫結構。
