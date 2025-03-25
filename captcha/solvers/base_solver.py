from abc import ABC, abstractmethod
import logging
from typing import Union, Dict, Any, Optional

class BaseCaptchaSolver(ABC):
    """所有驗證碼解決器的基礎抽象類"""
    
    def __init__(self, driver, config: Optional[Dict[str, Any]] = None):
        """
        初始化解決器
        
        Args:
            driver: WebDriver實例
            config: 配置選項字典
        """
        self.driver = driver
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        self.success_count = 0
        self.failure_count = 0
        self.setup()
        
    def setup(self):
        """設置解決器，可由子類覆寫"""
        pass
        
    @abstractmethod
    def detect(self) -> bool:
        """
        檢測頁面上是否存在此類型的驗證碼
        
        Returns:
            bool: 是否檢測到驗證碼
        """
        pass
        
    @abstractmethod
    def solve(self) -> bool:
        """
        解決驗證碼
        
        Returns:
            bool: 驗證碼是否成功解決
        """
        pass
        
    def report_result(self, success: bool):
        """
        報告驗證碼解決結果，用於統計和學習
        
        Args:
            success: 是否成功解決
        """
        if success:
            self.success_count += 1
        else:
            self.failure_count += 1
        
        self.logger.info(
            f"驗證碼解決結果: {success}, 成功率: "
            f"{self.success_count/(self.success_count+self.failure_count):.2%}"
        )
        
    def save_sample(self, data: Any, success: bool = False):
        """
        保存驗證碼樣本以供將來分析或訓練
        
        Args:
            data: 驗證碼數據（通常是圖像）
            success: 樣本是否為成功解決的樣本
        """
        if not self.config.get('save_samples', False):
            return
            
        import os
        import time
        
        # 決定保存路徑
        base_dir = self.config.get('sample_dir', '../captchas')
        solver_type = self.__class__.__name__.lower().replace('solver', '')
        status = 'success' if success else 'failed'
        
        # 創建目錄
        save_dir = os.path.join(base_dir, solver_type, status)
        os.makedirs(save_dir, exist_ok=True)
        
        # 保存樣本
        filename = f"{int(time.time())}_{hash(str(data))}.png"
        file_path = os.path.join(save_dir, filename)
        
        try:
            if hasattr(data, 'save'):  # PIL Image
                data.save(file_path)
            elif isinstance(data, bytes):  # Bytes data
                with open(file_path, 'wb') as f:
                    f.write(data)
            else:
                self.logger.warning(f"無法保存未知格式的驗證碼樣本: {type(data)}")
        except Exception as e:
            self.logger.error(f"保存驗證碼樣本失敗: {str(e)}")