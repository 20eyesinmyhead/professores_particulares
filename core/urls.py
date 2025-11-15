"""
Configuração de URL principal (Roteador) do projeto "Professor Certo".

Este arquivo é o "roteador" principal do site. Ele lê a URL que o usuário
solicita e direciona a requisição para a view (lógica) correta.
"""

from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
# Import necessário para servir arquivos de mídia em produção (Debug=False)
from django.views.static import serve 

urlpatterns = [
    # 1. Painel de Administração do Django
    # Rota padrão para gerenciar o site, usuários e dados.
    path('admin/', admin.site.urls),

    # 2. Rotas de Autenticação
    # Inclui as URLs padrão do Django para login, logout, reset de senha, etc.
    # Elas serão acessadas em '/accounts/login/', '/accounts/logout/', etc.
    path('accounts/', include('django.contrib.auth.urls')),
    
    # 3. Aplicação Principal 'users'
    # Delega todas as outras URLs (ex: '/', '/perfil/...') para
    # o arquivo 'urls.py' dentro do aplicativo 'users'.
    path('', include('users.urls', namespace='users')),
]

# --- Configuração de Arquivos de Mídia (Uploads) ---

# A configuração de mídia (uploads de usuários) é diferente do 
# gerenciamento de arquivos estáticos (CSS/JS), que é feito pelo WhiteNoise.

if settings.DEBUG:
    # Em Desenvolvimento (DEBUG=True):
    # O 'runserver' local serve os arquivos de mídia (fotos de perfil)
    # diretamente da pasta 'MEDIA_ROOT'.
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

else:
    # Em Produção (DEBUG=False):
    # Esta regra permite que o servidor de aplicação (Render) sirva os arquivos
    # de mídia (fotos) que estão armazenados no Disco Persistente.
    # Isso é necessário para que as fotos de perfil apareçam no site ativo.
    urlpatterns += [
        re_path(r'^media/(?P<path>.*)$', serve, {
            'document_root': settings.MEDIA_ROOT,
        }),
    ]