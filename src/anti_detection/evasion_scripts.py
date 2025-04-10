"""
蝦皮(Shopee)網站爬蟲反檢測腳本模組
包含各種用於繞過檢測的 JavaScript 腳本
"""

def get_general_evasion_script():
    """返回通用的反檢測腳本"""
    return """
    (function() {
        // 隱藏Webdriver特徵
        Object.defineProperty(navigator, 'webdriver', {
            get: () => false,
            configurable: true
        });
        
        // 移除自動化相關屬性
        delete document.$cdc_asdjflasutopfhvcZLmcfl_;
        
        // 模擬正常的Chrome特性
        window.chrome = {
            runtime: {},
            loadTimes: function() {},
            csi: function() {},
            app: {}
        };
        
        // 覆蓋Permissions API
        const originalQuery = window.navigator.permissions.query;
        window.navigator.permissions.query = function(parameters) {
            return parameters.name === 'notifications' 
                ? Promise.resolve({state: Notification.permission, onchange: null})
                : originalQuery.call(this, parameters);
        };
        
        // 添加語言特性
        Object.defineProperty(navigator, 'languages', {
            get: function() {
                return ['zh-TW', 'zh', 'en-US', 'en'];
            }
        });
        
        // 添加plugins特性
        Object.defineProperty(navigator, 'plugins', {
            get: function() {
                const plugins = [
                    { name: 'Chrome PDF Plugin', filename: 'internal-pdf-viewer' },
                    { name: 'Chrome PDF Viewer', filename: 'mhjfbmdgcfjbbpaeojofohoefgiehjai' },
                    { name: 'Native Client', filename: 'internal-nacl-plugin' }
                ];
                
                // 創建假的PluginArray
                const pluginArray = Object.create(PluginArray.prototype);
                pluginArray.length = plugins.length;
                
                // 添加插件到數組
                plugins.forEach((plugin, i) => {
                    const pluginItem = Object.create(Plugin.prototype);
                    pluginItem.name = plugin.name;
                    pluginItem.filename = plugin.filename;
                    pluginItem.description = plugin.name;
                    pluginItem.length = 1;
                    
                    pluginArray[i] = pluginItem;
                    pluginArray[plugin.name] = pluginItem;
                });
                
                return pluginArray;
            }
        });
    })();
    """

def get_shopee_specific_evasion_script():
    """返回蝦皮特定的反檢測腳本"""
    return """
    (function() {
        // 防止特定的蝦皮檢測函數
        const originalFetch = window.fetch;
        window.fetch = function() {
            // 避免特定的檢測請求
            const url = arguments[0];
            if (typeof url === 'string' && (
                url.includes('/api/v2/anti_bot/') || 
                url.includes('/api/v4/safety/detect') ||
                url.includes('captcha'))) {
                console.log('Intercepted detection request:', url);
                // 返回一個假的成功響應
                return Promise.resolve(new Response(JSON.stringify({success: true}), {
                    status: 200,
                    headers: { 'Content-Type': 'application/json' }
                }));
            }
            return originalFetch.apply(this, arguments);
        };
        
        // 防止指紋收集腳本
        const fingerprintDetectors = [
            'Fingerprint',
            'Fingerprint2',
            'FingerprintJS',
            'ClientJS',
            '__htmlsLsMeasure',
            '_hsab_e_',
            'hp_d', // 蝦皮特定的檢測變量
            'shopee.fe.check' // 蝦皮前端檢測
        ];
        
        fingerprintDetectors.forEach(name => {
            Object.defineProperty(window, name, {
                get: function() { return undefined; },
                set: function() {},
                configurable: false
            });
        });
        
        // 模擬常見的蝦皮用戶行為
        // 隨機移動滑鼠，模擬真實用戶
        let lastMoveTime = 0;
        document.addEventListener('mousemove', function(e) {
            const now = Date.now();
            // 儲存上次移動時間，用於動態調整延遲
            lastMoveTime = now;
        }, true);
        
        // 覆蓋可能的檢測函數
        if (typeof window.ShopeeCaptcha !== 'undefined') {
            const originalCheck = window.ShopeeCaptcha.check;
            window.ShopeeCaptcha.check = function() {
                console.log('ShopeeCaptcha.check called');
                // 返回一個假的通過結果
                return Promise.resolve({pass: true});
            };
        }
    })();
    """

