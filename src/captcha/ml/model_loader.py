import os
import logging
from typing import Dict, Any, Optional, List, Tuple
import numpy as np
from PIL import Image
import time

class ModelLoader:
    """機器學習模型加載工具"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化模型加載器
        
        Args:
            config: 配置選項
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.models = {}
        
        # 是否啟用機器學習
        self.enabled = config.get('enable_machine_learning', False)
        
        if self.enabled:
            self._load_models()
    
    def _load_models(self):
        """加載所有配置的模型"""
        if not self.enabled:
            return
            
        try:
            # 模型目錄
            model_dir = self.config.get('model_dir', '../models')
            max_retries = self.config.get('max_load_retries', 3)
            retry_delay = self.config.get('retry_delay', 1)
            
            for retry in range(max_retries):
                try:
                    # 加載文字識別模型
                    if 'text_recognition' in self.config:
                        self._load_text_recognition_model(model_dir)
                        
                    # 加載物件檢測模型
                    if 'object_detection' in self.config:
                        self._load_object_detection_model(model_dir)
                    
                    # 檢查模型版本
                    self._check_model_versions()
                    
                    # 預熱模型
                    self._warmup_models()
                    
                    self.logger.info(f"已加載 {len(self.models)} 個機器學習模型")
                    break
                    
                except Exception as e:
                    if retry < max_retries - 1:
                        self.logger.warning(f"加載模型失敗，將在 {retry_delay} 秒後重試: {str(e)}")
                        time.sleep(retry_delay)
                    else:
                        raise
                        
        except Exception as e:
            self.logger.error(f"加載模型時出錯: {str(e)}")
            self.enabled = False
    
    def _check_model_versions(self):
        """檢查已加載模型的版本"""
        for model_name, model_info in self.models.items():
            if 'version' in model_info:
                expected_version = self.config.get(f'{model_name}_version')
                if expected_version and model_info['version'] != expected_version:
                    self.logger.warning(f"{model_name} 版本不符: 期望 {expected_version}，實際 {model_info['version']}")
    
    def _warmup_models(self):
        """預熱模型，以提高首次推理速度"""
        try:
            # 創建示例輸入
            dummy_image = Image.new('RGB', (100, 30), color='white')
            
            # 預熱文字識別模型
            if 'text_recognition' in self.models:
                self.recognize_text(dummy_image)
                
            # 預熱物件檢測模型
            if 'object_detection' in self.models:
                self.detect_objects(dummy_image)
                
            self.logger.info("模型預熱完成")
            
        except Exception as e:
            self.logger.warning(f"模型預熱過程中出現錯誤: {str(e)}")
    
    def unload_models(self):
        """卸載所有模型以釋放資源"""
        try:
            for model_name, model_info in self.models.items():
                if 'model' in model_info:
                    del model_info['model']
            self.models.clear()
            self.enabled = False
            self.logger.info("已卸載所有模型")
        except Exception as e:
            self.logger.error(f"卸載模型時出錯: {str(e)}")
    
    def _load_text_recognition_model(self, model_dir: str):
        """加載文字識別模型"""
        try:
            # 模型配置
            model_config = self.config.get('text_recognition', {})
            model_path = os.path.join(model_dir, model_config.get('model_path', 'text_recognition.pth'))
            
            # 檢查模型文件是否存在
            if not os.path.exists(model_path):
                self.logger.warning(f"文字識別模型文件不存在: {model_path}")
                return
            
            # 加載模型（這裡是示例，實際加載方式取決於模型類型）
            if model_config.get('model_format', 'pytorch') == 'pytorch':
                try:
                    import torch
                    
                    # 檢查是否可以使用GPU
                    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
                    
                    # 加載模型
                    model = torch.load(model_path, map_location=device)
                    
                    # 設置為評估模式
                    model.eval()
                    
                    self.models['text_recognition'] = {
                        'model': model,
                        'device': device,
                        'char_set': model_config.get('char_set', '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'),
                        'image_size': model_config.get('image_size', [100, 30])
                    }
                    
                    self.logger.info(f"成功加載文字識別模型: {model_path}")
                    
                except ImportError:
                    self.logger.error("無法導入PyTorch，文字識別模型加載失敗")
                    
            else:
                self.logger.warning(f"不支持的模型格式: {model_config.get('model_format')}")
                
        except Exception as e:
            self.logger.error(f"加載文字識別模型時出錯: {str(e)}")
    
    def _load_object_detection_model(self, model_dir: str):
        """加載物件檢測模型"""
        try:
            # 模型配置
            model_config = self.config.get('object_detection', {})
            model_path = os.path.join(model_dir, model_config.get('model_path', 'object_detection.pth'))
            
            # 檢查模型文件是否存在
            if not os.path.exists(model_path):
                self.logger.warning(f"物件檢測模型文件不存在: {model_path}")
                return
            
            # 加載模型（這裡是示例，實際加載方式取決於模型類型）
            if model_config.get('model_format', 'pytorch') == 'pytorch':
                try:
                    import torch
                    
                    # 檢查是否可以使用GPU
                    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
                    
                    # 加載模型
                    model = torch.load(model_path, map_location=device)
                    
                    # 設置為評估模式
                    model.eval()
                    
                    self.models['object_detection'] = {
                        'model': model,
                        'device': device,
                        'confidence_threshold': model_config.get('confidence_threshold', 0.5),
                        'nms_threshold': model_config.get('nms_threshold', 0.4),
                        'classes': model_config.get('classes', [])
                    }
                    
                    self.logger.info(f"成功加載物件檢測模型: {model_path}")
                    
                except ImportError:
                    self.logger.error("無法導入PyTorch，物件檢測模型加載失敗")
                    
            else:
                self.logger.warning(f"不支持的模型格式: {model_config.get('model_format')}")
                
        except Exception as e:
            self.logger.error(f"加載物件檢測模型時出錯: {str(e)}")
    
    def recognize_text(self, image: Image.Image) -> Tuple[str, float]:
        """
        使用文字識別模型識別圖像中的文字
        
        Args:
            image: 輸入圖像
            
        Returns:
            識別的文字和置信度
        """
        if not self.enabled or 'text_recognition' not in self.models:
            return "", 0.0
            
        try:
            import torch
            import torchvision.transforms as transforms
            
            # 獲取模型信息
            model_info = self.models['text_recognition']
            model = model_info['model']
            device = model_info['device']
            char_set = model_info['char_set']
            image_size = model_info['image_size']
            
            # 預處理圖像
            transform = transforms.Compose([
                transforms.Resize(image_size),
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.5], std=[0.5])
            ])
            
            # 轉換圖像
            if image.mode != 'L':
                image = image.convert('L')  # 轉為灰度
                
            image_tensor = transform(image).unsqueeze(0).to(device)
            
            # 推理
            with torch.no_grad():
                outputs = model(image_tensor)
                
            # 後處理結果（示例，實際處理方式依賴於模型結構和輸出格式）
            if isinstance(outputs, tuple):
                probs, indices = outputs
                confidence = torch.mean(torch.max(probs, dim=2)[0]).item()
                indices = indices.squeeze().cpu().numpy()
                
                # 將索引轉換為字符
                text = ''.join([char_set[idx] for idx in indices if idx < len(char_set)])
                
                return text, confidence
            else:
                self.logger.warning("不支持的模型輸出格式")
                return "", 0.0
                
        except Exception as e:
            self.logger.error(f"文字識別推理時出錯: {str(e)}")
            return "", 0.0
    
    def detect_objects(self, image: Image.Image, target_class: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        使用物件檢測模型檢測圖像中的物體
        
        Args:
            image: 輸入圖像
            target_class: 目標類別，None表示檢測所有類別
            
        Returns:
            檢測到的物體列表，每個物體包含box座標、得分和類別
        """
        if not self.enabled or 'object_detection' not in self.models:
            return []
            
        try:
            import torch
            import torchvision.transforms as transforms
            
            # 獲取模型信息
            model_info = self.models['object_detection']
            model = model_info['model']
            device = model_info['device']
            confidence_threshold = model_info['confidence_threshold']
            classes = model_info['classes']
            
            # 預處理圖像
            transform = transforms.Compose([
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
            ])
            
            # 轉換圖像
            if image.mode != 'RGB':
                image = image.convert('RGB')
                
            image_tensor = transform(image).unsqueeze(0).to(device)
            
            # 推理
            with torch.no_grad():
                predictions = model(image_tensor)
                
            # 過濾預測結果
            detections = []
            
            # 處理預測結果（修復：添加額外的檢查）
            if isinstance(predictions, list) and len(predictions) > 0:
                prediction = predictions[0]  # 批次中的第一個圖像
                
                # 檢查預測結果是否包含必要的鍵
                if not all(key in prediction for key in ['boxes', 'scores', 'labels']):
                    self.logger.warning("預測結果缺少必要的鍵 (boxes/scores/labels)")
                    return []
                
                # 確保預測結果中有檢測到物體
                if len(prediction['boxes']) == 0:
                    return []
                
                # 處理每個檢測到的物體
                for i, box in enumerate(prediction['boxes']):
                    # 檢查索引是否有效
                    if i >= len(prediction['scores']) or i >= len(prediction['labels']):
                        continue
                    
                    score = prediction['scores'][i].item()
                    class_idx = prediction['labels'][i].item()
                    
                    # 過濾低置信度預測
                    if score < confidence_threshold:
                        continue
                    
                    # 獲取類別名稱（修復：確保索引合法）
                    if 0 < class_idx <= len(classes):
                        class_name = classes[class_idx - 1]
                    else:
                        class_name = f"class_{class_idx}"
                    
                    # 如果指定了目標類別，只返回該類別的預測
                    if target_class and class_name != target_class:
                        continue
                    
                    # 添加到檢測結果（修復：確保box可以轉換為列表）
                    try:
                        box_list = box.cpu().numpy().tolist()
                        detections.append({
                            'box': box_list,
                            'score': score,
                            'class': class_name
                        })
                    except Exception as e:
                        self.logger.warning(f"無法處理檢測框數據: {str(e)}")
            
            return detections
            
        except Exception as e:
            self.logger.error(f"物件檢測推理時出錯: {str(e)}")
            return []