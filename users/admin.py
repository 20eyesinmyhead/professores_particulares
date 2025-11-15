"""
Configuração do Painel de Administração do Django para o app 'users'.

Este arquivo "registra" os modelos do 'models.py' na interface de
administração do Django, permitindo que os superusuários gerenciem
os dados do site (ex: editar usuários, ver perfis).
"""

from django.contrib import admin
# 'UserAdmin' é a classe base do Django que já vem com toda a
# lógica de gerenciamento de usuários (mudança de senha, permissões, etc.)
from django.contrib.auth.admin import UserAdmin 
# Importa o modelo que queremos registrar
from .models import CustomUser 

# ==============================================================================
# 1. Configuração de Admin para o 'CustomUser'
# ==============================================================================

class CustomUserAdmin(UserAdmin):
    """
    Define a aparência e o comportamento do modelo 'CustomUser'
    dentro do Painel de Administração.
    
    Herdamos de 'UserAdmin' para aproveitar toda a funcionalidade
    padrão de gerenciamento de senhas e permissões do Django.
    """
    
    # --- Configurações da Lista de Usuários (list_display) ---
    
    # Define quais colunas aparecerão na lista principal de usuários
    list_display = (
        'username', 
        'email', 
        'nome_completo', 
        'is_professor', # Campo customizado
        'is_staff'      # Campo padrão (permite acesso ao admin)
    )
    
    # --- Configuração da Página de Edição (fieldsets) ---
    
    # 'fieldsets' organiza os campos na página de edição do usuário.
    # Nós sobrescrevemos o 'fieldsets' padrão do 'UserAdmin' para
    # remover 'first_name'/'last_name' e adicionar nossos campos customizados.
    fieldsets = (
        # Bloco 1: (sem título) - Campos de Autenticação
        (None, {'fields': ('username', 'password')}),
        
        # Bloco 2: Informações Pessoais (Customizado)
        ('Informações Pessoais', {'fields': (
            'nome_completo', 
            'email', 
            'biografia', 
            'cidade', 
            'foto_perfil'
        )}),
        
        # Bloco 3: Permissões
        ('Permissões', {'fields': (
            'is_active', 
            'is_professor', # Nosso campo de "papel"
            'is_staff', 
            'is_superuser', 
            'groups', 
            'user_permissions'
        )}),
        
        # Bloco 4: Datas (padrão do Django)
        ('Datas Importantes', {'fields': ('last_login', 'date_joined')}),
    )

    # --- Configurações Adicionais ---
    
    # 'filter_horizontal' melhora a interface de seleção para
    # campos "Muitos-para-Muitos" (como grupos e permissões),
    # transformando-a em uma caixa de seleção dupla ("disponíveis" vs "escolhidos").
    filter_horizontal = ('groups', 'user_permissions',)
    
    # Adiciona a capacidade de buscar usuários por estes campos
    search_fields = ('username', 'email', 'nome_completo')
    
    # Define a ordenação padrão na lista de usuários
    ordering = ('username',)

# ==============================================================================
# 2. Registro dos Modelos
# ==============================================================================

# Diz ao Django: "Gerencie o modelo 'CustomUser' usando as
# configurações definidas na classe 'CustomUserAdmin'."
admin.site.register(CustomUser, CustomUserAdmin)

# Nota: Não registramos 'ProfessorProfile' ou 'ContactProfessor' aqui
# (embora pudéssemos). 'ProfessorProfile' é gerenciado "dentro" do
# 'CustomUser' pela lógica de 'is_professor'.