def get_webgl_fingerprint_evasion_script(noise):
    """返回WebGL指紋混淆腳本"""
    return f"""
    (function() {{
        // 保存原始的getParameter函數
        const getParameter = WebGLRenderingContext.prototype.getParameter;
        WebGLRenderingContext.prototype.getParameter = function(parameter) {{
            // UNMASKED_VENDOR_WEBGL
            if (parameter === 37445) {{
                return 'Intel Inc.';
            }}
            // UNMASKED_RENDERER_WEBGL
            if (parameter === 37446) {{
                return 'Intel Iris Pro Graphics';
            }}
            
            // 對浮點數添加微小噪聲
            const result = getParameter.apply(this, arguments);
            if (typeof result === 'number' && !Number.isInteger(result)) {{
                // 添加一個範圍在 +/- {noise} 的隨機值
                return result * (1 + (Math.random() * {noise} * 2 - {noise}));
            }}
            
            return result;
        }};
        
        // 修改WebGL context創建
        const originalGetContext = HTMLCanvasElement.prototype.getContext;
        HTMLCanvasElement.prototype.getContext = function() {{
            const context = originalGetContext.apply(this, arguments);
            if (arguments[0] === 'webgl' || arguments[0] === 'experimental-webgl') {{
                // 混淆WebGL上下文
                const desensitizerMethods = ['getExtension', 'getParameter', 'getShaderPrecisionFormat'];
                for (const method of desensitizerMethods) {{
                    const original = context[method];
                    if (original) {{
                        context[method] = function() {{
                            let result = original.apply(this, arguments);
                            // 為某些結果添加噪聲
                            if (method === 'getShaderPrecisionFormat' && result) {{
                                result.rangeMin = result.rangeMin;
                                result.rangeMax = result.rangeMax;
                                result.precision = result.precision;
                            }}
                            return result;
                        }};
                    }}
                }}
            }}
            return context;
        }};
    }})();
    """

def get_canvas_fingerprint_evasion_script():
    """返回Canvas指紋混淆腳本"""
    return """
    (function() {
        // 保存原始方法
        const originalToDataURL = HTMLCanvasElement.prototype.toDataURL;
        const originalGetImageData = CanvasRenderingContext2D.prototype.getImageData;
        
        // 重寫toDataURL方法
        HTMLCanvasElement.prototype.toDataURL = function() {
            // 檢查是否是指紋收集
            if (this.width === 16 && this.height === 16) {
                // 很可能是指紋收集，返回隨機數據
                return 'data:image/png;base64,' + randomBase64(32);
            }
            
            // 檢查是否為文字渲染指紋
            const ctx = this.getContext('2d');
            if (ctx && ctx.__fingerprintDetectionAttempt) {
                // 已被標記為指紋檢測嘗試
                return 'data:image/png;base64,' + randomBase64(32);
            }
            
            // 在某些情況下添加些微噪聲
            if (this.width <= 200 && this.height <= 200 && Math.random() < 0.5) {
                const ctx = this.getContext('2d');
                if (ctx) {
                    // 添加單一像素的微小噪點
                    const pixel = ctx.getImageData(0, 0, 1, 1);
                    if (pixel && pixel.data) {
                        pixel.data[0] = Math.max(0, Math.min(255, pixel.data[0] + (Math.random() * 2 - 1)));
                        pixel.data[1] = Math.max(0, Math.min(255, pixel.data[1] + (Math.random() * 2 - 1)));
                        pixel.data[2] = Math.max(0, Math.min(255, pixel.data[2] + (Math.random() * 2 - 1)));
                        ctx.putImageData(pixel, 0, 0);
                    }
                }
            }
            
            return originalToDataURL.apply(this, arguments);
        };
        
        // 重寫getImageData方法
        CanvasRenderingContext2D.prototype.getImageData = function() {
            // 檢查是否是用於指紋的小尺寸canvas
            const canvas = this.canvas;
            if (canvas && canvas.width <= 32 && canvas.height <= 32) {
                // 標記為指紋檢測嘗試
                this.__fingerprintDetectionAttempt = true;
            }
            
            const imageData = originalGetImageData.apply(this, arguments);
            
            // 只對小尺寸的canvas添加噪聲（通常用於指紋）
            if (imageData && imageData.data && 
                arguments[2] <= 32 && arguments[3] <= 32 && 
                Math.random() < 0.5) {
                for (let i = 0; i < imageData.data.length; i += 4) {
                    // 為每個像素的RGBA通道添加微小變化
                    imageData.data[i] = Math.max(0, Math.min(255, imageData.data[i] + (Math.random() * 2 - 1)));
                    imageData.data[i+1] = Math.max(0, Math.min(255, imageData.data[i+1] + (Math.random() * 2 - 1)));
                    imageData.data[i+2] = Math.max(0, Math.min(255, imageData.data[i+2] + (Math.random() * 2 - 1)));
                    // Alpha通道通常不修改
                }
            }
            
            return imageData;
        };
        
        // 監控文字渲染 - 文字渲染是指紋識別的重要來源
        const originalFillText = CanvasRenderingContext2D.prototype.fillText;
        CanvasRenderingContext2D.prototype.fillText = function() {
            // 檢查是否為常見的指紋收集文字
            const text = arguments[0];
            if (text === 'Cwm fjordbank glyphs vext quiz' || 
                text === 'mmmmmmmmlli' || 
                text.length <= 5) {
                // 標記為指紋檢測嘗試
                this.__fingerprintDetectionAttempt = true;
                
                // 稍微修改位置參數，但不至於影響可讀性
                if (typeof arguments[1] === 'number' && typeof arguments[2] === 'number') {
                    arguments[1] += Math.random() * 0.02;
                    arguments[2] += Math.random() * 0.02;
                }
            }
            
            return originalFillText.apply(this, arguments);
        };
        
        // 生成隨機Base64字符串
        function randomBase64(length) {
            const charset = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/';
            let result = '';
            for (let i = 0; i < length; i++) {
                result += charset.charAt(Math.floor(Math.random() * charset.length));
            }
            return result;
        }
    })();
    """

