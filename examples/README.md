# Selenium 爬蟲框架使用說明文件   
這個文件將說明如何使用 Selenium 爬蟲框架來爬取不同網站的資料，包括 Google 搜尋結果、實價登錄及政府電子採購網等網站。   
## 專案檔案結構與功能介紹   
專案包含以下幾組爬蟲程式：   
### 1. Google 搜尋爬蟲系列   
- **basic\_1\_google\_search\_without\_template.py** - 基礎版 Google 搜尋爬蟲，不使用模板配置   
- **basic\_2\_google\_search.py** - 使用 JSON 配置文件的 Google 搜尋爬蟲   
- **basic\_3\_google\_search\_pts.py** - 針對公視新聞的 Google 搜尋爬蟲，含詳細頁面解析功能   
- **basic\_google\_search.json** - Google 搜尋爬蟲的配置文件   
- **basic\_google\_search\_pts.json** - 公視新聞搜尋爬蟲的配置文件   
   
### 2. 實價登錄爬蟲   
- **basic\_4\_price\_house.py** - 實價登錄網站資料爬取工具   
- **basic\_price\_house.json** - 實價登錄爬蟲的配置文件   
   
### 3. 政府電子採購網爬蟲   
- **basic\_5\_pcc\_award.py** - 政府電子採購網決標查詢爬蟲   
- **basic\_6\_pcc\_tender.py** - 政府電子採購網招標公告查詢爬蟲   
- **basic\_pcc\_award.json** - 決標查詢爬蟲的配置文件   
- **basic\_pcc\_tender.json** - 招標公告查詢爬蟲的配置文件   
   
## 環境安裝指南   
### 基本 Python 環境   
1. 確保已安裝 Python 3.7 或以上版本   
2. 安裝必要的 Python 套件：   
   
