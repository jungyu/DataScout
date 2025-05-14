#!/usr/bin/env python3
"""
DataScout Telegram Bot 啟動腳本
"""

import os
import sys
import logging
import argparse
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

def setup_logging(level):
    """設定日誌級別"""
    logging_levels = {
        "debug": logging.DEBUG,
        "info": logging.INFO,
        "warning": logging.WARNING,
        "error": logging.ERROR
    }
    log_level = logging_levels.get(level.lower(), logging.INFO)
    
    # 配置日誌
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=log_level
    )
    
    # 設定 urllib3 日誌級別 (避免過多的連接日誌)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)

def check_environment():
    """檢查環境變數是否已設定"""
    required_vars = ["DATASCOUT_BOT_TOKEN"]
    missing = [var for var in required_vars if not os.environ.get(var)]
    
    if missing:
        print(f"錯誤：缺少必要的環境變數: {', '.join(missing)}")
        print("請確保已設定環境變數或在 .env 文件中配置")
        sys.exit(1)
    
    # 檢查選項配置
    if not os.environ.get("AUTHORIZED_USERS") and os.environ.get("REQUIRE_AUTH", "").lower() in ("true", "1", "yes"):
        print("警告：已啟用授權檢查，但未設定授權用戶列表 (AUTHORIZED_USERS)")
        print("將無法使用機器人，除非您是管理員")

def main():
    """主函數"""
    parser = argparse.ArgumentParser(description="啟動 DataScout Telegram Bot")
    parser.add_argument("--log-level", default="info", 
                        choices=["debug", "info", "warning", "error"],
                        help="設定日誌級別")
    args = parser.parse_args()
    
    # 設定日誌
    setup_logging(args.log_level)
    
    # 檢查環境變數
    check_environment()
    
    # 這裡需要在導入 bot 之前檢查環境變數，因為 bot 模組在導入時就會讀取配置
    from telegram_bot.bot import DataScoutBot
    
    print("正在啟動 DataScout Telegram Bot...")
    DataScoutBot.run()

if __name__ == "__main__":
    main()
