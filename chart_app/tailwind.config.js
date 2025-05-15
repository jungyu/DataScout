
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./templates/**/*.html", 
    "./static/**/*.js", 
    "./src/**/*.js"
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Noto Sans TC', 'sans-serif'],
      },
      colors: {
        primary: {
          50: '#e6f0ff',
          100: '#cce0ff',
          200: '#99c1ff',
          300: '#66a3ff',
          400: '#3384ff',
          500: '#0066ff',  // 主色調
          600: '#0051cc',
          700: '#003d99',
          800: '#002966',
          900: '#001433',
        },
      },
    },
  },
  plugins: [require("daisyui")],
  // daisyUI 配置
  daisyui: {
    themes: [
      {
        light: {
          "primary": "#0066ff",
          "secondary": "#6c757d",
          "accent": "#37cdbe",
          "neutral": "#2b3440",
          "base-100": "#ffffff",
          "info": "#3abff8",
          "success": "#36d399",
          "warning": "#fbbd23",
          "error": "#f87272",
        },
        dark: {
          "primary": "#3384ff",
          "secondary": "#9ca3af",
          "accent": "#35aacc",
          "neutral": "#111827",
          "base-100": "#1f2937",
          "info": "#0284c7",
          "success": "#059669",
          "warning": "#d97706",
          "error": "#dc2626",
        },
      },
    ],
  },
}
