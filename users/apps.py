# users/apps.py

from django.apps import AppConfig

class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'

    def ready(self):
        # A simples importação do módulo de tags FORÇA o registro.
        #try:
            # Atenção: O nome aqui DEVE ser o nome do seu arquivo renomeado!
            import users.templatetags.perfil_tags 
        #except ImportError:
            #pass