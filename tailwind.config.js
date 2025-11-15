/** @type {import('tailwindcss').Config} */
// O comentário acima (/** @type ... */) habilita o
// intellisense (autocompletar) em editores como o VS Code.

module.exports = {
  // ===================================================================
  // SEÇÃO "CONTENT" (Conteúdo)
  // -------------------------------------------------------------------
  // Esta é a configuração mais importante.
  // Ela diz ao Tailwind para "assistir" estes arquivos. Qualquer
  // classe Tailwind (ex: 'text-center', 'py-4') usada nestes
  // arquivos será incluída no arquivo CSS final.
  // ===================================================================
  content: [
    
    // Padrão 1: Monitora todos os arquivos .html
    // na pasta 'templates' de qualquer aplicativo.
    // Ex: 'users/templates/users/login.html'
    './**/templates/**/*.html',
    
    // Padrão 2: Monitora arquivos .js
    // (Útil se você adicionar/remover classes Tailwind via JavaScript)
    './static/**/*.js',

    // Padrão 3 (Opcional, mas recomendado para o Django):
    // Monitora arquivos .py, caso você use classes CSS
    // em seus 'forms.py' (em widgets).
    './**/*.py' 
  ],
  
  // ===================================================================
  // SEÇÃO "THEME" (Tema)
  // -------------------------------------------------------------------
  // Aqui é onde você customiza o design padrão do Tailwind.
  // ===================================================================
  theme: {
    // 'extend' permite adicionar novas cores, fontes ou tamanhos
    // SEM remover os padrões do Tailwind.
    extend: {
      // Exemplo (descomentado):
      // Aqui você poderia adicionar a cor "âmbar"
      // principal do seu site como um nome customizado.
      //
      // colors: {
      //   'brand-primary': '#f59e0b', // (Tom de Âmbar)
      // }
      //
      // Isso permitiria usar classes como 'bg-brand-primary'.
    },
  },

  // ===================================================================
  // SEÇÃO "PLUGINS"
  // -------------------------------------------------------------------
  // Aqui você pode adicionar plugins que estendem
  // a funcionalidade do Tailwind (ex: plugins para formulários
  // ou tipografia).
  // ===================================================================
  plugins: [
    // Exemplo: 
    // require('@tailwindcss/forms'),
  ],
}