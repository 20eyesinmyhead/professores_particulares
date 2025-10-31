from django.contrib import admin
from django.contrib.auth.admin import UserAdmin 
from .models import CustomUser # Importa o novo modelo de usuário unificado

# Define a classe de administração para o CustomUser.
# Herdamos de UserAdmin para manter todas as funcionalidades padrão do Django (senha, permissões, etc.)
class CustomUserAdmin(UserAdmin):
    # Campos que você quer que apareçam na lista de usuários no Admin
    list_display = ('username', 'email', 'nome_completo', 'is_professor', 'is_staff')
    
    # 1. RESOLVENDO fieldsets E012: 
    # Usamos o fieldsets original e o modificamos para adicionar nossos campos customizados.
    # O UserAdmin.fieldsets é uma tupla, e as tuplas são imutáveis.
    # UserAdmin.fieldsets[1] contém o bloco 'Personal info' (first_name, last_name, email).
    # Como já adicionamos 'nome_completo' e 'biografia' (e removemos first/last name do CustomUser)
    # vamos sobrescrever o fieldset 'Personal info' (índice 1) e adicionar um novo no final.
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}), # Bloco 0: Autenticação
        ('Informações Pessoais', {'fields': ('nome_completo', 'email', 'biografia', 'cidade', 'foto_perfil')}), # Bloco 1: Customizado
        ('Permissões', {'fields': ('is_active', 'is_professor', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}), # Bloco 2: Permissões
        ('Datas Importantes', {'fields': ('last_login', 'date_joined')}), # Bloco 3: Datas
    )

    # 2. RESOLVENDO fields.E304 (Clash de Acessores Reversos)
    # Esta linha garante que o Django saiba como tratar os campos de grupos e permissões
    # em um modelo customizado que herda de AbstractUser, evitando o clash com auth.User
    filter_horizontal = ('groups', 'user_permissions',)
    
    # Permite buscar pelo nome completo
    search_fields = ('username', 'email', 'nome_completo')
    ordering = ('username',)

# Registra o novo modelo CustomUser com a classe de administração customizada
admin.site.register(CustomUser, CustomUserAdmin)

# Não precisamos registrar o modelo Professor (nem o Aluno), pois eles foram eliminados.