// tailwind.config.js
/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}", // 这一行是关键
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}