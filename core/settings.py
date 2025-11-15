"""
Configurações do Django para o projeto "Professor Certo".

Este arquivo gerencia as configurações do projeto, alternando dinamicamente
entre o ambiente de desenvolvimento (local) e o de produção (hospedado no Render).
"""

import os
from pathlib import Path
import dj_database_url

# Define o diretório base do projeto (a pasta que contém 'manage.py')
BASE_DIR = Path(__file__).resolve().parent.parent

# --- Configurações de Segurança e Ambiente ---

# Carrega a chave secreta a partir de uma variável de ambiente em produção (Render)
# ou usa uma chave local insegura apenas para desenvolvimento.
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-#vv6=3)!8f96h@_-w+jz84&1v9b=1k56^p4eg7+$#$$3mrgkk-')

# Define o modo DEBUG. É 'False' em produção (quando a variável 'RENDER' existe)
# e 'True' localmente, para exibir erros detalhados durante o desenvolvimento.
DEBUG = 'True'

# Lista de hosts permitidos.
ALLOWED_HOSTS = []

# Em produção, adiciona automaticamente o hostname fornecido pelo Render.
RENDER_EXTERNAL_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)
    # Exemplo: ALLOWED_HOSTS.append('www.professorcerto.com')


# --- Configuração de Aplicações e Middlewares ---

# Lista de aplicações que compõem o projeto.
INSTALLED_APPS = [
    # Aplicações padrão do Django
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Aplicação principal do projeto
    'users',
]

# Middlewares processam requisições e respostas globalmente.
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    # WhiteNoise: Serve arquivos estáticos (CSS, JS) de forma eficiente em produção.
    # Deve vir logo após o SecurityMiddleware.
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Define o arquivo 'urls.py' principal do projeto.
ROOT_URLCONF = 'core.urls'

# Configuração do motor de templates do Django.
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# Define a interface WSGI para o servidor web em produção.
WSGI_APPLICATION = 'core.wsgi.application'


# --- Configuração do Banco de Dados (Dinâmico) ---

# Configuração do banco de dados que alterna automaticamente.
DATABASES = {
    'default': dj_database_url.config(
        # Em produção (Render): lê a variável de ambiente 'DATABASE_URL' (PostgreSQL).
        # Em desenvolvimento (Local): usa o 'default' abaixo (sqlite3).
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
        conn_max_age=600
    )
}


# --- Validação de Senhas ---

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',},
]


# --- Configurações de Internacionalização (Português-Brasil) ---

LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_TZ = True


# --- Configuração de Arquivos Estáticos (CSS, JS) ---

# URL base para servir arquivos estáticos
STATIC_URL = '/static/'
# Onde o Django procura arquivos estáticos (além das pastas 'static' dos apps)
STATICFILES_DIRS = [ os.path.join(BASE_DIR, 'static'), ]
# Onde o 'collectstatic' reunirá todos os arquivos para produção
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
# Armazenamento otimizado do WhiteNoise (com compressão)
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'


# --- Configuração de Mídia (Uploads dos Usuários) ---

# URL base para servir os arquivos enviados pelos usuários (ex: fotos de perfil)
MEDIA_URL = '/media/'

# Lógica para alternar o local de armazenamento de mídia
if 'RENDER' in os.environ:
    # Em produção: Aponta para o "Mount Path" do Disco Persistente no Render.
    # Este caminho é lido da variável de ambiente 'MEDIA_ROOT_PATH'.
    MEDIA_ROOT = os.environ.get('MEDIA_ROOT_PATH', os.path.join(BASE_DIR, 'media'))
else:
    # Em desenvolvimento: Usa a pasta 'media' local.
    MEDIA_ROOT = BASE_DIR / 'media'


# --- Configurações Específicas do Projeto ---

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Redirecionamentos padrão após login/logout
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

# Informa ao Django para usar o modelo de usuário customizado
AUTH_USER_MODEL = 'users.CustomUser'


# --- Configuração de E-mail (Produção vs. Desenvolvimento) ---

EMAIL_SUBJECT_PREFIX = '[Professor Certo] '

if 'RENDER' in os.environ:
    # Em produção: Usa o SendGrid via SMTP.
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = 'smtp.sendgrid.net'
    EMAIL_PORT = 587
    EMAIL_USE_TLS = True
    # As credenciais são lidas das variáveis de ambiente do Render.
    EMAIL_HOST_USER = 'apikey' # Nome de usuário fixo para o SendGrid
    EMAIL_HOST_PASSWORD = os.environ.get('SENDGRID_API_KEY')
    DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL') # E-mail verificado no SendGrid
else:
    # Em desenvolvimento: Imprime e-mails no console, em vez de enviá-los.
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
    DEFAULT_FROM_EMAIL = 'noreply@desenvolvimento.com'