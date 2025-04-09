#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
音頻處理工具模組

提供音頻處理相關功能，包括：
1. 音頻預處理
2. 音頻增強
3. 音頻分割
4. 語音識別
5. 音頻保存和轉換
"""

import os
import wave
import numpy as np
import logging
import base64
import soundfile as sf
import librosa
import noisereduce as nr
from typing import Optional, Union, List, Tuple, Dict, Any
from dataclasses import dataclass

from .error import AudioProcessError, handle_error

@dataclass
class AudioProcessResult:
    """音頻處理結果數據類"""
    success: bool
    audio: Optional[np.ndarray] = None
    text: Optional[str] = None
    segments: Optional[List[np.ndarray]] = None
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class AudioProcessor:
    """音頻處理工具類"""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        初始化音頻處理器
        
        Args:
            logger: 日誌記錄器
        """
        self.logger = logger or logging.getLogger(__name__)
        
    @handle_error(error_types=(AudioProcessError,))
    def preprocess_audio(
        self,
        audio: Union[str, bytes, np.ndarray]
    ) -> np.ndarray:
        """
        音頻預處理
        
        Args:
            audio: 輸入音頻，可以是文件路徑、字節數據或numpy數組
            
        Returns:
            預處理後的音頻
        """
        try:
            # 轉換為numpy數組
            if isinstance(audio, str):
                audio_data, sr = librosa.load(audio, sr=None)
            elif isinstance(audio, bytes):
                audio_data, sr = librosa.load(audio, sr=None)
            elif isinstance(audio, np.ndarray):
                audio_data = audio.copy()
                sr = 22050  # 假設採樣率為22050
            else:
                raise AudioProcessError("不支持的音頻格式")
                
            # 預加重
            pre_emphasis = 0.97
            emphasized_audio = np.append(
                audio_data[0],
                audio_data[1:] - pre_emphasis * audio_data[:-1]
            )
            
            # 正規化
            normalized_audio = emphasized_audio / np.max(np.abs(emphasized_audio))
            
            return normalized_audio
            
        except Exception as e:
            self.logger.error(f"音頻預處理失敗: {str(e)}")
            raise AudioProcessError(f"音頻預處理失敗: {str(e)}")
            
    @handle_error(error_types=(AudioProcessError,))
    def enhance_audio(self, audio: np.ndarray) -> np.ndarray:
        """
        音頻增強
        
        Args:
            audio: 輸入音頻
            
        Returns:
            增強後的音頻
        """
        try:
            # 降噪
            reduced_noise = nr.reduce_noise(
                y=audio,
                sr=22050,
                stationary=True
            )
            
            # 諧波-打擊樂分離
            y_harmonic, y_percussive = librosa.effects.hpss(reduced_noise)
            
            # 合併
            enhanced_audio = y_harmonic + y_percussive
            
            return enhanced_audio
            
        except Exception as e:
            self.logger.error(f"音頻增強失敗: {str(e)}")
            raise AudioProcessError(f"音頻增強失敗: {str(e)}")
            
    @handle_error(error_types=(AudioProcessError,))
    def segment_audio(self, audio: np.ndarray) -> List[np.ndarray]:
        """
        音頻分割
        
        Args:
            audio: 輸入音頻
            
        Returns:
            分割後的音頻片段列表
        """
        try:
            # 計算能量
            energy = librosa.feature.rms(y=audio)[0]
            
            # 基於能量閾值分割
            threshold = np.mean(energy) * 0.5
            segments = []
            
            start = 0
            for i in range(len(energy)):
                if energy[i] < threshold and i > start:
                    segment = audio[start:i]
                    if len(segment) > 1000:  # 過濾太短的片段
                        segments.append(segment)
                    start = i
                    
            # 添加最後一個片段
            if start < len(audio):
                segment = audio[start:]
                if len(segment) > 1000:
                    segments.append(segment)
                    
            return segments
            
        except Exception as e:
            self.logger.error(f"音頻分割失敗: {str(e)}")
            raise AudioProcessError(f"音頻分割失敗: {str(e)}")
            
    @handle_error(error_types=(AudioProcessError,))
    def recognize_speech(self, audio: np.ndarray) -> str:
        """
        識別音頻中的語音
        
        Args:
            audio: 輸入音頻
            
        Returns:
            識別出的文字
        """
        try:
            # 這裡需要集成語音識別引擎
            # 簡化處理，返回空字符串
            return ""
            
        except Exception as e:
            self.logger.error(f"語音識別失敗: {str(e)}")
            raise AudioProcessError(f"語音識別失敗: {str(e)}")
            
    @handle_error(error_types=(AudioProcessError,))
    def save_audio(
        self,
        audio: np.ndarray,
        path: str,
        sr: int = 22050,
        format: str = "wav"
    ) -> None:
        """
        保存音頻
        
        Args:
            audio: 輸入音頻
            path: 保存路徑
            sr: 採樣率
            format: 音頻格式
        """
        try:
            sf.write(path, audio, sr)
            
        except Exception as e:
            self.logger.error(f"音頻保存失敗: {str(e)}")
            raise AudioProcessError(f"音頻保存失敗: {str(e)}")
            
    @handle_error(error_types=(AudioProcessError,))
    def audio_to_base64(self, audio: np.ndarray) -> str:
        """
        將音頻轉換為Base64編碼
        
        Args:
            audio: 輸入音頻
            
        Returns:
            Base64編碼的音頻數據
        """
        try:
            import base64
            import io
            
            # 保存為WAV格式
            buffer = io.BytesIO()
            sf.write(buffer, audio, 22050, format='wav')
            
            # 轉換為Base64
            return base64.b64encode(buffer.getvalue()).decode('utf-8')
            
        except Exception as e:
            self.logger.error(f"音頻轉Base64失敗: {str(e)}")
            raise AudioProcessError(f"音頻轉Base64失敗: {str(e)}") 