/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        studio: {
          dark: '#0B0F19',
          card: '#131B2E',
          border: '#1E293B',
          accent: '#F59E0B',
          glow: '#3B82F6'
        }
      }
    },
  },
  plugins: [],
}
