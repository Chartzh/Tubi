/** @type {import('tailwindcss').Config} */
export default {
  content: ['./src/**/*.{html,js,svelte,ts}'],
  theme: {
    extend: {
      colors: {
        tubi: {
          bg: '#0b0d14',
          card: '#131622',
          deck: '#151926',
          elevated: '#1a1f30',
          border: '#23293d',
          'border-focus': '#3b4363',
          text: '#f1f3f9',
          muted: '#8f98af',
          accent: '#e11d48',
          'accent-hover': '#f43f5e',
          cyan: '#00f0ff',
        }
      },
      fontFamily: {
        display: ['"Space Grotesk"', 'sans-serif'],
        mono: ['"JetBrains Mono"', 'monospace'],
        sans: ['Inter', 'sans-serif'],
      }
    },
  },
  plugins: [],
};
