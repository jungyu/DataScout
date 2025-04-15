#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
音頻指紋偽裝模組

此模組提供音頻指紋偽裝功能，包括：
1. 音頻上下文偽裝
2. 音頻節點偽裝
3. 音頻參數偽裝
"""

from typing import Dict, Any, List
import random
from loguru import logger

from ..utils.exceptions import AntiDetectionException


class AudioSpoofer:
    """音頻指紋偽裝器"""
    
    def __init__(self):
        """初始化音頻指紋偽裝器"""
        # 音頻上下文參數
        self.context_params = {
            "sampleRate": [44100, 48000, 96000, 192000],
            "channelCount": [1, 2, 4, 6, 8],
            "channelCountMode": ["explicit", "max", "clamped-max"],
            "channelInterpretation": ["speakers", "discrete"],
            "latencyHint": ["interactive", "balanced", "playback"]
        }
        
        # 音頻節點參數
        self.node_params = {
            "gain": {
                "min": -1.0,
                "max": 1.0,
                "default": 1.0
            },
            "frequency": {
                "min": 20,
                "max": 20000,
                "default": 440
            },
            "detune": {
                "min": -1200,
                "max": 1200,
                "default": 0
            },
            "Q": {
                "min": 0.0001,
                "max": 1000,
                "default": 1
            }
        }
        
        # 音頻波形類型
        self.waveforms = ["sine", "square", "sawtooth", "triangle"]
        
        # 音頻處理器參數
        self.processor_params = {
            "bufferSize": [256, 512, 1024, 2048, 4096],
            "numberOfInputs": [0, 1, 2, 4, 8],
            "numberOfOutputs": [0, 1, 2, 4, 8],
            "channelCount": [1, 2, 4, 6, 8]
        }
    
    def get_random_audio_fingerprint(self) -> Dict[str, Any]:
        """
        獲取隨機音頻指紋
        
        Returns:
            Dict[str, Any]: 音頻指紋信息
        """
        return {
            "context": {
                "sampleRate": random.choice(self.context_params["sampleRate"]),
                "channelCount": random.choice(self.context_params["channelCount"]),
                "channelCountMode": random.choice(self.context_params["channelCountMode"]),
                "channelInterpretation": random.choice(self.context_params["channelInterpretation"]),
                "latencyHint": random.choice(self.context_params["latencyHint"])
            },
            "nodes": {
                "gain": random.uniform(self.node_params["gain"]["min"], self.node_params["gain"]["max"]),
                "frequency": random.uniform(self.node_params["frequency"]["min"], self.node_params["frequency"]["max"]),
                "detune": random.uniform(self.node_params["detune"]["min"], self.node_params["detune"]["max"]),
                "Q": random.uniform(self.node_params["Q"]["min"], self.node_params["Q"]["max"])
            },
            "waveform": random.choice(self.waveforms),
            "processor": {
                "bufferSize": random.choice(self.processor_params["bufferSize"]),
                "numberOfInputs": random.choice(self.processor_params["numberOfInputs"]),
                "numberOfOutputs": random.choice(self.processor_params["numberOfOutputs"]),
                "channelCount": random.choice(self.processor_params["channelCount"])
            }
        }
    
    def get_consistent_audio_fingerprint(self) -> Dict[str, Any]:
        """
        獲取一致的音頻指紋（每次調用返回相同的指紋）
        
        Returns:
            Dict[str, Any]: 音頻指紋信息
        """
        return {
            "context": {
                "sampleRate": 44100,
                "channelCount": 2,
                "channelCountMode": "explicit",
                "channelInterpretation": "speakers",
                "latencyHint": "interactive"
            },
            "nodes": {
                "gain": 1.0,
                "frequency": 440,
                "detune": 0,
                "Q": 1
            },
            "waveform": "sine",
            "processor": {
                "bufferSize": 2048,
                "numberOfInputs": 1,
                "numberOfOutputs": 1,
                "channelCount": 2
            }
        }
    
    def apply_spoof(self, page) -> None:
        """
        應用音頻指紋偽裝
        
        Args:
            page: Playwright 頁面對象
        """
        try:
            fingerprint = self.get_consistent_audio_fingerprint()
            
            script = f"""
            // 修改 AudioContext 參數
            const originalAudioContext = window.AudioContext || window.webkitAudioContext;
            window.AudioContext = window.webkitAudioContext = function(options) {{
                const context = new originalAudioContext(options);
                
                // 修改 sampleRate
                Object.defineProperty(context, 'sampleRate', {{
                    get: function() {{
                        return {fingerprint['context']['sampleRate']};
                    }}
                }});
                
                // 修改 channelCount
                Object.defineProperty(context, 'channelCount', {{
                    get: function() {{
                        return {fingerprint['context']['channelCount']};
                    }}
                }});
                
                // 修改 channelCountMode
                Object.defineProperty(context, 'channelCountMode', {{
                    get: function() {{
                        return '{fingerprint['context']['channelCountMode']}';
                    }}
                }});
                
                // 修改 channelInterpretation
                Object.defineProperty(context, 'channelInterpretation', {{
                    get: function() {{
                        return '{fingerprint['context']['channelInterpretation']}';
                    }}
                }});
                
                // 修改 latencyHint
                Object.defineProperty(context, 'latencyHint', {{
                    get: function() {{
                        return '{fingerprint['context']['latencyHint']}';
                    }}
                }});
                
                return context;
            }};
            
            // 修改 OscillatorNode 參數
            const originalOscillatorNode = window.OscillatorNode;
            window.OscillatorNode = function(context, options) {{
                const node = new originalOscillatorNode(context, options);
                
                // 修改 frequency
                Object.defineProperty(node.frequency, 'value', {{
                    get: function() {{
                        return {fingerprint['nodes']['frequency']};
                    }}
                }});
                
                // 修改 detune
                Object.defineProperty(node.detune, 'value', {{
                    get: function() {{
                        return {fingerprint['nodes']['detune']};
                    }}
                }});
                
                // 修改 type
                Object.defineProperty(node, 'type', {{
                    get: function() {{
                        return '{fingerprint['waveform']}';
                    }}
                }});
                
                return node;
            }};
            
            // 修改 GainNode 參數
            const originalGainNode = window.GainNode;
            window.GainNode = function(context, options) {{
                const node = new originalGainNode(context, options);
                
                // 修改 gain
                Object.defineProperty(node.gain, 'value', {{
                    get: function() {{
                        return {fingerprint['nodes']['gain']};
                    }}
                }});
                
                return node;
            }};
            
            // 修改 BiquadFilterNode 參數
            const originalBiquadFilterNode = window.BiquadFilterNode;
            window.BiquadFilterNode = function(context, options) {{
                const node = new originalBiquadFilterNode(context, options);
                
                // 修改 Q
                Object.defineProperty(node.Q, 'value', {{
                    get: function() {{
                        return {fingerprint['nodes']['Q']};
                    }}
                }});
                
                return node;
            }};
            
            // 修改 AudioWorkletNode 參數
            const originalAudioWorkletNode = window.AudioWorkletNode;
            window.AudioWorkletNode = function(context, name, options) {{
                const node = new originalAudioWorkletNode(context, name, options);
                
                // 修改 processorOptions
                Object.defineProperty(node, 'processorOptions', {{
                    get: function() {{
                        return {{
                            bufferSize: {fingerprint['processor']['bufferSize']},
                            numberOfInputs: {fingerprint['processor']['numberOfInputs']},
                            numberOfOutputs: {fingerprint['processor']['numberOfOutputs']},
                            channelCount: {fingerprint['processor']['channelCount']}
                        }};
                    }}
                }});
                
                return node;
            }};
            """
            
            page.add_init_script(script)
            logger.info("已應用音頻指紋偽裝")
        except Exception as e:
            logger.error(f"應用音頻指紋偽裝時發生錯誤: {str(e)}")
            raise AntiDetectionException(f"應用音頻指紋偽裝失敗: {str(e)}") 