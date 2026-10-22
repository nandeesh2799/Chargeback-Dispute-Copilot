/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        fintech: {
          dark: "#0B0F19",
          surface: "#111827",
          border: "#1F2937",
          accent: "#4F46E5",
          accentHover: "#4338CA",
          success: "#10B981",
          warning: "#F59E0B",
          danger: "#EF4444",
        }
      },
      fontFamily: {
        sans: ["Inter", "-apple-system", "BlinkMacSystemFont", "Segoe UI", "Roboto", "sans-serif"],
        mono: ["Fira Code", "monospace"]
      }
    },
  },
  plugins: [],
}
