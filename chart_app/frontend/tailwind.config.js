/** @type {import('tailwindcss').Config} */
const path = require('path');

module.exports = {
  content: [
    '../templates/**/*.{html,js}',
    '../static/**/*.{js,css}',
    './input.css',
    // 使用更寬松的匹配模式
    '../**/*.html',
    '../**/*.js',
  ],
  safelist: [
    {
      pattern: /./, // 這將包含所有的 Tailwind 類
      variants: ['hover', 'focus', 'md', 'lg', 'sm']
    }
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['"Noto Sans TC"', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
