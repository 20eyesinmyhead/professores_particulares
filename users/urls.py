from django.urls import path
from django.contrib.auth import views as auth_views # Views padrões do Django para login/logout
from . import views

app_name = 'users'

urlpatterns = [
    # ----------------------------------------------------------------------
    # 1. AUTENTICAÇÃO PADRÃO (Django Auth)
    # ----------------------------------------------------------------------
    # CORREÇÃO: Usa auth_views para evitar o AttributeError
    path('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    
    # ----------------------------------------------------------------------
    # 2. FLUXOS PERSONALIZADOS
    # ----------------------------------------------------------------------
    
    # Registro (View Unificada)
    path('registro/', views.registro, name='registro'),
    
    # Edição de Perfil (View Unificada para CustomUser e ProfessorProfile)
    path('perfil/editar/', views.editar_perfil, name='editar_perfil'),

    # CORREÇÃO DE ORDEM: A rota MAIS ESPECÍFICA (excluir) deve vir ANTES da rota genérica (username)
    path('perfil/excluir/', views.excluir_conta, name='excluir_conta'),
    
    # ADICIONADO: Nova rota para "Minhas Mensagens"
    path('perfil/mensagens/', views.minhas_mensagens, name='minhas_mensagens'),

    # Detalhe de Perfil (Mostra o perfil de qualquer usuário, usa o username)
    path('perfil/<str:username>/', views.perfil_detalhe, name='perfil_detalhe'),
    
    # ----------------------------------------------------------------------
    # 3. LISTAGEM E BUSCA DE PROFESSORES
    # ----------------------------------------------------------------------
    
    # Lista principal de professores (com busca)
    path('', views.lista_professores, name='lista_professores'),
    
    # Lista de professores voluntários (usa o mesmo view com um argumento extra)
    path('voluntarios/', views.lista_professores, {'somente_voluntarios': True}, name='lista_voluntarios'),
    
    # ----------------------------------------------------------------------
    # 4. FUNCIONALIDADE DE CONTATO
    # ----------------------------------------------------------------------
    
    # Contato com um professor específico (usa a PK do CustomUser professor)
    path('contato/<int:professor_pk>/', views.contato_professor, name='contato_professor'),

    # Rota para a página 'Sobre Nós'
    path('sobre/', views.sobre_nos, name='sobre_nos'),
]

from django.urls import path
# Importa as views de autenticação prontas do Django (para login/logout)
from django.contrib.auth import views as auth_views 
# Importa as views customizadas (ex: registro, perfil) do 'views.py'
from . import views

# Define um "namespace" para este aplicativo.
# Isso permite usar URLs como 'users:login' ou 'users:perfil_detalhe'
# nos templates, evitando conflito com outros aplicativos.
app_name = 'users'

urlpatterns = [
    # ----------------------------------------------------------------------
    # 1. AUTENTICAÇÃO PADRÃO (Django Auth)
    # ----------------------------------------------------------------------
    
    # Usa a view de Login padrão do Django, mas aponta para o nosso template customizado.
    path('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name='login'),
    
    # Usa a view de Logout padrão do Django (não precisa de template).
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    
    # ----------------------------------------------------------------------
    # 2. FLUXOS PERSONALIZADOS (Registro e Perfis)
    # ----------------------------------------------------------------------
    
    # Rota para a página de registro (usa a view 'registro' do views.py)
    path('registro/', views.registro, name='registro'),
    
    # Rota para a página de edição de perfil do usuário logado
    path('perfil/editar/', views.editar_perfil, name='editar_perfil'),

    # Rota para a "Zona de Perigo" (excluir conta).
    # Esta rota DEVE vir ANTES da rota '<str:username>' porque o Django
    # lê as URLs em ordem. Se viesse depois, '/perfil/excluir/' seria
    # interpretado como um 'username' chamado "excluir".
    path('perfil/excluir/', views.excluir_conta, name='excluir_conta'),
    
    # Rota para a caixa de entrada de mensagens do usuário
    path('perfil/mensagens/', views.minhas_mensagens, name='minhas_mensagens'),

    # Rota de Perfil Dinâmica:
    # Captura um valor da URL (ex: 'joao123') e o passa
    # para a view 'perfil_detalhe' como um argumento 'username'.
    path('perfil/<str:username>/', views.perfil_detalhe, name='perfil_detalhe'),
    
    # ----------------------------------------------------------------------
    # 3. LISTAGEM E BUSCA (Páginas Principais)
    # ----------------------------------------------------------------------
    
    # A URL raiz do aplicativo (ex: 'professorcerto.onrender.com/')
    # usa a view 'lista_professores'. Esta é a home page.
    path('', views.lista_professores, name='lista_professores'),
    
    # Rota para voluntários.
    # Esta é uma rota inteligente: ela REUTILIZA a mesma view 'lista_professores',
    # mas passa um argumento extra {'somente_voluntarios': True} para a função.
    path('voluntarios/', views.lista_professores, {'somente_voluntarios': True}, name='lista_voluntarios'),
    
    # ----------------------------------------------------------------------
    # 4. FUNCIONALIDADE DE CONTATO E PÁGINAS ESTÁTICAS
    # ----------------------------------------------------------------------
    
    # Rota de Contato Dinâmica:
    # Captura o ID do professor (um número inteiro) da URL e o passa
    # para a view 'contato_professor' como 'professor_pk'.
    path('contato/<int:professor_pk>/', views.contato_professor, name='contato_professor'),

    # Rota para a página estática 'Sobre Nós'
    path('sobre/', views.sobre_nos, name='sobre_nos'),
]