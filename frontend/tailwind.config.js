/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",                      // Vite uses this
    "./src/**/*.{js,ts,jsx,tsx}",        // all React components
  ],
  theme: {
    extend: {
      colors: {
        tumblue: "#3070B3",
        iceblue: "#E3EFF7",
        anthracite: "#333333",
        lightgray: "#F5F5F5",
        tumhover: "#245a8d",
      },
    },
  },
  plugins: [],
};
