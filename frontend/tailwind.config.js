/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./app/**/*.{js,jsx,ts,tsx}",
    "./components/**/*.{js,jsx,ts,tsx}",
  ],
  presets: [require("nativewind/preset")],
  theme: {
    extend: {
      colors: {
        closet: {
          primary: "#2D3142",
          secondary: "#4F5D75",
          accent: "#BFC0C0",
          surface: "#EFEFEF",
        },
      },
    },
  },
  plugins: [],
};
