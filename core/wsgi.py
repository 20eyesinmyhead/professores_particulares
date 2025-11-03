"""
Configuração WSGI para o projeto core.
Isso expõe o WSGI 'callable' como uma variável de nível de módulo chamada ``application``.
"""
import os
from django.core.wsgi import get_wsgi_application
from django.conf import settings
from whitenoise import WhiteNoise

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

# Pega a aplicação Django padrão
application = get_wsgi_application()

# 1. Envolve com o WhiteNoise para servir ARQUIVOS ESTÁTICOS (logo, css)
# O WhiteNoise busca arquivos do STATIC_ROOT (que o 'collectstatic' criou)
application = WhiteNoise(application, root=settings.STATIC_ROOT)

# 2. Adiciona a capacidade de servir ARQUIVOS DE MÍDIA (fotos de perfil)
# O WhiteNoise agora também servirá arquivos do MEDIA_ROOT (o Disco Persistente)
if settings.MEDIA_ROOT:
    application.add_files(settings.MEDIA_ROOT, prefix=settings.MEDIA_URL)
