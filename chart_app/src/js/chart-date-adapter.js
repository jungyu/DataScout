/**
 * Chart.js 日期適配器配置
 * 導入並配置 chartjs-adapter-luxon
 */

// 確保這個文件作為webpack的入口之一
// 導入必要的依賴
import { DateTime } from 'luxon';
import 'chartjs-adapter-luxon';

console.log('chartjs-adapter-luxon 已正確載入');

// 導出一個用於檢查適配器是否正確載入的函數
export function verifyDateAdapter() {
    if (typeof Chart !== 'undefined' && Chart.adapters && Chart.adapters._date) {
        console.log('Chart.js 日期適配器檢查: 已正確載入');
        return true;
    } else {
        console.error('Chart.js 日期適配器檢查: 未正確載入');
        return false;
    }
}

// 導出方便其他模組使用的 Luxon DateTime
export { DateTime };
