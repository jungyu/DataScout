// 瀏覽器指紋偽裝腳本

// 導入配置
const { DEFAULT_CONFIG, VERSION } = require('./config.js');

// 日誌工具
const logger = {
    info: (msg) => console.log(`[Stealth ${VERSION.toString()}] ${msg}`),
    error: (msg, error) => console.error(`[Stealth ${VERSION.toString()}] ${msg}:`, error),
    debug: (msg) => console.debug(`[Stealth ${VERSION.toString()}] ${msg}`)
};

// 工具函數
const utils = {
    // 生成隨機數
    random: (min, max) => Math.random() * (max - min) + min,
    
    // 生成高斯分佈隨機數
    gaussian: (mean, std) => {
        const u1 = Math.random();
        const u2 = Math.random();
        const z0 = Math.sqrt(-2.0 * Math.log(u1)) * Math.cos(2.0 * Math.PI * u2);
        return z0 * std + mean;
    },
    
    // 添加噪點
    addNoise: (data, noise, pattern = 'random') => {
        for (let i = 0; i < data.length; i++) {
            let noiseValue = 0;
            switch (pattern) {
                case 'random':
                    noiseValue = utils.random(-noise, noise);
                    break;
                case 'gaussian':
                    noiseValue = utils.gaussian(0, noise);
                    break;
                case 'uniform':
                    noiseValue = noise * (Math.random() > 0.5 ? 1 : -1);
                    break;
            }
            data[i] += noiseValue;
        }
        return data;
    }
};

// 修改 navigator 物件
function modifyNavigator(config) {
    const { browser, languages } = config;
    
    // 修改 webdriver 標記
    Object.defineProperty(navigator, 'webdriver', {
        get: () => false
    });
    
    // 修改語言
    Object.defineProperty(navigator, 'languages', {
        get: () => languages
    });
    
    // 修改平台
    Object.defineProperty(navigator, 'platform', {
        get: () => browser.platform
    });
    
    // 修改 userAgent
    Object.defineProperty(navigator, 'userAgent', {
        get: () => browser.userAgent
    });
    
    // 修改 vendor
    Object.defineProperty(navigator, 'vendor', {
        get: () => browser.vendor
    });
    
    // 修改語言
    Object.defineProperty(navigator, 'language', {
        get: () => browser.language
    });
    
    logger.debug('Navigator properties modified');
}

// 修改螢幕屬性
function modifyScreenProperties(config) {
    const { screen } = config;
    
    Object.defineProperties(screen, {
        width: { get: () => screen.width },
        height: { get: () => screen.height },
        availWidth: { get: () => screen.availWidth },
        availHeight: { get: () => screen.availHeight },
        colorDepth: { get: () => screen.colorDepth },
        pixelDepth: { get: () => screen.pixelDepth }
    });
    
    logger.debug('Screen properties modified');
}

// 偽裝 WebGL 指紋
function spoofWebGL(config) {
    const { webgl } = config;
    const getParameter = WebGLRenderingContext.prototype.getParameter;
    
    WebGLRenderingContext.prototype.getParameter = function(parameter) {
        // 偽裝 WebGL 參數
        switch (parameter) {
            case 37445: // UNMASKED_VENDOR_WEBGL
                return webgl.vendor;
            case 37446: // UNMASKED_RENDERER_WEBGL
                return webgl.renderer;
            case 35724: // VERSION
                return webgl.version;
            case 35720: // SHADING_LANGUAGE_VERSION
                return webgl.shadingLanguageVersion;
            default:
                return getParameter.apply(this, arguments);
        }
    };
    
    logger.debug('WebGL fingerprint spoofed');
}

// 修改 Canvas 指紋
function modifyCanvas(config) {
    const { canvas } = config;
    const originalGetContext = HTMLCanvasElement.prototype.getContext;
    
    HTMLCanvasElement.prototype.getContext = function(type, attributes) {
        const context = originalGetContext.call(this, type, attributes);
        
        if (type === '2d') {
            const originalGetImageData = context.getImageData;
            context.getImageData = function() {
                const imageData = originalGetImageData.apply(this, arguments);
                utils.addNoise(imageData.data, canvas.noise, canvas.pattern);
                return imageData;
            };
        }
        
        return context;
    };
    
    logger.debug('Canvas fingerprint modified');
}

