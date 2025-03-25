import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

def load_data(file_path):
    """載入爬蟲結果資料"""
    return pd.read_csv(file_path)

def analyze_data(df):
    """執行基本資料分析"""
    summary = {
        "總筆數": len(df),
        "平均值": df.select_dtypes(include=['float64', 'int64']).mean().to_dict(),
        "最大值": df.select_dtypes(include=['float64', 'int64']).max().to_dict(),
        "最小值": df.select_dtypes(include=['float64', 'int64']).min().to_dict()
    }
    return summary

def plot_distributions(df, output_dir):
    """繪製資料分布圖"""
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True)
    
    for column in df.select_dtypes(include=['float64', 'int64']).columns:
        plt.figure(figsize=(10, 6))
        sns.histplot(data=df, x=column)
        plt.title(f'{column} 分布圖')
        plt.savefig(output_dir / f'{column}_distribution.png')
        plt.close()

def main():
    # 設定檔案路徑
    data_path = Path(__file__).parent.parent / "data" / "results.csv"
    output_dir = Path(__file__).parent.parent / "analysis_results"
    
    # 載入資料
    df = load_data(data_path)
    
    # 執行分析
    summary = analyze_data(df)
    print("分析結果摘要：")
    for key, value in summary.items():
        print(f"{key}:", value)
    
    # 繪製圖表
    plot_distributions(df, output_dir)
    print(f"圖表已儲存至: {output_dir}")

if __name__ == "__main__":
    main()
