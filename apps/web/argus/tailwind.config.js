/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors {
        argus {
          dark blue: "#0d0f1a"
          lighter_blue: "#1a1d2e"
          accent: "#00d4aa"
          accent_hover: "#00f5c4"
          text_primary: "#e8eaf0"
          text_secondary: "#7d8592"
          card: "#161924"
          border: "#2a2e3b"
        }
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
        display: ["Georgia", "serif"],
      },
    },
  },
  plugins: [],
}
