@echo off
setlocal enabledelayedexpansion

echo 📦 正在編譯前端...
call npm run build

:: 設定目標目錄
set "WEB_SERVICE_PATH=..\web_service"
set "STATIC_PATH=%WEB_SERVICE_PATH%\static"
set "TEMPLATES_PATH=%WEB_SERVICE_PATH%\templates"

:: 備份現有的靜態資源
echo 📦 備份現有的靜態資源...
set "BACKUP_DIR=%STATIC_PATH%\backup_%date:~0,4%%date:~5,2%%date:~8,2%_%time:~0,2%%time:~3,2%%time:~6,2%"
set "BACKUP_DIR=!BACKUP_DIR: =0!"
if exist "%STATIC_PATH%" (
    mkdir "%BACKUP_DIR%" 2>nul
    move "%STATIC_PATH%\*" "%BACKUP_DIR%" 2>nul
)

:: 創建必要的目錄
echo 📦 創建必要的目錄...
mkdir "%STATIC_PATH%" 2>nul
mkdir "%TEMPLATES_PATH%" 2>nul

:: 複製靜態資源
echo 📦 複製靜態資源...
xcopy /E /I /Y "dist\*" "%STATIC_PATH%"

:: 額外複製範例資料
echo 📦 額外複製範例資料...
mkdir "%STATIC_PATH%\assets\examples" 2>nul
xcopy /E /I /Y "public\assets\examples\*" "%STATIC_PATH%\assets\examples\" 2>nul

:: 複製組件
echo 📦 複製組件 components/charts...
mkdir "%STATIC_PATH%\components\charts" 2>nul
xcopy /Y "public\components\charts\*.html" "%STATIC_PATH%\components\charts\" 2>nul

:: 複製自訂 JS
echo 📦 複製自訂 JS...
xcopy /Y "public\*.js" "%STATIC_PATH%\" 2>nul

:: 複製 index.html 到 templates
echo 📦 複製 index.html 到 templates...
copy /Y "dist\index.html" "%TEMPLATES_PATH%\index.html"

:: 顯示完成訊息
echo ✅ 前端已成功部署到 web_service！
echo - 靜態資源：%STATIC_PATH%
echo - 首頁模板：%TEMPLATES_PATH%\index.html
echo - 備份目錄：%BACKUP_DIR%

endlocal 