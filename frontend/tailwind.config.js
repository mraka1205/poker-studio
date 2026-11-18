/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      fontFamily: {
        sans: ['Vazirmatn', 'system-ui', 'sans-serif'],
        vazir: ['Vazirmatn', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'Consolas', 'monospace']
      },
      colors: {
        studio: {
          bg: '#090D16',
          card: '#111827',
          cardBorder: '#1F2937',
          sidebar: '#0B0F19',
          gold: '#F59E0B',
          felt: '#064E3B',
          feltLight: '#059669',
          cyan: '#06B6D4',
          accent: '#6366F1'
        }
      }
    },
  },
  plugins: [],
}
