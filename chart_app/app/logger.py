"""
日誌配置模組。

此模組提供了應用程式的日誌配置功能。
"""
import logging
import os
from pathlib import Path
from datetime import datetime

def setup_logging() -> None:
    """設置應用程式的日誌配置。"""
    
    # 確保日誌目錄存在
    log_dir = Path(__file__).parent.parent / "logs"
    log_dir.mkdir(exist_ok=True)
    
    # 建立日誌文件名，包含日期時間
    log_filename = f"app_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    log_path = log_dir / log_filename
    
    # 配置根日誌器
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_path),
            logging.StreamHandler()
        ]
    )
    
    # 應用程式日誌器
    logger = logging.getLogger("chart_app")
    logger.setLevel(logging.INFO)
    
    # 設置第三方庫的日誌級別
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.error").setLevel(logging.INFO)
    
    logger.info(f"日誌記錄初始化完成，日誌文件: {log_path}")
