"""
stealth.py - Playwright 隱身模式共用腳本
"""
from loguru import logger

def inject_stealth_js(context) -> None:
    """
    注入隱身模式腳本，覆蓋自動化特徵與指紋
    Args:
        context: Playwright BrowserContext 物件
    """
    stealth_js = """
    () => {
        Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
        Object.defineProperty(navigator, 'hardwareConcurrency', { get: () => 8 });
        Object.defineProperty(navigator, 'deviceMemory', { get: () => 8 });
        Object.defineProperty(navigator, 'language', { get: () => 'en-US' });
        Object.defineProperty(navigator, 'platform', { get: () => 'MacIntel' });
        // 模擬正常的 Cookie 行為
        const cookieDesc = Object.getOwnPropertyDescriptor(Document.prototype, 'cookie') || {};
        const cookieGetter = cookieDesc.get || function() {};
        const cookieSetter = cookieDesc.set || function() {};
        Object.defineProperty(Document.prototype, 'cookie', {
            get: function() { return cookieGetter.call(document); },
            set: function(val) { cookieSetter.call(document, val); return true; },
            enumerable: true
        });
        // 模擬滑鼠事件
        const simulateHumanInteractions = () => {
            const randomMoveInterval = setInterval(() => {
                const randomX = Math.floor(Math.random() * window.innerWidth);
                const randomY = Math.floor(Math.random() * window.innerHeight);
                const events = ['mousemove', 'mouseover', 'mouseout'];
                const event = events[Math.floor(Math.random() * events.length)];
                const mouseEvent = new MouseEvent(event, {
                    view: window,
                    bubbles: true,
                    cancelable: true,
                    clientX: randomX,
                    clientY: randomY,
                });
                document.dispatchEvent(mouseEvent);
            }, 2000 + Math.random() * 3000);
            setTimeout(() => { clearInterval(randomMoveInterval); }, 300000);
        };
        setTimeout(simulateHumanInteractions, 5000);
        // 覆蓋 Permissions API
        if (navigator.permissions) {
            const originalQuery = navigator.permissions.query;
            navigator.permissions.query = function(parameters) {
                if (parameters.name === 'notifications') {
                    return Promise.resolve({ state: "prompt", onchange: null });
                }
                return originalQuery.apply(this, arguments);
            };
        }
    }
    """
    context.add_init_script(stealth_js)
    logger.info("已注入隱身模式腳本")
