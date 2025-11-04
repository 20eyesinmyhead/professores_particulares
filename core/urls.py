from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
# ADICIONADO: Import para servir ficheiros em produção
from django.views.static import serve 

# 1. IMPORTAR A VIEW 'sobre_nos' (NECESSÁRIO PARA A ROTA)
from users.views import sobre_nos

urlpatterns = [
    # Rota de Administrador
    path('admin/', admin.site.urls),
    
    # 2. ADICIONADA A ROTA PARA 'SOBRE NÓS' (CORRIGE O ERRO 500)
    path('sobre/', sobre_nos, name='sobre_nos'),
    
    # Rota Raiz (vai para o app 'users' - Lista de Professores)
    path('', include('users.urls', namespace='users')),

    # Rotas de autenticação padrão (para reset de senha, etc.)
    path('accounts/', include('django.contrib.auth.urls')),
]

# 4. SERVIR ARQUIVOS DE MÍDIA

# Em MODO DE DESENVOLVIMENTO (DEBUG=True)
# Isso permite que o runserver local encontre suas fotos de perfil
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# 5. NOVO: SERVIR MÍDIA EM MODO DE PRODUÇÃO (DEBUG=False)
# Isto diz ao Django para servir os ficheiros do 'MEDIA_ROOT' (o Disco Persistente)
# usando a URL 'MEDIA_URL' (/media/)
if not settings.DEBUG:
    urlpatterns += [
        re_path(r'^media/(?P<path>.*)$', serve, {
            'document_root': settings.MEDIA_ROOT,
        }),
    ]

