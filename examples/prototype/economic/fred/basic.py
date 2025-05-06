import pandas as pd
import pandas_datareader.data as web
import datetime
import matplotlib.pyplot as plt
from pathlib import Path
import os

# 定義要取的 FRED 指標 ID
fred_ids = ["UNRATE", "GDP", "DFF", "T10YIE", "WALCL"]

# 設定時間範圍 (例如：從 2000 年至今)
start_date = datetime.datetime(2000, 1, 1)
end_date = datetime.datetime.now() # 取到今天

# 確保目標目錄存在
data_dir = Path("../data")
images_dir = Path("../images")
data_dir.mkdir(exist_ok=True)
images_dir.mkdir(exist_ok=True)

# 取得目前日期作為檔案名稱的一部分
today_str = datetime.datetime.now().strftime("%Y%m%d")

# 使用 web.DataReader 從 FRED 獲取數據
try:
    fred_data = web.DataReader(fred_ids, 'fred', start_date, end_date)

    # 打印前幾行數據查看
    print("從 FRED 獲取的數據：")
    print(fred_data.head())

    # 打印數據的後幾行和基本資訊
    print("\n數據基本資訊：")
    fred_data.info()
    
    # 保存完整數據集到 CSV 檔案
    csv_filename = f"fred_economic_indicators_{today_str}.csv"
    csv_path = data_dir / csv_filename
    fred_data.to_csv(csv_path)
    print(f"\n已將完整數據保存至: {csv_path}")
    
    # 為每個指標創建單獨的圖表
    for indicator in fred_ids:
        if indicator in fred_data.columns:
            plt.figure(figsize=(12, 6))
            
            # 繪製指標數據
            indicator_data = fred_data[indicator].dropna()
            indicator_data.plot(title=f'FRED {indicator} 指標趨勢')
            
            plt.grid(True)
            plt.tight_layout()
            
            # 保存圖表
            img_filename = f"fred_{indicator}_trend_{today_str}.png"
            img_path = images_dir / img_filename
            plt.savefig(img_path, dpi=300)
            print(f"已將 {indicator} 趨勢圖保存至: {img_path}")
            
            # 單獨保存這個指標的數據
            indiv_csv_filename = f"fred_{indicator}_{today_str}.csv"
            indiv_csv_path = data_dir / indiv_csv_filename
            indicator_data.to_frame().to_csv(indiv_csv_path)
            print(f"已將 {indicator} 數據保存至: {indiv_csv_path}")
            
            # 如果有足夠的数据，创建近一年的趋势图
            if not indicator_data.empty:
                one_year_ago = indicator_data.index.max() - pd.DateOffset(years=1)
                recent_data = indicator_data[indicator_data.index >= one_year_ago]
                
                if not recent_data.empty:
                    plt.figure(figsize=(12, 6))
                    recent_data.plot(title=f'FRED {indicator} 近一年趨勢')
                    plt.grid(True)
                    plt.tight_layout()
                    
                    # 保存近一年趨勢圖
                    recent_img_filename = f"fred_{indicator}_recent_trend_{today_str}.png"
                    recent_img_path = images_dir / recent_img_filename
                    plt.savefig(recent_img_path, dpi=300)
                    print(f"已將 {indicator} 近一年趨勢圖保存至: {recent_img_path}")
    
    # 創建一個包含所有指標的組合圖表（每個指標一個子圖）
    fig, axes = plt.subplots(len(fred_ids), 1, figsize=(12, 4*len(fred_ids)), sharex=True)
    for i, indicator in enumerate(fred_ids):
        if indicator in fred_data.columns:
            indicator_data = fred_data[indicator].dropna()
            indicator_data.plot(ax=axes[i], title=f'FRED {indicator}')
            axes[i].grid(True)
    
    plt.tight_layout()
    combined_img_filename = f"fred_all_indicators_{today_str}.png"
    combined_img_path = images_dir / combined_img_filename
    plt.savefig(combined_img_path, dpi=300)
    print(f"已將組合趨勢圖保存至: {combined_img_path}")

except Exception as e:
    print(f"獲取或處理 FRED 數據時發生錯誤: {e}")
    print("請確認指標 ID 是否正確，以及網路連線是否正常。")
    import traceback
    print(traceback.format_exc()) # 顯示詳細的錯誤信息

# 你也可以一次取一個指標（作為示範）
try:
    unrate_data = web.DataReader("UNRATE", 'fred', start_date, end_date)
    print("\n失業率數據：")
    print(unrate_data.head())
    
    # 額外保存失業率數據（如果上面沒有處理過）
    if "UNRATE" not in fred_ids:
        unrate_csv_path = data_dir / f"fred_UNRATE_{today_str}.csv"
        unrate_data.to_csv(unrate_csv_path)
        print(f"已將失業率數據單獨保存至: {unrate_csv_path}")
        
        # 繪製失業率趨勢圖
        plt.figure(figsize=(12, 6))
        unrate_data.plot(title='美國失業率趨勢')
        plt.grid(True)
        plt.tight_layout()
        
        unrate_img_path = images_dir / f"fred_UNRATE_trend_{today_str}.png"
        plt.savefig(unrate_img_path, dpi=300)
        print(f"已將失業率趨勢圖保存至: {unrate_img_path}")
except Exception as e:
    print(f"獲取失業率數據時發生錯誤: {e}")