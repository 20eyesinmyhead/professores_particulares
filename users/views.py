# professores_voluntarios/users/views.py

from django.shortcuts import render
from django.db.models import Q # <--- ESSENCIAL PARA FILTRO COM 'OU'
from .models import Professor

def lista_professores(request):
    
    # 1. Pega o termo de busca 'q' da URL. O termo virá da caixa de busca do formulário.
    # O segundo parâmetro (a string vazia '') é o valor padrão se 'q' não estiver na URL.
    termo_busca = request.GET.get('q', '')
    
    # Começa com todos os professores
    professores = Professor.objects.all()
    
    if termo_busca:
        # 2. Se houver um termo, aplica o filtro:
        
        # O Q() permite usar o operador OR (|) entre diferentes condições de filtro.
        # __icontains é a busca por 'contém o texto' sem se importar com MAIÚSCULAS/minúsculas.
        professores = professores.filter(
            Q(disciplina__icontains=termo_busca) | 
            Q(nome_completo__icontains=termo_busca)
        ).distinct()
        
    # Ordena os resultados pelo nome
    professores = professores.order_by('nome_completo')
        
    context = {
        'titulo': 'Encontre seu Professor Particular',
        'professores': professores,
        # O termo de busca é adicionado ao contexto, embora não seja estritamente necessário 
        # para a lista.html, ajuda na debug (e o template usa request.GET.q)
    }
    
    # 3. Retorna a página com o contexto (lista filtrada)
    return render(request, 'users/lista.html', context)
# professores_voluntarios/users/views.py (ADICIONAR)

def lista_voluntarios(request):
    
    # Busca APENAS os professores onde 'is_voluntario' é True
    professores = Professor.objects.filter(is_voluntario=True).order_by('nome_completo')
    
    context = {
        'titulo': 'Professores Voluntários (Aulas Gratuitas)',
        'professores': professores,
        'is_voluntario_page': True # Uma flag para usar no template, se necessário
    }
    
    # Reutilizamos o mesmo template lista.html, já que ele exibe professores
    return render(request, 'users/lista.html', context)