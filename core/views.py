from django.shortcuts import render

def sobre_nos(request):
    """
    Renderiza a página 'Sobre Nós'.
    """
    return render(request, 'core/sobre_nos.html')
