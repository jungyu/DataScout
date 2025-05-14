/** @type {import('tailwindcss').Config} */
const path = require('path');

module.exports = {
  content: [
    "/Users/aaron/Projects/DataScout/chart_app/templates/**/*.html",
    "/Users/aaron/Projects/DataScout/chart_app/static/**/*.js"
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
