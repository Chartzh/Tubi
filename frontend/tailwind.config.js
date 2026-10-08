/** @type {import('tailwindcss').Config} */
export default {
  content: ['./src/**/*.{html,js,svelte,ts}'],
  theme: {
    extend: {
      colors: {
        tubi: {
          bg: '#0b0d13',
          card: '#131620',
          elevated: '#1a1e2c',
          border: '#212638',
          text: '#f3f4f6',
          muted: '#94a3b8',
          accent: '#e11d48',
          'accent-hover': '#be123c',
        }
      }
    },
  },
  plugins: [],
};
