# Python 虛擬環境管理指南

建立時間: 2025年5月25日 下午11:24

## 目錄
1. [基本操作](#基本操作)
2. [套件管理](#套件管理)
3. [常見問題處理](#常見問題處理)
4. [注意事項](#注意事項)

## 基本操作

### 建立虛擬環境
```bash
# 在專案目錄外建立虛擬環境
cd /Users/aaron/Projects/DataScout
python -m venv venv
```

### 啟動虛擬環境
```bash
# macOS/Linux
source venv/bin/activate

# Windows
.\venv\Scripts\activate
```

### 退出虛擬環境
```bash
deactivate
```

## 套件管理

### 安裝專案依賴
```bash
# 進入專案目錄
cd telegram_bot  # 或其他專案目錄

# 安裝依賴
pip install -e .
```

### 查看已安裝套件
```bash
# 列出所有已安裝的套件
pip list
```

### 導出依賴清單
```bash
# 導出依賴清單
pip freeze > requirements.txt
```

## 常見問題處理

### 1. 清空並重新安裝所有套件

#### 方法一：使用 pip freeze
```bash
# 列出所有已安裝的套件
pip freeze > requirements_to_remove.txt

# 卸載所有套件
pip uninstall -r requirements_to_remove.txt -y

# 刪除臨時文件
rm requirements_to_remove.txt

# 重新安裝專案依賴
pip install -e .
```

#### 方法二：使用 Python 腳本（推薦）
```python
import pkg_resources
import subprocess

# 獲取已安裝的套件
installed_packages = [pkg.key for pkg in pkg_resources.working_set]

# 排除基礎套件
exclude_packages = {'pip', 'setuptools', 'wheel'}
packages_to_remove = [pkg for pkg in installed_packages if pkg not in exclude_packages]

# 卸載套件
for package in packages_to_remove:
    try:
        subprocess.check_call(['pip', 'uninstall', '-y', package])
    except subprocess.CalledProcessError:
        print(f"無法卸載 {package}")
```

### 2. 移除特定套件

#### 方法一：使用 pip uninstall
```bash
# 直接卸載指定套件
pip uninstall package_name -y
```

#### 方法二：從 requirements.txt 卸載
```bash
# 從 requirements.txt 卸載所有套件
pip uninstall -r requirements.txt -y

# 或使用更安全的方式
cat requirements.txt | cut -d'=' -f1 | xargs pip uninstall -y
```

### 3. 完全重置虛擬環境
```bash
# 1. 退出虛擬環境
deactivate

# 2. 刪除現有虛擬環境
rm -rf venv  # macOS/Linux
# 或
rmdir /s /q venv  # Windows

# 3. 創建新的虛擬環境
python -m venv venv

# 4. 啟動虛擬環境
source venv/bin/activate  # macOS/Linux
# 或
.\venv\Scripts\activate  # Windows

# 5. 安裝專案依賴
pip install -e .
```

## 注意事項

1. 建議在虛擬環境中操作，避免影響系統 Python 環境
2. 某些基礎套件（如 pip、setuptools、wheel）最好不要卸載
3. 如果遇到依賴問題，可能需要使用 `--no-deps` 參數
4. 建議在操作前先備份重要的套件列表
5. 在 macOS 上使用命令時，注意避免使用 `awk` 命令，改用 `cut` 或 Python 腳本

讓我為您說明如何安裝 `playwright_base` 的依賴：

1. **首先確認虛擬環境已啟動**：
```bash
# 確認是否在虛擬環境中
which python
# 應該顯示：/Users/aaron/Projects/DataScout/venv/bin/python
```

2. **安裝 playwright_base 的依賴**：
```bash
# 進入 playwright_base 目錄
cd /Users/aaron/Projects/DataScout/playwright_base

# 安裝依賴
pip install -e .
```

3. **如果 playwright_base 有自己的 requirements.txt**：
```bash
# 直接安裝 requirements.txt 中的依賴
pip install -r requirements.txt
```

4. **安裝 Playwright 瀏覽器**：
```bash
# 安裝 Playwright 的瀏覽器
playwright install
```

5. **驗證安裝**：
```bash
# 檢查已安裝的套件
pip list | grep playwright
```

6. **注意事項**：
   - 確保您在正確的虛擬環境中
   - 如果遇到權限問題，可能需要使用 `sudo` 或調整權限
   - 如果安裝過程中出現錯誤，可以嘗試：
     ```bash
     # 更新 pip
     pip install --upgrade pip
     
     # 清除 pip 快取
     pip cache purge
     
     # 重新安裝
     pip install -e .
     ```

7. **檢查依賴是否正確安裝**：
```bash
# 檢查 Python 是否可以導入 playwright
python -c "from playwright.sync_api import sync_playwright; print('Playwright 安裝成功')"
```

如果您需要查看 `playwright_base` 的具體依賴，我可以幫您檢查 `setup.py` 或 `requirements.txt` 的內容。

讓我為您說明如何安裝 `persistence` 的依賴：

1. **首先確認虛擬環境已啟動**：
```bash
# 確認是否在虛擬環境中
which python
# 應該顯示：/Users/aaron/Projects/DataScout/venv/bin/python
```

2. **安裝 persistence 的依賴**：
```bash
# 進入 persistence 目錄
cd /Users/aaron/Projects/DataScout/persistence

# 安裝依賴
pip install -e .
```

3. **如果 persistence 有自己的 requirements.txt**：
```bash
# 直接安裝 requirements.txt 中的依賴
pip install -r requirements.txt
```

4. **驗證安裝**：
```bash
# 檢查已安裝的套件
pip list | grep persistence
```

5. **注意事項**：
   - 確保您在正確的虛擬環境中
   - 如果遇到權限問題，可能需要使用 `sudo` 或調整權限
   - 如果安裝過程中出現錯誤，可以嘗試：
     ```bash
     # 更新 pip
     pip install --upgrade pip
     
     # 清除 pip 快取
     pip cache purge
     
     # 重新安裝
     pip install -e .
     ```

6. **檢查依賴是否正確安裝**：
```bash
# 檢查 Python 是否可以導入 persistence
python -c "import persistence; print('Persistence 安裝成功')"
```

如果您需要查看 `persistence` 的具體依賴，我可以幫您檢查 `setup.py` 或 `requirements.txt` 的內容。

讓我為您說明如何安裝 `autoflow` 的依賴：

1. **首先確認虛擬環境已啟動**：
```bash
# 確認是否在虛擬環境中
which python
# 應該顯示：/Users/aaron/Projects/DataScout/venv/bin/python
```

2. **安裝 autoflow 的依賴**：
```bash
# 進入 autoflow 目錄
cd /Users/aaron/Projects/DataScout/autoflow

# 安裝依賴
pip install -e .
```

3. **如果 autoflow 有自己的 requirements.txt**：
```bash
# 直接安裝 requirements.txt 中的依賴
pip install -r requirements.txt
```

4. **驗證安裝**：
```bash
# 檢查已安裝的套件
pip list | grep autoflow
```

5. **注意事項**：
   - 確保您在正確的虛擬環境中
   - 如果遇到權限問題，可能需要使用 `sudo` 或調整權限
   - 如果安裝過程中出現錯誤，可以嘗試：
     ```bash
     # 更新 pip
     pip install --upgrade pip
     
     # 清除 pip 快取
     pip cache purge
     
     # 重新安裝
     pip install -e .
     ```

6. **檢查依賴是否正確安裝**：
```bash
# 檢查 Python 是否可以導入 autoflow
python -c "import autoflow; print('Autoflow 安裝成功')"
```

如果您需要查看 `autoflow` 的具體依賴，我可以幫您檢查 `setup.py` 或 `requirements.txt` 的內容。
