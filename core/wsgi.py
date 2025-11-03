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
# Esta linha é OBRIGATÓRIA para o logo, css, etc.
application = WhiteNoise(application, root=settings.STATIC_ROOT)

# 2. REMOVIDO: O bloco de arquivos de mídia foi removido.
# O WhiteNoise (com add_files) não é adequado para arquivos de mídia
# (como fotos de perfil) porque ele só escaneia a pasta no startup.
# O upload de arquivos não seria detectado.
# Vamos configurar o 'urls.py' para servir esses arquivos.
#
# if settings.MEDIA_ROOT:
#    application.add_files(settings.MEDIA_ROOT, prefix=settings.MEDIA_URL)
