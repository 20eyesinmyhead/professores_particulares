from django.urls import path
from django.contrib.auth import views as auth_views # Views padrões do Django para login/logout
from . import views

app_name = 'users'

urlpatterns = [
    # ----------------------------------------------------------------------
    # 1. AUTENTICAÇÃO PADRÃO (Django Auth)
    # ----------------------------------------------------------------------
    # Opcional: usar o LoginView padrão, mas apontando para nosso template
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
    
    # Detalhe de Perfil (Mostra o perfil de qualquer usuário, usa o username)
    path('perfil/<str:username>/', views.perfil_detalhe, name='perfil_detalhe'),
    
    # ----------------------------------------------------------------------
    # 3. LISTAGEM E BUSCA DE PROFESSORES
    # ----------------------------------------------------------------------
    
    # Lista principal de professores (com busca)
    # Rota raiz do app 'users' (pode ser /professores/ no projeto principal)
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

    # Rota para a página 'Minhas Mensagens'
    path('mensagens/', views.minhas_mensagens, name='minhas_mensagens'),
]
