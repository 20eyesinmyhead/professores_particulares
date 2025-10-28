

# professores_voluntarios/users/urls.py (MODIFICAR)

from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    # URL 1: Lista de professores com busca
    path('', views.lista_professores, name='lista'),
    
    # URL 2: Nova URL para listar apenas voluntários
    path('voluntarios/', views.lista_voluntarios, name='voluntarios'), # <-- ADICIONAR ESTA LINHA
]