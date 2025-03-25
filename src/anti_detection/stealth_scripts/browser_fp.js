// 修改 navigator 物件屬性
function modifyNavigator() {
    Object.defineProperty(navigator, 'webdriver', {
        get: () => false
    });
    
    Object.defineProperty(navigator, 'languages', {
        get: () => ['zh-TW', 'zh', 'en-US', 'en']
    });
}

// 偽裝 WebGL 指紋
function spoofWebGL() {
    const getParameter = WebGLRenderingContext.prototype.getParameter;
    WebGLRenderingContext.prototype.getParameter = function(parameter) {
        if (parameter === 37445) {
            return 'Intel Open Source Technology Center';
        }
        if (parameter === 37446) {
            return 'Mesa DRI Intel(R) HD Graphics';
        }
        return getParameter.apply(this, arguments);
    };
}

// 修改螢幕和視窗屬性
function modifyScreenProperties() {
    Object.defineProperty(screen, 'width', {
        get: () => 1920
    });
    Object.defineProperty(screen, 'height', {
        get: () => 1080
    });
    Object.defineProperty(screen, 'availWidth', {
        get: () => 1920
    });
    Object.defineProperty(screen, 'availHeight', {
        get: () => 1040
    });
}

// 主要的指紋偽裝函數
function applyStealthMode() {
    try {
        modifyNavigator();
        spoofWebGL();
        modifyScreenProperties();
        
        // 隱藏自動化特徵
        delete window.cdc_adoQpoasnfa76pfcZLmcfl_Array;
        delete window.cdc_adoQpoasnfa76pfcZLmcfl_Promise;
        delete window.cdc_adoQpoasnfa76pfcZLmcfl_Symbol;
        
        console.log('Browser fingerprint modifications applied successfully');
    } catch (error) {
        console.error('Error applying stealth mode:', error);
    }
}

// 執行偽裝
applyStealthMode();
