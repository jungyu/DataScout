/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{html,js}",
    "../templates/**/*.{html,js}",
    "../static/**/*.{html,js}"
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Noto Sans TC', 'sans-serif'],
      },
      colors: {
        'primary-dark': '#0F172A',
        'secondary-dark': '#1E293B',
      },
    },
  },
  plugins: [
    require('daisyui')
  ],
  daisyui: {
    themes: [
      {
        light: {
          ...require("daisyui/src/theming/themes")["[data-theme=light]"],
          primary: "#4f46e5",
          secondary: "#0ea5e9",
          accent: "#0fa5e9",
          neutral: "#2a323c",
          "base-100": "#f3f4f6",
          "base-200": "#e5e7eb",
          "base-300": "#d1d5db",
        },
        dark: {
          ...require("daisyui/src/theming/themes")["[data-theme=dark]"],
          primary: "#6366f1",
          secondary: "#0ea5e9",
          accent: "#22d3ee",
          neutral: "#1f2937",
          "base-100": "#0f172a",
          "base-200": "#1e293b", 
          "base-300": "#334155",
        },
      },
    ],
    darkTheme: "dark",
  },
}