def get_mouse_movement_simulation_script():
    """返回滑鼠行為模擬腳本"""
    return """
    (function() {
        // 跟蹤滑鼠狀態
        let lastX = 0;
        let lastY = 0;
        let lastTime = 0;
        let clickCount = 0;
        
        // 監聽滑鼠移動
        window.addEventListener('mousemove', function(e) {
            const now = Date.now();
            // 計算速度
            if (lastTime > 0) {
                const dt = now - lastTime;
                if (dt > 0) {
                    const dx = e.clientX - lastX;
                    const dy = e.clientY - lastY;
                    const speed = Math.sqrt(dx*dx + dy*dy) / dt;
                    
                    // 如果滑鼠移動速度異常（太快或太直線），添加一點隨機性
                    if (speed > 1.5) { // 速度閾值
                        // 在下一幀產生一些微小的隨機移動
                        setTimeout(() => {
                            const event = new MouseEvent('mousemove', {
                                clientX: e.clientX + (Math.random() * 4 - 2),
                                clientY: e.clientY + (Math.random() * 4 - 2),
                                bubbles: true,
                                cancelable: true
                            });
                            document.dispatchEvent(event);
                        }, 16); // 大約一幀的時間
                    }
                }
            }
            
            // 更新上一次位置和時間
            lastX = e.clientX;
            lastY = e.clientY;
            lastTime = now;
        }, true);
        
        // 監聽點擊
        window.addEventListener('click', function(e) {
            clickCount++;
            
            // 每隔幾次點擊，模擬人類的微小誤差
            if (clickCount % 3 === 0) {
                // 在點擊後產生小滑鼠移動
                setTimeout(() => {
                    const event = new MouseEvent('mousemove', {
                        clientX: e.clientX + (Math.random() * 10 - 5),
                        clientY: e.clientY + (Math.random() * 10 - 5),
                        bubbles: true,
                        cancelable: true
                    });
                    document.dispatchEvent(event);
                }, Math.random() * 300 + 50);
            }
        }, true);
        
        // 監聽滾動
        let lastScrollTime = 0;
        let scrollCount = 0;
        
        window.addEventListener('scroll', function() {
            const now = Date.now();
            scrollCount++;
            
            // 檢測快速連續滾動
            if (lastScrollTime > 0 && now - lastScrollTime < 50) {
                // 機器人可能會產生非常規則的滾動間隔
                // 在極短時間內快速連續滾動可能是機器人行為
                
                // 每隔幾次快速滾動，添加一個隨機延遲，模擬人類手指停頓
                if (scrollCount % 5 === 0) {
                    // 停頓片刻
                    const pauseTime = Math.random() * 500 + 100;
                    setTimeout(() => {
                        // 滾動一小段距離
                        window.scrollBy(0, Math.random() * 10 - 5);
                    }, pauseTime);
                }
            }
            
            lastScrollTime = now;
        }, true);
        
        // 模擬初始的隨機滑鼠移動
        setTimeout(() => {
            const centerX = window.innerWidth / 2;
            const centerY = window.innerHeight / 2;
            
            // 產生從屏幕邊緣到中心的移動軌跡
            const startX = Math.random() * window.innerWidth;
            const startY = Math.random() * window.innerHeight;
            
            // 模擬5-10個中間點的自然移動曲線
            let currentX = startX;
            let currentY = startY;
            const steps = 5 + Math.floor(Math.random() * 5);
            
            for (let i = 0; i < steps; i++) {
                // 計算下一個點，逐漸接近中心
                const ratio = (i + 1) / steps;
                const nextX = currentX + (centerX - startX) * ratio / steps + (Math.random() * 20 - 10);
                const nextY = currentY + (centerY - startY) * ratio / steps + (Math.random() * 20 - 10);
                
                // 延遲執行，模擬移動軌跡
                setTimeout(() => {
                    const event = new MouseEvent('mousemove', {
                        clientX: nextX,
                        clientY: nextY,
                        bubbles: true,
                        cancelable: true
                    });
                    document.dispatchEvent(event);
                }, i * (Math.random() * 100 + 50));
                
                currentX = nextX;
                currentY = nextY;
            }
        }, 1000);
    })();
    """

