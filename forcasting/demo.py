#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股價預測系統演示腳本

這個腳本展示了如何使用股價預測系統的各種功能
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from stock_predictor import StockPredictor
import pandas as pd


def demo_basic_usage():
    """演示基本用法"""
    print("=== 基本用法演示 ===")
    
    # 創建預測器
    predictor = StockPredictor()
    
    # 運行完整流程
    results = predictor.run_full_pipeline(
        symbol='AAPL',
        optimize_params=False
    )
    
    print("基本用法演示完成!")
    return results


def demo_step_by_step():
    """演示步驟化使用"""
    print("\n=== 步驟化使用演示 ===")
    
    predictor = StockPredictor()
    
    # 步驟 1: 獲取數據
    print("1. 獲取數據...")
    data = predictor.fetch_data('MSFT')
    print(f"獲取了 {len(data)} 行數據")
    
    # 步驟 2: 特徵工程
    print("2. 特徵工程...")
    engineered_data = predictor.engineer_features()
    print(f"工程後有 {engineered_data.shape[1]} 個欄位")
    
    # 步驟 3: 準備特徵
    print("3. 準備特徵...")
    features, target = predictor.prepare_features()
    print(f"準備了 {features.shape[1]} 個特徵")
    
    # 步驟 4: 分割數據
    print("4. 分割數據...")
    X_train, X_test, y_train, y_test = predictor.split_data()
    print(f"訓練集: {len(X_train)}, 測試集: {len(X_test)}")
    
    # 步驟 5: 訓練模型
    print("5. 訓練模型...")
    model = predictor.train_model(X_train, y_train)
    print("模型訓練完成")
    
    # 步驟 6: 評估模型
    print("6. 評估模型...")
    results = predictor.evaluate_model(X_test, y_test)
    print(f"測試準確率: {results['accuracy']:.4f}")
    
    # 步驟 7: 回測
    print("7. 回測分析...")
    backtest_results, metrics = predictor.run_backtest()
    print(f"策略收益: {metrics['total_strategy_return']:.4f}")
    
    # 步驟 8: 預測未來
    print("8. 預測未來...")
    predictions = predictor.predict_future()
    for i, pred in enumerate(predictions):
        print(f"未來第{i+1}天: {pred['prediction']} (概率: {pred['probability']:.4f})")
    
    print("步驟化演示完成!")


def demo_multiple_stocks():
    """演示多個股票的預測"""
    print("\n=== 多股票預測演示 ===")
    
    stocks = ['AAPL', 'GOOGL', 'MSFT', 'TSLA']
    results_summary = []
    
    for stock in stocks:
        print(f"\n正在處理 {stock}...")
        try:
            predictor = StockPredictor()
            results = predictor.run_full_pipeline(
                symbol=stock,
                optimize_params=False
            )
            
            # 收集結果
            summary = {
                'symbol': stock,
                'accuracy': results['evaluation']['accuracy'],
                'roc_auc': results['evaluation']['roc_auc'],
                'strategy_return': results['backtest']['total_strategy_return'],
                'sharpe_ratio': results['backtest']['sharpe_ratio']
            }
            results_summary.append(summary)
            
        except Exception as e:
            print(f"處理 {stock} 時出錯: {e}")
            continue
    
    # 輸出匯總結果
    if results_summary:
        summary_df = pd.DataFrame(results_summary)
        print("\n=== 多股票結果匯總 ===")
        print(summary_df.round(4))
        
        # 保存匯總結果
        summary_df.to_csv('/Users/aaron/Projects/DataScout/data/output/multi_stock_summary.csv', index=False)
        print("匯總結果已保存")


def demo_custom_config():
    """演示自定義配置"""
    print("\n=== 自定義配置演示 ===")
    
    # 自定義配置
    custom_config = {
        'default_symbol': 'NVDA',
        'start_date': '2020-01-01',
        'end_date': '2024-12-31',
        'split_date': '2024-01-01'
    }
    
    predictor = StockPredictor(config=custom_config)
    
    print("使用自定義配置運行...")
    results = predictor.run_full_pipeline(optimize_params=False)
    
    print("自定義配置演示完成!")


def demo_model_persistence():
    """演示模型保存和加載"""
    print("\n=== 模型持久化演示 ===")
    
    # 訓練並保存模型
    print("訓練新模型...")
    predictor = StockPredictor()
    predictor.run_full_pipeline('AAPL', optimize_params=False)
    
    # 創建新的預測器並加載模型
    print("加載已保存的模型...")
    new_predictor = StockPredictor()
    try:
        feature_names = new_predictor.load_model()
        print("模型加載成功!")
        print(f"模型包含 {len(feature_names)} 個特徵")
        
        # 使用加載的模型進行預測
        # 注意：需要先準備相同格式的數據
        new_predictor.fetch_data('AAPL')
        new_predictor.engineer_features()
        new_predictor.prepare_features()
        
        predictions = new_predictor.predict_future()
        print("使用加載的模型預測成功!")
        
    except Exception as e:
        print(f"模型加載失敗: {e}")
    
    print("模型持久化演示完成!")


def main():
    """主演示函數"""
    print("🚀 股價預測系統演示")
    print("=" * 50)
    
    # 選擇要運行的演示
    demos = {
        '1': ('基本用法', demo_basic_usage),
        '2': ('步驟化使用', demo_step_by_step),
        '3': ('多股票預測', demo_multiple_stocks),
        '4': ('自定義配置', demo_custom_config),
        '5': ('模型持久化', demo_model_persistence),
        'all': ('運行所有演示', None)
    }
    
    print("可用的演示:")
    for key, (name, _) in demos.items():
        print(f"  {key}: {name}")
    
    choice = input("\n請選擇要運行的演示 (默認: 1): ").strip() or '1'
    
    if choice == 'all':
        # 運行所有演示
        for key, (name, func) in demos.items():
            if func is not None:
                try:
                    print(f"\n{'='*20} {name} {'='*20}")
                    func()
                except Exception as e:
                    print(f"演示 {name} 失敗: {e}")
                    continue
    elif choice in demos and demos[choice][1] is not None:
        # 運行選定的演示
        name, func = demos[choice]
        print(f"\n運行演示: {name}")
        try:
            func()
        except Exception as e:
            print(f"演示失敗: {e}")
    else:
        print("無效的選擇!")
        return
    
    print("\n" + "="*50)
    print("演示完成! 🎉")
    print("\n📊 查看輸出文件:")
    print("  - 圖表: /Users/aaron/Projects/DataScout/data/output/")
    print("  - 模型: /Users/aaron/Projects/DataScout/data/models/")
    print("  - 日誌: /Users/aaron/Projects/DataScout/data/output/stock_prediction.log")
    
    print("\n⚠️  免責聲明:")
    print("此系統僅供學習研究用途，不構成投資建議。")
    print("實際投資需謹慎考慮風險。")


if __name__ == "__main__":
    main()
