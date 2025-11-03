from django.contrib import admin
from django.urls import path, include

# 1. IMPORTAÇÕES ADICIONADAS
# Necessário para servir arquivos estáticos (logo.jpg) e de mídia (fotos de perfil)
# durante o desenvolvimento (DEBUG=True)
from django.conf import settings
from django.conf.urls.static import static

# 2. REMOVIDA A IMPORTAÇÃO DESNECESSÁRIA
# A view 'lista_professores' não é mais necessária aqui,
# pois o 'include' abaixo cuidará dela.
# from users.views import lista_professores 

urlpatterns = [
    # Rota de Administrador
    path('admin/', admin.site.urls),
    
    # 3. CORREÇÃO DA ROTA RAIZ
    # Removemos a linha duplicada 'path('', lista_professores...)'
    # Esta única linha agora controla a página inicial (que vai para 'users:lista_professores')
    # E também todas as outras URLs do app 'users' (como /registro/, /perfil/, etc.)
    path('', include('users.urls', namespace='users')),

    # Rotas de autenticação padrão (para reset de senha, etc.)
    path('accounts/', include('django.contrib.auth.urls')),
]

# 4. ADIÇÃO PARA SERVIR ARQUIVOS DE MÍDIA

# Em MODO DE DESENVOLVIMENTO (DEBUG=True)
# Isso permite que o runserver local encontre suas fotos de perfil
if settings.DEBUG:
    # (Não precisamos de STATIC_URL, o WhiteNoise cuida disso)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# 5. REMOVIDO: Bloco de Mídia em Produção (WhiteNoise cuidará disso no wsgi.py)
# if not settings.DEBUG:
#     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

