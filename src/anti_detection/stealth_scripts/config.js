// stealth scripts 配置文件

const DEFAULT_CONFIG = {
    // 螢幕配置
    screen: {
        width: 1920,
        height: 1080,
        availWidth: 1920,
        availHeight: 1040,
        colorDepth: 24,
        pixelDepth: 24
    },
    
    // 語言配置
    languages: ['zh-TW', 'zh', 'en-US', 'en'],
    
    // WebGL 配置
    webgl: {
        vendor: 'Intel Open Source Technology Center',
        renderer: 'Mesa DRI Intel(R) HD Graphics',
        version: 'WebGL GLSL ES 1.0',
        shadingLanguageVersion: 'WebGL GLSL ES 1.0'
    },
    
    // Canvas 配置
    canvas: {
        noise: 0.0001,  // 噪點強度
        pattern: 'random'  // 噪點模式：random, gaussian, uniform
    },
    
    // 音頻配置
    audio: {
        noise: 0.0001,  // 噪點強度
        sampleRate: 44100,
        channelCount: 2
    },
    
    // 字體配置
    fonts: {
        // 常用字體列表
        common: [
            'Arial',
            'Helvetica',
            'Times New Roman',
            'Times',
            'Courier New',
            'Courier',
            'Verdana',
            'Georgia',
            'Palatino',
            'Garamond',
            'Bookman',
            'Comic Sans MS',
            'Trebuchet MS',
            'Arial Black'
        ],
        // 中文字體
        chinese: [
            'Microsoft YaHei',
            'Microsoft JhengHei',
            'PingFang SC',
            'PingFang TC',
            'Heiti TC',
            'Heiti SC',
            'STHeiti',
            'STSong',
            'STKaiti',
            'STFangsong'
        ]
    },
    
    // 瀏覽器配置
    browser: {
        platform: 'Win32',
        userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        vendor: 'Google Inc.',
        language: 'zh-TW'
    },
    
    // 性能配置
    performance: {
        memory: {
            jsHeapSizeLimit: 2172649472,
            totalJSHeapSize: 100000000,
            usedJSHeapSize: 80000000
        },
        timing: {
            navigationStart: Date.now(),
            fetchStart: Date.now() + 100,
            domainLookupStart: Date.now() + 200,
            domainLookupEnd: Date.now() + 300,
            connectStart: Date.now() + 400,
            connectEnd: Date.now() + 500,
            requestStart: Date.now() + 600,
            responseStart: Date.now() + 700,
            responseEnd: Date.now() + 800,
            domLoading: Date.now() + 900,
            domInteractive: Date.now() + 1000,
            domContentLoadedEventStart: Date.now() + 1100,
            domContentLoadedEventEnd: Date.now() + 1200,
            domComplete: Date.now() + 1300,
            loadEventStart: Date.now() + 1400,
            loadEventEnd: Date.now() + 1500
        }
    }
};

// 版本信息
const VERSION = {
    major: 1,
    minor: 0,
    patch: 0,
    toString: function() {
        return `${this.major}.${this.minor}.${this.patch}`;
    }
};

// 導出配置
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        DEFAULT_CONFIG,
        VERSION
    };
} 