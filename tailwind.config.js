/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./app/templates/**/*.html",
    "./app/static/**/*.js"
  ],
  theme: {
    extend: {
      colors: {
        'negro': '#0a0a0a',
        'negro-suave': '#111111',
        'gris-oscuro': '#1a1a1a',
        'gris-medio': '#2a2a2a',
        'gris-claro': '#888888',
        'blanco': '#f5f5f5',
        'dorado': '#c9a96e',
        'dorado-claro': '#e8c99a',
      },
      fontFamily: {
        'sans': ['Inter', 'sans-serif'],
        'serif': ['Playfair Display', 'serif'],
      },
      letterSpacing: {
        'widest2': '0.3em',
        'widest3': '0.5em',
      }
    },
  },
  plugins: [],
}