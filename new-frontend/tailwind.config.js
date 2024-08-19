/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./src/**/*.{js,jsx,ts,tsx}"],
  theme: {
    extend: {
      fontFamily: {
        header: ["Libre Baskerville", "sans-serif"],
        body: ["Nunito Sans", "sans-serif"],
      },
      colors: {
        primary: {
          lighter: "#6B9ADB",
          light: "#3A78CF",
          DEFAULT: "#285EA4",
          dark: "#1C4273",
          darker: "#102542",
        },
        secondary: {
          light: "#ffffff",
          DEFAULT: "#ffffff",
          dark: "#ffffff",
        },
      },
    },
  },
  plugins: [],
};
