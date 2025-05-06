import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import matplotlib as mpl

# 設定中文字型支援
# 嘗試使用系統中存在的常見中文字型名稱列表作為優先順序
plt.rcParams['font.family'] = ['Noto Sans Gothic', 'Taipei Sans TC Beta', 'AppleGothic', 'Heiti TC']

# 解決負號顯示為方框的問題 (與中文字體問題常一起出現)
plt.rcParams['axes.unicode_minus'] = False

print("Matplotlib 已設定中文字型。")

# --- 測試繪圖範例 ---
# 建立一些測試數據
x = [1, 2, 3, 4, 5]
y = [2, 4, 6, 8, 10]

plt.plot(x, y)
plt.title('測試中文標題')
plt.xlabel('X 軸標籤')
plt.ylabel('Y 軸標籤')
plt.legend(['測試圖例']) # 使用 legend 需要先定義 label

plt.show()