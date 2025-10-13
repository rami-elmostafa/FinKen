/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#FFD100',
          dark: '#FFC900',
          light: '#FFEB99',
        },
        secondary: {
          DEFAULT: '#333333',
          light: '#555555',
          dark: '#000000',
        },
        accent: {
          blue: '#0b6ea8',
          green: '#28a745',
          red: '#dc3545',
          yellow: '#ffc107',
          orange: '#fd7e14',
        },
        gray: {
          50: '#f8f9fa',
          100: '#f0f0f0',
          200: '#e9ecef',
          300: '#dee2e6',
          400: '#ced4da',
          500: '#adb5bd',
          600: '#6c757d',
          700: '#495057',
          800: '#343a40',
          900: '#212529',
        },
      },
      fontFamily: {
        sans: ['Segoe UI', 'Tahoma', 'Geneva', 'Verdana', 'sans-serif'],
      },
      borderRadius: {
        'card': '25px',
      },
      boxShadow: {
        'card': '0 4px 8px rgba(0, 0, 0, 0.08)',
        'elevated': '0 2px 8px rgba(0, 0, 0, 0.1)',
      },
    },
  },
  plugins: [],
}
