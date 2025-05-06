import matplotlib.font_manager as fm

# 找出所有包含中文字的字型名稱
# 這裡使用一些常見的中文/東亞字型名稱關鍵字來過濾
all_fonts = [f.name for f in fm.fontManager.ttflist]
chinese_fonts = [f for f in all_fonts if any(x in f.lower() for x in ['hei', 'ming', 'song', 'yuan', '黑', '宋', '圓', '明', 'chinese', 'gothic', 'tc', 'cn', 'jp', 'kr', 'cjk', 'pingfang', 'microsoft jhenghei', 'microsoft yahei', 'noto sans cjk'])]

print("系統可用中文字型:")
if chinese_fonts:
    for font in chinese_fonts:
        print(f"- {font}")
else:
    print("警告：未偵測到常見的中文字型。您可能需要安裝中文字型。")