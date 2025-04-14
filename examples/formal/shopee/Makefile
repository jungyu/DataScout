# Shopee 爬蟲 Makefile

# 變數定義
PYTHON = python3
PYTEST = pytest
PIP = pip3

# 目錄定義
SRC_DIR = .
TEST_DIR = tests
EXAMPLE_DIR = examples
LOG_DIR = logs
RESULT_DIR = results

# 目標定義
.PHONY: all clean test run-example-basic run-example-advanced install

# 預設目標
all: install test

# 安裝依賴
install:
	$(PIP) install -r requirements.txt

# 清理
clean:
	rm -rf $(LOG_DIR)
	rm -rf $(RESULT_DIR)
	rm -rf __pycache__
	rm -rf */__pycache__
	rm -rf */*/__pycache__
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete

# 執行測試
test:
	$(PYTEST) $(TEST_DIR) -v

# 執行基本範例
run-example-basic:
	$(PYTHON) $(EXAMPLE_DIR)/basic_usage.py

# 執行進階範例
run-example-advanced:
	$(PYTHON) $(EXAMPLE_DIR)/advanced_usage.py

# 建立必要的目錄
setup-dirs:
	mkdir -p $(LOG_DIR)
	mkdir -p $(RESULT_DIR)

# 檢查程式碼風格
lint:
	flake8 $(SRC_DIR)
	black --check $(SRC_DIR)
	isort --check-only $(SRC_DIR)

# 格式化程式碼
format:
	black $(SRC_DIR)
	isort $(SRC_DIR)

# 顯示幫助訊息
help:
	@echo "可用的命令："
	@echo "  make install          - 安裝依賴"
	@echo "  make clean           - 清理暫存檔案"
	@echo "  make test            - 執行測試"
	@echo "  make run-example-basic    - 執行基本範例"
	@echo "  make run-example-advanced - 執行進階範例"
	@echo "  make setup-dirs      - 建立必要的目錄"
	@echo "  make lint            - 檢查程式碼風格"
	@echo "  make format          - 格式化程式碼"
	@echo "  make help            - 顯示此幫助訊息" 