def get_cookie_protection_script():
    """返回Cookie保護腳本"""
    return """
    (function() {
        // 保護關鍵Cookie不被修改
        const keyCookies = ['SPC_EC', 'SPC_U', 'SPC_SI', 'SPC_F'];
        
        // 保存原始的document.cookie getter和setter
        const originalCookieGetter = Object.getOwnPropertyDescriptor(Document.prototype, 'cookie').get;
        const originalCookieSetter = Object.getOwnPropertyDescriptor(Document.prototype, 'cookie').set;
        
        // 重定義cookie屬性
        Object.defineProperty(document, 'cookie', {
            get: function() {
                return originalCookieGetter.call(this);
            },
            set: function(value) {
                // 檢查嘗試設置的cookie是否為關鍵cookie
                const cookieName = value.split('=')[0].trim();
                
                // 阻止可疑的修改嘗試
                if (keyCookies.includes(cookieName)) {
                    // 檢查是否為可疑來源（非頂級頁面或來自iframe）
                    if (window !== window.top || document.referrer.indexOf(location.hostname) === -1) {
                        console.log(`阻止可疑來源修改關鍵Cookie: ${cookieName}`);
                        return; // 阻止設置
                    }
                    
                    // 檢查是否與特定模式匹配
                    const suspiciousPatterns = [
                        /shopee_webUnique_ccd/i,
                        /captcha/i,
                        /bot_/i,
                        /verification_/i
                    ];
                    
                    for (const pattern of suspiciousPatterns) {
                        if (pattern.test(value)) {
                            console.log(`阻止可疑Cookie修改: ${value}`);
                            return; // 阻止設置
                        }
                    }
                }
                
                // 允許正常的cookie設置
                return originalCookieSetter.call(this, value);
            },
            configurable: true
        });
        
        // 補丁XMLHttpRequest，監控可能的cookie相關操作
        const originalOpen = XMLHttpRequest.prototype.open;
        XMLHttpRequest.prototype.open = function() {
            const url = arguments[1];
            
            // 監控可能用於cookie驗證或收集的請求
            if (typeof url === 'string' && (
                url.includes('/api/v4/account/login_status') || 
                url.includes('/api/v4/account/basic') ||
                url.includes('/api/v2/authentication'))) {
                this._isSensitiveRequest = true;
            }
            
            return originalOpen.apply(this, arguments);
        };
        
        const originalSend = XMLHttpRequest.prototype.send;
        XMLHttpRequest.prototype.send = function() {
            // 對敏感請求進行特殊處理
            if (this._isSensitiveRequest) {
                // 添加監聽器來檢查響應
                this.addEventListener('load', function() {
                    try {
                        const response = JSON.parse(this.responseText);
                        // 檢查是否包含cookie或驗證信息
                        if (response && (response.cookie || response.tokens || response.verification)) {
                            console.log('檢測到敏感信息響應，進行處理');
                            // 可以進行進一步處理...
                        }
                    } catch {}
                });
            }
            
            return originalSend.apply(this, arguments);
        };
        
        // 監控localStorage操作，防止指紋存儲
        const originalSetItem = Storage.prototype.setItem;
        Storage.prototype.setItem = function(key, value) {
            // 檢查可疑鍵名
            const suspiciousKeys = [
                'fingerprint',
                'deviceId',
                'botDetect',
                'captcha',
                'shopee_webUnique',
                'SPC_tbsc'
            ];
            
            for (const suspiciousKey of suspiciousKeys) {
                if (key.toLowerCase().includes(suspiciousKey.toLowerCase())) {
                    console.log(`阻止可疑localStorage操作: ${key}`);
                    // 可以選擇完全阻止或修改存儲的值
                    // 這裡採用修改值的方式
                    const fakeValue = `{"timestamp":${Date.now()},"random":"${Math.random().toString(36).substring(2)}"}`;
                    return originalSetItem.call(this, key, fakeValue);
                }
            }
            
            return originalSetItem.call(this, key, value);
        };
    })();
    """ 