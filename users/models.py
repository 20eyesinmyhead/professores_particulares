from django.db import models

# professores_voluntarios/users/models.py

from django.db import models

class Professor(models.Model):
    """
    Define a estrutura de dados para o perfil de um professor.
    """
    # Dados de Identificação
    nome_completo = models.CharField(max_length=200)
    email = models.EmailField(unique=True) # Garante que cada email é único
    
    # Dados da Aula
    disciplina = models.CharField(max_length=100)
    bio = models.TextField(blank=True, null=True)
    
    # Campo Essencial (Para o seu Diferencial)
    is_voluntario = models.BooleanField(
        default=False,
        help_text="Marque se o professor oferece aulas de forma gratuita/voluntária."
    )
    
    # Data de criação do perfil
    data_cadastro = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Professor"
        verbose_name_plural = "Professores"
        
    def __str__(self):
        # Como o objeto será representado no painel de admin
        return f"{self.nome_completo} ({self.disciplina})"