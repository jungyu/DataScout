# -*- coding: utf-8 -*-
"""
DataScout 圖表字型配置模組
提供統一的中文字型支援
"""

import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import platform
import os
from typing import List, Dict, Optional


class ChartFontManager:
    """圖表字型管理器"""
    
    def __init__(self):
        self.system = platform.system().lower()
        self.chinese_fonts = self._detect_chinese_fonts()
        self.default_font = self._get_default_font()
        
    def _detect_chinese_fonts(self) -> List[str]:
        """偵測系統可用的中文字型"""
        all_fonts = [f.name for f in fm.fontManager.ttflist]
        
        # 常見中文字型關鍵字
        chinese_keywords = [
            'hei', 'ming', 'song', 'yuan', '黑', '宋', '圓', '明',
            'chinese', 'gothic', 'tc', 'cn', 'jp', 'kr', 'cjk',
            'pingfang', 'microsoft jhenghei', 'microsoft yahei',
            'noto sans cjk', 'noto sans tc', 'noto sans sc',
            'taipei sans', 'apple gothic', 'heiti'
        ]
        
        chinese_fonts = []
        for font in all_fonts:
            if any(keyword in font.lower() for keyword in chinese_keywords):
                chinese_fonts.append(font)
                
        return chinese_fonts
    
    def _get_default_font(self) -> str:
        """根據系統平台選擇預設中文字型，優先使用系統中實際可用的字體"""
        if self.system == 'darwin':  # macOS
            priority_fonts = [
                'Heiti TC',
                'STHeiti',  
                'Apple LiGothic',
                'Apple LiSung',
                'Hei',
                'Kai',
                'Arial Unicode MS'
            ]
        elif self.system == 'windows':  # Windows
            priority_fonts = [
                'Noto Sans TC',
                'Noto Sans CJK TC',
                'Microsoft JhengHei',
                'Microsoft YaHei',
                'SimHei',
                'SimSun'
            ]
        else:  # Linux
            priority_fonts = [
                'Noto Sans TC',
                'Noto Sans CJK TC',
                'Noto Sans CJK SC',
                'WenQuanYi Micro Hei',
                'AR PL UMing TW'
            ]
        
        # 查找可用的優先字型
        for font in priority_fonts:
            if font in self.chinese_fonts:
                return font
                
        # 如果沒有找到優先字型，使用第一個可用的中文字型
        if self.chinese_fonts:
            return self.chinese_fonts[0]
            
        # 最後備用方案
        return 'DejaVu Sans'
    
    def setup_matplotlib_fonts(self) -> None:
        """設定 matplotlib 中文字型支援，優先使用思源黑體字"""
        try:
            # 設定字型優先順序，優先使用系統實際可用的字體
            font_priority = [
                self.default_font,
                'Heiti TC',
                'Apple LiSung',
                'Apple LiGothic',
                'STHeiti',
                'Arial Unicode MS',
                'DejaVu Sans'
            ]
            
            plt.rcParams['font.family'] = font_priority
            plt.rcParams['axes.unicode_minus'] = False
            
            # 設定字型大小
            plt.rcParams['font.size'] = 12
            plt.rcParams['axes.titlesize'] = 14
            plt.rcParams['axes.labelsize'] = 12
            plt.rcParams['xtick.labelsize'] = 10
            plt.rcParams['ytick.labelsize'] = 10
            plt.rcParams['legend.fontsize'] = 11
            
            print(f"Matplotlib 中文字型已設定完成，優先使用: {self.default_font}")
            
        except Exception as e:
            print(f"設定 matplotlib 字型時發生錯誤: {e}")
            # 使用基本配置作為備用
            plt.rcParams['font.family'] = ['DejaVu Sans']
            plt.rcParams['axes.unicode_minus'] = False
    
    def get_web_font_config(self) -> Dict[str, str]:
        """取得網頁字型配置，優先使用思源黑體字"""
        return {
            'primary': "'Noto Sans TC', 'Noto Sans CJK TC', 'PingFang TC', 'Microsoft JhengHei', 'Heiti TC', sans-serif",
            'fallback': "Arial, sans-serif",
            'google_fonts_url': "https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@300;400;500;600;700&display=swap"
        }
    
    def get_apexcharts_font_config(self) -> Dict:
        """取得 ApexCharts 字型配置"""
        web_fonts = self.get_web_font_config()
        
        return {
            'chart': {
                'fontFamily': web_fonts['primary'],
                'fontSize': '14px'
            },
            'title': {
                'style': {
                    'fontFamily': web_fonts['primary'],
                    'fontSize': '16px',
                    'fontWeight': '600'
                }
            },
            'legend': {
                'fontFamily': web_fonts['primary'],
                'fontSize': '12px'
            },
            'dataLabels': {
                'style': {
                    'fontFamily': web_fonts['primary'],
                    'fontSize': '11px'
                }
            },
            'xaxis': {
                'labels': {
                    'style': {
                        'fontFamily': web_fonts['primary'],
                        'fontSize': '12px'
                    }
                },
                'title': {
                    'style': {
                        'fontFamily': web_fonts['primary'],
                        'fontSize': '13px'
                    }
                }
            },
            'yaxis': {
                'labels': {
                    'style': {
                        'fontFamily': web_fonts['primary'],
                        'fontSize': '12px'
                    }
                },
                'title': {
                    'style': {
                        'fontFamily': web_fonts['primary'],
                        'fontSize': '13px'
                    }
                }
            },
            'tooltip': {
                'style': {
                    'fontFamily': web_fonts['primary'],
                    'fontSize': '12px'
                }
            }
        }
    
    def print_font_info(self) -> None:
        """列印字型資訊"""
        print(f"系統平台: {self.system}")
        print(f"預設中文字型: {self.default_font}")
        print(f"可用中文字型數量: {len(self.chinese_fonts)}")
        if self.chinese_fonts:
            print("可用中文字型列表:")
            for i, font in enumerate(self.chinese_fonts[:10], 1):  # 只顯示前10個
                print(f"  {i}. {font}")
            if len(self.chinese_fonts) > 10:
                print(f"  ... 還有 {len(self.chinese_fonts) - 10} 個字型")


# 全域字型管理器實例
font_manager = ChartFontManager()


def setup_chinese_fonts():
    """設定中文字型支援的便捷函數"""
    font_manager.setup_matplotlib_fonts()
    return font_manager


def get_chart_font_config():
    """取得圖表字型配置的便捷函數"""
    return font_manager.get_apexcharts_font_config()


if __name__ == "__main__":
    # 測試腳本
    manager = setup_chinese_fonts()
    manager.print_font_info()
    
    # 測試 matplotlib 繪圖
    import numpy as np
    
    x = np.linspace(0, 10, 100)
    y = np.sin(x)
    
    plt.figure(figsize=(10, 6))
    plt.plot(x, y, label='正弦波')
    plt.title('中文字型測試圖表')
    plt.xlabel('時間軸')
    plt.ylabel('數值')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    print("正在儲存測試圖表...")
    plt.savefig('/Users/aaron/Projects/DataScout/test_chinese_font.png', dpi=150, bbox_inches='tight')
    print("測試圖表已儲存為 test_chinese_font.png")
    plt.show()
