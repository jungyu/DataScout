import pandas as pd
import matplotlib.pyplot as plt
import os
import datetime as dt
from pathlib import Path
# https://www.stat.gov.tw/Point.aspx?sid=t.10&n=3589&sms=11480
# https://www.cbc.gov.tw/tw/lp-644-1.html
# 請替換成你從央行網站找到的實際 Excel 或 CSV 文件連結
# 這個 URL 只是範例，請務必找到最新的、正確的連結
file_url = "https://www.cbc.gov.tw/content/asset/AbilityInternational/Files/Foreign_Exchange_Reserves_and_Foreign_Investment_Position.xls" # 範例 URL, 可能需要根據網站實際情況調整

# 確保目標目錄存在
data_dir = Path("../data")
images_dir = Path("../images")
data_dir.mkdir(exist_ok=True)
images_dir.mkdir(exist_ok=True)

try:
    # 對於 Excel 文件 (.xls 或 .xlsx)
    # 通常政府提供的 Excel 文件可能會有標題、備註等在前面的行，需要用 skiprows 跳過
    # 也需要確認哪個 Sheet (工作表) 包含數據
    # column names 可能需要手動指定或根據文件內容調整
    # 實際的 skiprows 和 names 參數需要打開文件確認
    # 這裡假設數據從第 3 行開始，且第 1 列是日期，第 2 列是外匯存底金額
    # header=None 表示不將第一行作為標頭，names 手動指定列名
    # parse_dates=True 自動嘗試將日期列解析為日期時間對象
    # index_col=0 將日期列設置為索引
    df_fxreserves = pd.read_excel(file_url, sheet_name='Sheet1', skiprows=3, header=None, names=['Date', 'FX_Reserves_USD_Million'], parse_dates=[0], index_col=0)

    # 如果文件是 CSV 格式，使用 pd.read_csv
    # df_fxreserves = pd.read_csv(file_url, ...) # 參數類似，根據 CSV 格式調整

    # 清理數據：去除可能存在的 NaN 行或非數據行
    df_fxreserves = df_fxreserves.dropna()

    # 顯示數據
    print("台灣央行外匯儲備數據 (百萬美元):")
    print(df_fxreserves.head())
    print(df_fxreserves.tail())

    # 檢查數據類型
    print("\n數據資訊:")
    df_fxreserves.info()
    
    # 取得目前日期作為檔案名稱的一部分
    today = dt.datetime.now().strftime("%Y%m%d")
    
    # 保存處理後的數據到 CSV 檔案
    csv_filename = f"tw_fx_reserves_{today}.csv"
    csv_path = data_dir / csv_filename
    df_fxreserves.to_csv(csv_path)
    print(f"\n已將數據保存至: {csv_path}")
    
    # 創建視覺化圖表
    plt.figure(figsize=(12, 6))
    df_fxreserves.plot(title='台灣外匯存底趨勢 (百萬美元)', figsize=(12, 6))
    plt.grid(True)
    plt.tight_layout()
    
    # 保存圖表
    img_filename = f"tw_fx_reserves_trend_{today}.png"
    img_path = images_dir / img_filename
    plt.savefig(img_path, dpi=300)
    print(f"已將趨勢圖保存至: {img_path}")
    
    # 如果最近一年的資料足夠，建立最近一年趨勢圖
    one_year_ago = df_fxreserves.index.max() - pd.DateOffset(years=1)
    recent_data = df_fxreserves[df_fxreserves.index >= one_year_ago]
    
    if not recent_data.empty:
        plt.figure(figsize=(12, 6))
        recent_data.plot(title='台灣外匯存底近一年趨勢 (百萬美元)', figsize=(12, 6))
        plt.grid(True)
        plt.tight_layout()
        
        # 保存近一年趨勢圖
        recent_img_filename = f"tw_fx_reserves_recent_trend_{today}.png"
        recent_img_path = images_dir / recent_img_filename
        plt.savefig(recent_img_path, dpi=300)
        print(f"已將近一年趨勢圖保存至: {recent_img_path}")

except Exception as e:
    print(f"處理數據時發生錯誤: {e}")
    print("請確認文件 URL 是否正確，以及文件格式、跳過行數、列名等參數是否與文件內容匹配。")
    print("另外，請確認是否有權限寫入 ../data/ 和 ../images/ 目錄。")