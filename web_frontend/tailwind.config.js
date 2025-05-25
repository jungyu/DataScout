   /** @type {import('tailwindcss').Config} */
import daisyui from 'daisyui';

export default {
  content: [
    "./public/index.html",
    "./src/**/*.{js,jsx,ts,tsx}"
  ],
  theme: {
    extend: {
      colors: {
        primary: "#1E293B",
        secondary: "#4F46E5",
        accent: "#6366F1",
        neutral: "#64748B",
      },
    },
  },
  plugins: [daisyui],
  daisyui: {
    themes: [
      {
        "fantasy": {
          ...require("daisyui/src/theming/themes")["fantasy"],
          "primary": "#331c77",
          "primary-focus": "#251458", 
          "primary-content": "#ffffff",
          "base-100": "#ffffff",
          "base-200": "#f8f9fc",
          "base-300": "#f1f5f9",
          "base-content": "#334155",
          "accent": "#7c3aed",
          "accent-content": "#ffffff",
          "neutral": "#64748b",
          "neutral-focus": "#475569",
          "neutral-content": "#f8fafc",
          "success": "#10b981",
          "success-content": "#ffffff",
          "error": "#ef4444",
          "error-content": "#ffffff",
        }
      },
      {
        "fantasy-dark": {
          ...require("daisyui/src/theming/themes")["[data-theme=fantasy]"],
          "primary": "#1E293B",
          "primary-focus": "#0F172A", 
          "primary-content": "#f8fafc",
          "base-100": "#1E293B",
          "base-200": "#0F172A",
          "base-300": "#020617",
          "base-content": "#E2E8F0",
          "accent": "#8B5CF6",
          "accent-content": "#ffffff",
          "neutral": "#1f2937",
          "neutral-focus": "#1e293b",
          "neutral-content": "#ffffff",
          "success": "#10b981",
          "success-content": "#ffffff",
          "error": "#ef4444",
          "error-content": "#ffffff",
        },
      },
    ],
    darkTheme: "fantasy-dark",
  },
}