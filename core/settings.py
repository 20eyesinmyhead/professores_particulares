"""
Django settings for core project.
Versão SIMPLIFICADA para usar o Disco Persistente do Render (Plano Starter).
"""
import os 
from pathlib import Path
import dj_database_url 

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# MODIFICADO: Carrega a SECRET_KEY do ambiente (produção) ou usa a sua local (desenvolvimento)
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-#vv6=3)!8f96h@_-w+jz84&1v9b=1k56^p4eg7+$#$$3mrgkk-')

# MODIFICADO: DEBUG é 'False' em produção (quando a var 'RENDER' existir) e 'True' localmente
DEBUG = 'RENDER' not in os.environ

# MODIFICADO: Adiciona o host do Render.com automaticamente em produção
ALLOWED_HOSTS = []

RENDER_EXTERNAL_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)
    # Adicione também o seu domínio customizado se você o configurou
    # ALLOWED_HOSTS.append('www.professorcerto.com') 


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'users',
    # REMOVIDO: 'storages' (não é mais necessário com o Disco Persistente)
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    # ADICIONADO: WhiteNoise Middleware (para arquivos CSS/JS estáticos)
    'whitenoise.middleware.WhiteNoiseMiddleware', 
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'core.urls'

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
      D   },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'


# Database
# Configuração de banco de dados para produção (Render) e fallback para local (sqlite3)
DATABASES = {
    'default': dj_database_url.config(
        # Usa o sqlite3 como padrão se a DATABASE_URL (do Render) não for encontrada
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
        conn_max_age=600
    )
}


# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',},
]


# Internationalization
LANGUAGE_CODE = 'pt-br' 
TIME_ZONE = 'America/Sao_Paulo' 
USE_I18N = True
USE_TZ = True


# ----------------------------------------------------
# CONFIGURAÇÃO DE ARQUIVOS ESTÁTICOS (CSS, JS)
# ----------------------------------------------------

STATIC_URL = '/static/'
STATICFILES_DIRS = [ os.path.join(BASE_DIR, 'static'), ]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# ----------------------------------------------------
# CONFIGURAÇÃO DE MÍDIA (Uploads de Imagens) - SIMPLIFICADO
# ----------------------------------------------------

MEDIA_URL = '/media/'

# Esta é a nova lógica:
if 'RENDER' in os.environ:
    # PRODUÇÃO (Render): Aponta para o "Mount Path" do Disco Persistente
    # Nós definimos 'MEDIA_ROOT_PATH' no ambiente do Render como '/var/data/media'
    MEDIA_ROOT = os.environ.get('MEDIA_ROOT_PATH', os.path.join(BASE_DIR, 'media'))
else:
    # DESENVOLVIMENTO (Local): Aponta para a pasta 'media' no seu PC
    MEDIA_ROOT = BASE_DIR / 'media'


# ----------------------------------------------------
# CONFIGURAÇÕES DO PROJETO (Redirecionamentos, E-mail, Usuário)
# ----------------------------------------------------

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

# Configuração de E-mail (AINDA EM MODO DE DESENVOLVIMENTO - NÃO ENVIA E-MAILS REAIS)
# (Para enviar e-mails reais, você precisará configurar o SendGrid ou similar)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
DEFAULT_FROM_EMAIL = 'noreply@professorcerto.com'
EMAIL_SUBJECT_PREFIX = '[Professor Certo] '

# CONFIGURAÇÃO DE USUÁRIO CUSTOMIZADO
AUTH_USER_MODEL = 'users.CustomUser'

