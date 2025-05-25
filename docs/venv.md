# Python 虛擬環境下的套件安裝管理

建立時間: 2025年5月25日 下午11:24

## 目錄
1. [基本操作](#基本操作)
2. [套件管理](#套件管理)
3. [常見問題處理](#常見問題處理)

## 基本操作

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

### 創建新的虛擬環境
```bash
# 創建虛擬環境
python -m venv venv

# 啟動虛擬環境
source venv/bin/activate  # macOS/Linux
# 或
.\venv\Scripts\activate  # Windows
```

## 套件管理

### 安裝專案依賴
```bash
# 安裝專案依賴
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