// tailwind.config.js
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './templates/**/*.html',         // Para templates na pasta raiz 'templates'
    './**/templates/**/*.html',      // Para templates dentro de pastas 'templates' em apps Django
    './static/**/*.js',              // Se você tiver JavaScript que usa classes Tailwind
    // Adicione outros caminhos se você tiver classes Tailwind em outros tipos de arquivos
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}