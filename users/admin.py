from django.contrib import admin

# professores_voluntarios/users/admin.py

from django.contrib import admin
from .models import Professor

# Registra o modelo para que ele apareça no painel de administração
admin.site.register(Professor)
