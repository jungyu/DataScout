import pandas as pd
import requests
import io
import matplotlib.pyplot as plt
import os
import datetime as dt
from pathlib import Path

# 請替換成你從財政部網站找到的實際文件下載連結
# 這個 URL 是 Treasury 網站上一個可能的數據文件連結範例 (TXT 格式，TAB 分隔)
# 請務必找到最新的、正確的連結
file_url = "https://ticdata.treasury.gov/Publish/mfh.txt" # 範例 URL, 請務必確認

# 確保目標目錄存在
data_dir = Path("../data")
images_dir = Path("../images")
data_dir.mkdir(exist_ok=True)
images_dir.mkdir(exist_ok=True)

try:
    # 使用 requests 下載文件內容
    response = requests.get(file_url)
    response.raise_for_status() # 檢查請求是否成功

    # 將下載的內容讀入 Pandas DataFrame
    # TIC 的 TXT 文件通常是 TAB 分隔的
    # header=0 表示第一行是表頭
    # 實際的分隔符號 (sep) 需要根據文件內容確認，可能是 '\t' 或 ','
    # index_col 可能需要設定日期列作為索引
    # 數據格式也可能需要調整 (例如去除逗號並轉換為數字)
    # 實際的參數需要打開文件確認
    # 這裡假設它是 Tab 分隔的 TXT 文件，並且日期是第一列 (Year/Month)，國家是後續的列

    # 使用 io.StringIO 讓 pandas 可以從字符串直接讀取
    data_string = io.StringIO(response.text)

    # 嘗試讀取 TSV 文件
    # 注意：TIC 的文件格式可能很特殊，可能需要更複雜的解析邏輯
    # 例如，年份和月份可能在不同的列，或者有額外的表頭行
    # 請務必打開 mfh.txt 文件查看其結構
    df_tic = pd.read_csv(data_string, sep='\t', header=0)

    print("原始數據的前幾行:")
    print(df_tic.head()) # 打印原始讀取的數據框架，以便檢查格式

    # 數據清洗和處理 (這部分高度依賴於文件格式)
    # 從查看mfh.txt的內容來看，它通常有Date列與各國家列
    # 我們假設文件有'Date'和'Taiwan'列
    
    # 檢查文件中是否包含 'Taiwan' 列
    if 'Taiwan' in df_tic.columns:
        # 提取台灣數據
        df_taiwan = df_tic[['Date', 'Taiwan']]
        
        # 將Date列轉換為日期格式（如果需要）
        df_taiwan['Date'] = pd.to_datetime(df_taiwan['Date'])
        
        # 將Taiwan列轉換為數值型別（去除可能的千位分隔符）
        df_taiwan['Taiwan'] = pd.to_numeric(df_taiwan['Taiwan'].astype(str).str.replace(',', ''), errors='coerce')
        
        # 移除任何可能的NaN值
        df_taiwan_cleaned = df_taiwan.dropna()
        
        # 設置Date為索引
        df_taiwan_cleaned = df_taiwan_cleaned.set_index('Date')
        
        print("\n台灣持有美債數據 (百萬美元):")
        print(df_taiwan_cleaned.head())
        print(df_taiwan_cleaned.tail())
        
        # 檢查數據類型
        print("\n數據資訊:")
        print(df_taiwan_cleaned.info())
        
        # 取得目前日期作為檔案名稱的一部分
        today = dt.datetime.now().strftime("%Y%m%d")
        
        # 保存處理後的數據到 CSV 檔案
        csv_filename = f"tw_us_treasury_holdings_{today}.csv"
        csv_path = data_dir / csv_filename
        df_taiwan_cleaned.to_csv(csv_path)
        print(f"\n已將數據保存至: {csv_path}")
        
        # 創建視覺化圖表
        plt.figure(figsize=(12, 6))
        df_taiwan_cleaned.plot(title='台灣持有美國國債趨勢 (百萬美元)', figsize=(12, 6))
        plt.grid(True)
        plt.tight_layout()
        
        # 保存圖表
        img_filename = f"tw_us_treasury_holdings_trend_{today}.png"
        img_path = images_dir / img_filename
        plt.savefig(img_path, dpi=300)
        print(f"已將趨勢圖保存至: {img_path}")
        
        # 如果最近一年的資料足夠，建立最近一年趨勢圖
        if not df_taiwan_cleaned.empty:
            one_year_ago = df_taiwan_cleaned.index.max() - pd.DateOffset(years=1)
            recent_data = df_taiwan_cleaned[df_taiwan_cleaned.index >= one_year_ago]
            
            if not recent_data.empty:
                plt.figure(figsize=(12, 6))
                recent_data.plot(title='台灣持有美國國債近一年趨勢 (百萬美元)', figsize=(12, 6))
                plt.grid(True)
                plt.tight_layout()
                
                # 保存近一年趨勢圖
                recent_img_filename = f"tw_us_treasury_holdings_recent_trend_{today}.png"
                recent_img_path = images_dir / recent_img_filename
                plt.savefig(recent_img_path, dpi=300)
                print(f"已將近一年趨勢圖保存至: {recent_img_path}")
    else:
        print("警告: 在數據中未找到 'Taiwan' 列！")
        print("可用的列名:", df_tic.columns.tolist())
        print("請檢查數據格式並相應地調整程式碼。")


except requests.exceptions.RequestException as e:
    print(f"下載文件時發生錯誤: {e}")
except Exception as e:
    print(f"讀取或處理文件時發生錯誤: {e}")
    print("請檢查文件 URL 是否正確，以及文件格式、分隔符號、列名等參數是否與文件內容匹配。")
    import traceback
    print(traceback.format_exc()) # 顯示詳細的錯誤信息