// 修改音頻指紋
function modifyAudio(config) {
    const { audio } = config;
    const originalGetChannelData = AudioBuffer.prototype.getChannelData;
    
    AudioBuffer.prototype.getChannelData = function() {
        const data = originalGetChannelData.apply(this, arguments);
        utils.addNoise(data, audio.noise, 'gaussian');
        return data;
    };
    
    logger.debug('Audio fingerprint modified');
}

// 修改字體指紋
function modifyFonts(config) {
    const { fonts } = config;
    const originalQuerySelector = document.querySelector;
    
    document.querySelector = function(selector) {
        if (selector === '*') {
            // 返回偽裝的字體列表
            return [...fonts.common, ...fonts.chinese];
        }
        return originalQuerySelector.apply(this, arguments);
    };
    
    logger.debug('Font fingerprint modified');
}

// 修改性能指標
function modifyPerformance(config) {
    const { performance } = config;
    
    // 修改內存信息
    if (window.performance && window.performance.memory) {
        Object.defineProperties(window.performance.memory, {
            jsHeapSizeLimit: { get: () => performance.memory.jsHeapSizeLimit },
            totalJSHeapSize: { get: () => performance.memory.totalJSHeapSize },
            usedJSHeapSize: { get: () => performance.memory.usedJSHeapSize }
        });
    }
    
    // 修改時間信息
    if (window.performance && window.performance.timing) {
        Object.defineProperties(window.performance.timing, {
            navigationStart: { get: () => performance.timing.navigationStart },
            fetchStart: { get: () => performance.timing.fetchStart },
            domainLookupStart: { get: () => performance.timing.domainLookupStart },
            domainLookupEnd: { get: () => performance.timing.domainLookupEnd },
            connectStart: { get: () => performance.timing.connectStart },
            connectEnd: { get: () => performance.timing.connectEnd },
            requestStart: { get: () => performance.timing.requestStart },
            responseStart: { get: () => performance.timing.responseStart },
            responseEnd: { get: () => performance.timing.responseEnd },
            domLoading: { get: () => performance.timing.domLoading },
            domInteractive: { get: () => performance.timing.domInteractive },
            domContentLoadedEventStart: { get: () => performance.timing.domContentLoadedEventStart },
            domContentLoadedEventEnd: { get: () => performance.timing.domContentLoadedEventEnd },
            domComplete: { get: () => performance.timing.domComplete },
            loadEventStart: { get: () => performance.timing.loadEventStart },
            loadEventEnd: { get: () => performance.timing.loadEventEnd }
        });
    }
    
    logger.debug('Performance metrics modified');
}

// 隱藏自動化特徵
function hideAutomation() {
    // 刪除 Selenium 相關的全局變量
    delete window.cdc_adoQpoasnfa76pfcZLmcfl_Array;
    delete window.cdc_adoQpoasnfa76pfcZLmcfl_Promise;
    delete window.cdc_adoQpoasnfa76pfcZLmcfl_Symbol;
    
    // 刪除其他自動化標記
    delete window._Selenium_IDE_Recorder;
    delete window._selenium;
    delete window.callSelenium;
    delete window._phantom;
    delete window.__nightmare;
    delete window.domAutomation;
    delete window.domAutomationController;
    
    logger.debug('Automation features hidden');
}

// 主要的指紋偽裝函數
function applyStealthMode(config = DEFAULT_CONFIG) {
    try {
        logger.info('Starting stealth mode application');
        
        // 應用各種偽裝
        modifyNavigator(config);
        modifyScreenProperties(config);
        spoofWebGL(config);
        modifyCanvas(config);
        modifyAudio(config);
        modifyFonts(config);
        modifyPerformance(config);
        hideAutomation();
        
        logger.info('Stealth mode applied successfully');
    } catch (error) {
        logger.error('Failed to apply stealth mode', error);
        throw error;
    }
}

// 檢查更新
function checkForUpdates() {
    fetch('https://api.example.com/stealth-updates')
        .then(response => response.json())
        .then(updates => {
            if (updates.version > VERSION.toString()) {
                logger.info(`New version available: ${updates.version}`);
                // 應用更新
                applyUpdates(updates);
            }
        })
        .catch(error => {
            logger.error('Failed to check for updates', error);
        });
}

// 執行偽裝
applyStealthMode();

// 定期檢查更新
setInterval(checkForUpdates, 24 * 60 * 60 * 1000); // 每24小時檢查一次
