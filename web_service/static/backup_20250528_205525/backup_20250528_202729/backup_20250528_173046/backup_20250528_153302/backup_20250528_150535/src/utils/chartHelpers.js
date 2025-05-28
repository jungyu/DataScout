   /**
 * 圖表輔助工具函數
 */

// 格式化日期為 HH:MM 格式
export const formatTime = (date) => {
  if (!(date instanceof Date)) {
    date = new Date(date);
  }
  return date.toLocaleTimeString('zh-TW', {hour: '2-digit', minute: '2-digit'});
};

// 格式化日期為 YYYY-MM-DD 格式
export const formatDate = (date) => {
  if (!(date instanceof Date)) {
    date = new Date(date);
  }
  return date.toLocaleDateString('zh-TW', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit'
  }).replace(/\//g, '-');
};

// 格式化數字為金額格式
export const formatCurrency = (value, currency = 'USD', locale = 'zh-TW') => {
  return new Intl.NumberFormat(locale, {
    style: 'currency',
    currency: currency
  }).format(value);
};

// 格式化數字為百分比格式
export const formatPercent = (value, digits = 2) => {
  return new Intl.NumberFormat('zh-TW', {
    style: 'percent',
    minimumFractionDigits: digits,
    maximumFractionDigits: digits
  }).format(value / 100);
};

// 生成隨機顏色
export const randomColor = () => {
  return '#' + Math.floor(Math.random() * 16777215).toString(16);
};

// 獲取顏色陣列
export const getColorPalette = (count = 10) => {
  const baseColors = [
    '#4F46E5', // Indigo
    '#06B6D4', // Cyan
    '#10B981', // Emerald
    '#F59E0B', // Amber
    '#EF4444', // Red
    '#8B5CF6', // Purple
    '#EC4899', // Pink
    '#F97316', // Orange
    '#14B8A6', // Teal
    '#6366F1'  // Indigo/Blue
  ];
  
  if (count <= baseColors.length) {
    return baseColors.slice(0, count);
  }
  
  // 需要更多顏色時生成隨機顏色
  const colors = [...baseColors];
  for (let i = baseColors.length; i < count; i++) {
    colors.push(randomColor());
  }
  
  return colors;
};

// 計算數據的統計值
export const calculateStats = (data, key = 'value') => {
  const values = data.map(item => typeof item === 'object' ? item[key] : item);
  
  const sum = values.reduce((acc, val) => acc + val, 0);
  const avg = sum / values.length;
  
  values.sort((a, b) => a - b);
  const min = values[0];
  const max = values[values.length - 1];
  const median = values.length % 2 === 0 
    ? (values[values.length / 2 - 1] + values[values.length / 2]) / 2 
    : values[Math.floor(values.length / 2)];
  
  return { sum, avg, min, max, median };
};

// 幫助函數：將OHLC數據轉換為蠟燭圖格式
export const convertToOHLC = (data, dateField, openField, highField, lowField, closeField) => {
  return data.map(item => ({
    x: new Date(item[dateField]).getTime(),
    y: [
      item[openField],
      item[highField],
      item[lowField],
      item[closeField]
    ]
  }));
};