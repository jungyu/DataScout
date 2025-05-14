"""
Gemini API 客戶端模組

用於與 Google Gemini API 交互，處理圖像分析請求
"""

import os
import logging
import asyncio
from typing import Union, Optional, BinaryIO, Dict, Any

logger = logging.getLogger(__name__)

class GeminiClient:
    """Google Gemini API 客戶端，用於處理圖像分析請求"""
    
    def __init__(self):
        """初始化 Gemini 客戶端，設置 API 金鑰並配置模型"""
        from telegram_bot.config import GEMINI_API_KEY
        self.api_key = GEMINI_API_KEY
        
        if not self.api_key:
            logger.error("Gemini API 金鑰未設置，請在 .env 文件中設置 GEMINI_API_KEY")
            raise ValueError("Gemini API 金鑰未設置")
            
        # 延遲導入 google.generativeai，以避免在不需要時載入它
        import google.generativeai as genai
        
        # 配置 API
        genai.configure(api_key=self.api_key)
        
        # 初始化模型 - 支援圖像的模型
        # 更新為最新的 Gemini 模型，取代已棄用的 gemini-pro-vision
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        
        logger.info("Gemini 客戶端初始化完成")
    
    async def analyze_image(self, 
                           image_path: str, 
                           prompt: str = "描述這張圖片中的內容") -> str:
        """
        分析圖像並返回描述
        
        Args:
            image_path: 圖像文件路徑
            prompt: 提示詞，告訴 Gemini 如何解讀圖像
            
        Returns:
            str: 圖像分析結果
        """
        try:
            # 在非同步函數中執行同步操作
            # 使用 run_in_executor 以避免阻塞事件循環
            loop = asyncio.get_event_loop()
            
            # 在執行器中處理圖像和 API 請求
            result = await loop.run_in_executor(None, self._process_image, image_path, prompt)
            
            return result
            
        except Exception as e:
            logger.error(f"圖像分析失敗: {str(e)}", exc_info=True)
            return f"圖像分析時發生錯誤: {str(e)}"
    
    def _process_image(self, image_path: str, prompt: str) -> str:
        """
        處理圖像的同步方法，供 run_in_executor 使用
        
        Args:
            image_path: 圖像文件路徑
            prompt: 提示詞
            
        Returns:
            str: 圖像分析結果
        """
        try:
            # 導入必要的庫
            from PIL import Image
            
            # 讀取圖像
            img = Image.open(image_path)
            
            # 確保圖像處於 RGB 模式 (Gemini 需要)
            if img.mode != "RGB":
                img = img.convert("RGB")
                
            # 調用 Gemini API
            response = self.model.generate_content([prompt, img])
            
            # 提取並返回結果文本
            if response.text:
                logger.info("圖像分析成功")
                return response.text
            else:
                logger.warning("圖像分析返回空結果")
                return "無法解讀圖像內容"
                
        except Exception as e:
            logger.error(f"處理圖像時發生錯誤: {str(e)}")
            raise e