pip install -r requirements.txt   
[requirements.txt](vscode-file:/vscode-app/Applications/Visual%20Studio%20Code.app/Contents/Resources/app/out/vs/code/electron-sandbox/workbench/workbench.html) 文件內容：   
selenium>=4.9.0   
lxml>=4.9.2   
webdriver-manager>=3.8.6   
requests>=2.28.2   
beautifulsoup4>=4.12.2   
### Windows 環境下的 Selenium 安裝   
1. **安裝 Chrome 瀏覽器**：   
    - 從 [https://www.google.com/chrome/](vscode-file:/vscode-app/Applications/Visual%20Studio%20Code.app/Contents/Resources/app/out/vs/code/electron-sandbox/workbench/workbench.html) 下載安裝   
2. **安裝 ChromeDriver**：   
    - 方法一：使用 webdriver-manager 自動管理（推薦）   
        pip install webdriver-manager   
    - 方法二：手動安裝   
        - 查看您的 Chrome 版本：Chrome 設定 → 關於 Chrome   
        - 從 [https://sites.google.com/chromium.org/driver/](vscode-file:/vscode-app/Applications/Visual%20Studio%20Code.app/Contents/Resources/app/out/vs/code/electron-sandbox/workbench/workbench.html) 下載對應版本   
        - 將 chromedriver.exe 放入 PATH 環境變數中的目錄，或放在專案根目錄   
3. **檢查安裝**：   
    python -c "from selenium import webdriver; from selenium.webdriver.chrome.service import Service; from webdriver\_manager.chrome import ChromeDriverManager; driver = webdriver.Chrome(service=Service(ChromeDriverManager().install())); driver.quit()"   
   
### Ubuntu 環境下的 Selenium 安裝   
1. **安裝 Chrome 瀏覽器**：   
    wget -q -O - https://dl-ssl.google.com/linux/linux\_signing\_key.pub \| sudo apt-key add -   
    sudo sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list'   
    sudo apt update   
    sudo apt install google-chrome-stable   
2. **安裝 ChromeDriver**：   
    - 使用 webdriver-manager 自動管理（推薦）：   
        pip install webdriver-manager   
    - 或手動安裝：   
        CHROME\_VERSION=$(google-chrome --version \| awk '{print $3}' \| cut -d. -f1)   
        wget -N https://chromedriver.storage.googleapis.com/LATEST\_RELEASE\_${CHROME\_VERSION} -O latest\_release   
        DRIVER\_VERSION=$(cat latest\_release)   
        wget -N https://chromedriver.storage.googleapis.com/${DRIVER\_VERSION}/chromedriver\_linux64.zip   
        unzip chromedriver\_linux64.zip   
        chmod +x chromedriver   
        sudo mv chromedriver /usr/local/bin/   
        rm chromedriver\_linux64.zip latest\_release   
3. **安裝必要的系統依賴**：   
    sudo apt install -y xvfb libxi6 libgconf-2-4   
4. **如需無界面執行**：   
    sudo apt install -y xvfb   
    # 執行時使用   
    # xvfb-run python your\_crawler.py   
   
## 執行方式   
### 基本執行命令   
從專案根目錄執行以下命令來運行爬蟲：   
python examples/basic\_6\_pcc\_tender.py   
### 政府電子採購網爬蟲執行範例   
政府電子採購網有兩個爬蟲：招標公告查詢和決標查詢。   
### 1. 招標公告查詢爬蟲 (basic\_6\_pcc\_tender.py)   
此爬蟲會根據設定條件爬取政府電子採購網的招標公告資料。   
python examples/basic\_6\_pcc\_tender.py   
修改 [basic\_pcc\_tender.json](vscode-file:/vscode-app/Applications/Visual%20Studio%20Code.app/Contents/Resources/app/out/vs/code/electron-sandbox/workbench/workbench.html) 配置檔案可以變更爬蟲的行為：   
- `search\_parameters` 區塊中可設定搜尋條件   
    - [tender\_name](vscode-file:/vscode-app/Applications/Visual%20Studio%20Code.app/Contents/Resources/app/out/vs/code/electron-sandbox/workbench/workbench.html): 標案名稱   
    - [tender\_start\_date](vscode-file:/vscode-app/Applications/Visual%20Studio%20Code.app/Contents/Resources/app/out/vs/code/electron-sandbox/workbench/workbench.html): 招標公告開始日期   
    - [tender\_end\_date](vscode-file:/vscode-app/Applications/Visual%20Studio%20Code.app/Contents/Resources/app/out/vs/code/electron-sandbox/workbench/workbench.html): 招標公告結束日期   
    - [procurement\_category](vscode-file:/vscode-app/Applications/Visual%20Studio%20Code.app/Contents/Resources/app/out/vs/code/electron-sandbox/workbench/workbench.html): 採購性質（財物類、工程類、勞務類）   
    - [date\_type](vscode-file:/vscode-app/Applications/Visual%20Studio%20Code.app/Contents/Resources/app/out/vs/code/electron-sandbox/workbench/workbench.html): 日期類型（等標期內、當日、日期區間）   
   
主要更新的功能：   
- 修正了搜尋 URL 構建邏輯，現在正確使用 `dateType=isSpdt` 參數   
- 新增了 `policyAdvocacy` 參數支援   
- 優化了詳情頁面的資料提取，特別是處理複雜格式的地址、電話和分類資訊   
   
### 2. 決標查詢爬蟲 (basic\_5\_pcc\_award.py)   
此爬蟲可爬取決標公告資料：   
python examples/basic\_5\_pcc\_award.py   
可修改 [basic\_pcc\_award.json](vscode-file:/vscode-app/Applications/Visual%20Studio%20Code.app/Contents/Resources/app/out/vs/code/electron-sandbox/workbench/workbench.html) 配置中的 `search\_parameters` 來調整搜尋條件：   
- [tender\_name](vscode-file:/vscode-app/Applications/Visual%20Studio%20Code.app/Contents/Resources/app/out/vs/code/electron-sandbox/workbench/workbench.html): 標案名稱   
- [award\_announce\_start\_date](vscode-file:/vscode-app/Applications/Visual%20Studio%20Code.app/Contents/Resources/app/out/vs/code/electron-sandbox/workbench/workbench.html): 決標公告開始日期   
- [award\_announce\_end\_date](vscode-file:/vscode-app/Applications/Visual%20Studio%20Code.app/Contents/Resources/app/out/vs/code/electron-sandbox/workbench/workbench.html): 決標公告結束日期   
- [procurement\_category](vscode-file:/vscode-app/Applications/Visual%20Studio%20Code.app/Contents/Resources/app/out/vs/code/electron-sandbox/workbench/workbench.html): 採購性質   
- [tender\_status](vscode-file:/vscode-app/Applications/Visual%20Studio%20Code.app/Contents/Resources/app/out/vs/code/electron-sandbox/workbench/workbench.html): 標案狀態   
   
### 實價登錄爬蟲執行範例   
實價登錄爬蟲可以爬取特定地區的房產交易資料：   
python examples/basic\_4\_price\_house.py   
在 [basic\_price\_house.json](vscode-file:/vscode-app/Applications/Visual%20Studio%20Code.app/Contents/Resources/app/out/vs/code/electron-sandbox/workbench/workbench.html) 中可以修改這些參數：   
- [city](vscode-file:/vscode-app/Applications/Visual%20Studio%20Code.app/Contents/Resources/app/out/vs/code/electron-sandbox/workbench/workbench.html): 縣市（如「屏東縣」）   
- [district](vscode-file:/vscode-app/Applications/Visual%20Studio%20Code.app/Contents/Resources/app/out/vs/code/electron-sandbox/workbench/workbench.html): 鄉鎮區（如「內埔鄉」）   
- [building\_type](vscode-file:/vscode-app/Applications/Visual%20Studio%20Code.app/Contents/Resources/app/out/vs/code/electron-sandbox/workbench/workbench.html): 建物型態   
   
### Google 搜尋爬蟲執行範例   
### 1. 基礎版 Google 搜尋   
python examples/basic\_1\_google\_search\_without\_template.py   
### 2. 配置化 Google 搜尋   
python examples/basic\_2\_google\_search.py   
可在 [basic\_google\_search.json](vscode-file:/vscode-app/Applications/Visual%20Studio%20Code.app/Contents/Resources/app/out/vs/code/electron-sandbox/workbench/workbench.html) 中修改 [search.keyword](vscode-file:/vscode-app/Applications/Visual%20Studio%20Code.app/Contents/Resources/app/out/vs/code/electron-sandbox/workbench/workbench.html) 參數設定搜尋關鍵字。   
### 3. 公視新聞爬蟲   
python examples/basic\_3\_google\_search\_pts.py   
在 [basic\_google\_search\_pts.json](vscode-file:/vscode-app/Applications/Visual%20Studio%20Code.app/Contents/Resources/app/out/vs/code/electron-sandbox/workbench/workbench.html) 中可設定搜尋關鍵字及詳情頁面解析方式。   
## 常見問題與解決方案   
### 1. ChromeDriver 版本不匹配   
**問題**: 出現 `SessionNotCreatedException` 錯誤，提示 ChromeDriver 版本與 Chrome 不匹配。   
**解決方案**:   
- 推薦使用 [webdriver-manager](vscode-file:/vscode-app/Applications/Visual%20Studio%20Code.app/Contents/Resources/app/out/vs/code/electron-sandbox/workbench/workbench.html) 套件自動管理 ChromeDriver 版本   
- 如手動安裝，確保下載的 ChromeDriver 版本與您的 Chrome 瀏覽器版本匹配   
   
### 2. 頁面載入超時   
**問題**: 出現 [TimeoutException](vscode-file:/vscode-app/Applications/Visual%20Studio%20Code.app/Contents/Resources/app/out/vs/code/electron-sandbox/workbench/workbench.html) 錯誤。   
**解決方案**:   
- 增加 `delays.page\_load` 設定值   
- 檢查網路連線是否穩定   
- 確認目標網站是否允許爬蟲訪問   
   
### 3. XPath 選擇器失效   
**問題**: 無法找到頁面元素，可能是網站結構有變更。   
**解決方案**:   
- 更新 JSON 配置檔中的 XPath 選擇器   
- 添加備用 XPath 選擇器在 [fallback\_xpath](vscode-file:/vscode-app/Applications/Visual%20Studio%20Code.app/Contents/Resources/app/out/vs/code/electron-sandbox/workbench/workbench.html) 欄位中   
- 使用 Chrome 開發者工具檢查最新的頁面結構   
   
### 4. 防爬蟲機制檢測   
**問題**: 網站偵測到爬蟲行為並阻擋。   
**解決方案**:   
- 調整 `delays` 設定增加操作間隔時間   
- 在 HTTP 請求標頭中添加更擬真的 `User-Agent`   
- 使用代理 IP 輪換訪問   
- 減少批次請求數量   
   
## 維護與更新   
如果遇到爬蟲失效的情況，通常是因為目標網站結構變更。這時可以：   
1. 使用 Chrome 開發者工具重新檢查頁面元素   
2. 更新 JSON 配置檔中的 XPath 選擇器   
3. 如有必要，可能需要修改 Python 代碼中的解析邏輯   
   
## 特別提示   
- 使用爬蟲時請尊重網站的 robots.txt 規則   
- 避免頻繁請求對目標網站造成負擔   
- 僅將爬取的資料用於合法、合理的目的   
