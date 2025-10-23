import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        'hebrew': ['Noto Sans Hebrew', 'SBL Hebrew', 'serif'],
        'mono': ['JetBrains Mono', 'monospace'],
      },
      colors: {
        earth: '#8B4513',
        sky: '#87CEEB',
        gold: '#DAA520',
        olive: '#808000',
        crimson: '#DC143C',
        purple: '#663399',
        text: '#2C3E50',
        muted: '#7F8C8D',
      },
      direction: {
        'rtl': 'rtl',
      },
      animation: {
        'fade-in': 'fadeIn 0.5s ease-in-out',
        'slide-up': 'slideUp 0.3s ease-out',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { transform: 'translateY(10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
      },
    },
  },
  plugins: [],
};

export default config;
