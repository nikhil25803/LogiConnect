import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        backgroundPrimary: "#FFFFFF",
        backgroundSecondary: "#F4F6F9",
        textWhite: "#FFFFFF",
        textDark: "#141414",
        textPrimary: "#F67366",
        textSecondary: "#2C2D5B",
        textLight: "#333333",
      },
      fontFamily: {
        poppins: ["Poppins"],
        montserrat: ["Montserrat", "sans-serif"],
      },
    },
  },
  plugins: [],
};
export default config;
