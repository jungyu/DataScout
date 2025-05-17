/**
 * 集中管理應用程式狀態
 * 包含狀態初始化、獲取和設置功能
 */

/**
 * 應用程式狀態物件
 */
const appState = {
    myChart: null,
    currentDataFile: null,
    currentDataType: 'json',
    currentChartType: 'radar',  // 預設為雷達圖
    currentChartTheme: 'default',
    availableDataFiles: {},
    dataColumnInfo: null,
    dataStats: {
        totalPoints: 0,
        datasetCount: 0
    }
};

/**
 * 獲取整個應用程式狀態
 * @returns {Object} 當前應用程式狀態
 */
export function getAppState() {
    return appState;
}

/**
 * 獲取特定狀態值
 * @param {string} key - 狀態屬性的鍵名
 * @returns {*} 屬性值
 */
export function getStateValue(key) {
    return appState[key];
}

/**
 * 設置狀態屬性值
 * @param {string} key - 狀態屬性鍵名
 * @param {*} value - 要設置的值
 */
export function setStateValue(key, value) {
    if (key in appState) {
        appState[key] = value;
        console.log(`狀態更新: ${key} = `, value);
    } else {
        console.warn(`嘗試設置未定義的狀態屬性: ${key}`);
    }
}

/**
 * 更新資料統計數據
 * @param {Object} data - 圖表數據
 */
export function updateDataStats(data) {
    try {
        let totalPoints = 0;
        let datasetCount = 0;
        
        // 計算數據點總數和數據集數量
        if (data && data.datasets) {
            datasetCount = data.datasets.length;
            
            data.datasets.forEach(dataset => {
                if (dataset.data && Array.isArray(dataset.data)) {
                    totalPoints += dataset.data.length;
                }
            });
        }
        
        appState.dataStats = {
            totalPoints,
            datasetCount
        };
        
        console.log(`資料統計已更新: ${datasetCount} 個數據集, ${totalPoints} 個數據點`);
    } catch (error) {
        console.error('更新資料統計時發生錯誤:', error);
    }
}

/**
 * 重置應用程式狀態
 */
export function resetAppState() {
    appState.myChart = null;
    appState.dataColumnInfo = null;
    appState.dataStats = {
        totalPoints: 0,
        datasetCount: 0
    };
    console.log('應用程式狀態已重置');
}

/**
 * 初始化應用程式狀態
 * @returns {Object} 初始化的應用程式狀態
 */
export function initializeAppState() {
    console.log('初始化應用程式狀態');
    window.chartAppLoaded = true;
    return appState;
}

// 導出預設的應用程式狀態
export default appState;
