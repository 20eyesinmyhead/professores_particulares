"""
Definição dos Modelos (Tabelas) para o aplicativo 'users'.

Este arquivo contém a estrutura de todo o banco de dados do aplicativo:
1. CustomUserManager: Gerencia a criação de usuários.
2. CustomUser: A tabela central de usuários (alunos e professores).
3. ProfessorProfile: Uma extensão do CustomUser com dados de professor.
4. ContactProfessor: A tabela que armazena as mensagens de contato.
"""

from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import gettext_lazy as _
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings

# ==============================================================================
# 1. CUSTOM USER MANAGER
# ==============================================================================

class CustomUserManager(BaseUserManager):
    """
    Gerenciador customizado para o modelo 'CustomUser'.
    Necessário pois sobrescrevemos o modelo de usuário padrão para
    usar 'email' como o campo de login (USERNAME_FIELD).
    """
    
    def create_user(self, email, password=None, **extra_fields):
        """
        Cria e salva um usuário comum com o email e senha fornecidos.
        """
        if not email:
            raise ValueError(_('O email deve ser fornecido'))
        
        email = self.normalize_email(email)
        
        # 'username' ainda é necessário (definido em REQUIRED_FIELDS)
        username = extra_fields.get('username')
        if not username:
            # Fornece um fallback se o username não for passado
            username = email.split('@')[0] 
            
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Cria e salva um superusuário (admin) com o email e senha fornecidos.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser deve ter is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser deve ter is_superuser=True.'))
            
        return self.create_user(email, password, **extra_fields)

# ==============================================================================
# 2. CUSTOM USER MODEL (Tabela Principal)
# ==============================================================================

class CustomUser(AbstractUser):
    """
    Modelo de Usuário customizado (substitui o 'User' padrão do Django).
    Armazena todos os dados comuns a Alunos e Professores.
    """
    
    # --- Campos de Autenticação ---
    # Sobrescreve 'AbstractUser' para tornar 'email' o login e ser único.
    email = models.EmailField(_('endereço de email'), unique=True)
    
    # Remove 'first_name' e 'last_name' padrão do Django.
    first_name = None
    last_name = None
    
    # --- Campos de Perfil Pessoal (Comuns a todos) ---
    nome_completo = models.CharField(_('Nome Completo'), max_length=150, blank=False)
    como_deseja_ser_chamado = models.CharField(_('Como Deseja Ser Chamado'), max_length=50, blank=True)
    cpf = models.CharField(_('CPF'), max_length=14, unique=True, null=True, blank=True)
    telefone = models.CharField(_('Telefone'), max_length=20, blank=True)
    data_nascimento = models.DateField(_('Data de Nascimento'), null=True, blank=True)
    
    # --- Localização ---
    cidade = models.CharField(_('Cidade'), max_length=100, blank=True)
    cep = models.CharField(_('CEP'), max_length=10, blank=True)
    
    # --- Campos de Perfil Detalhado (Aluno/Geral) ---
    foto_perfil = models.ImageField(_('Foto de Perfil'), upload_to='profile_pics/', null=True, blank=True)
    escolaridade = models.TextField(_('Escolaridade'), blank=True)
    interesses = models.TextField(_('Interesses e Hobbies'), blank=True)
    historico_aprendizagem = models.TextField(_('Histórico de Aprendizagem (Aluno)'), blank=True)
    biografia = models.TextField(_('Biografia Pessoal'), blank=True)
    
    # --- Campo de Papel (Role) ---
    # Este campo 'liga' o perfil de professor
    is_professor = models.BooleanField(_('É Professor'), default=False, 
        help_text=_('Designa se este usuário ativou a modalidade professor.')
    )
    
    # --- Configuração do Modelo ---
    objects = CustomUserManager() # Usa o gerenciador customizado
    
    USERNAME_FIELD = 'email' # Define 'email' como o campo de login
    REQUIRED_FIELDS = ['username', 'nome_completo'] # Campos pedidos no 'createsuperuser'

    class Meta:
        verbose_name = _('Usuário')
        verbose_name_plural = _('Usuários')

    def __str__(self):
        # Representação em texto do objeto (ex: no Admin)
        return self.email

    def get_full_name(self):
        # Método usado pelo Django para obter o nome principal
        return self.nome_completo
    
# ==============================================================================
# 3. PERFIL DE EXTENSÃO: PROFESSOR PROFILE
# ==============================================================================

class ProfessorProfile(models.Model):
    """
    Extensão do modelo 'CustomUser' com dados específicos de Professores.
    Usa um relacionamento "Um-para-Um" (OneToOneField), significando que
    um usuário só pode ter um perfil de professor, e vice-versa.
    """
    
    
    # --- Vínculo com Usuário ---
    # 'on_delete=models.CASCADE': Se o CustomUser for apagado, este perfil também será.
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='professorprofile' # Permite acesso reverso: user.professorprofile
    )
    
    # --- Informações Profissionais ---
    disciplinas = models.TextField(_('Disciplinas Lecionadas'), 
        help_text=_('Ex: Matemática, Física, Português. Separe por vírgulas.')
    )
    tarifa_hora = models.DecimalField(_('Tarifa por Hora (R$)'), max_digits=6, decimal_places=2, null=True, blank=True)
    curriculum = models.TextField(_('Conteúdo do Currículo'), blank=True, 
        help_text=_('Experiência profissional relevante, certificações, etc.')
    )
    bio_profissional = models.TextField(_('Bio Profissional'), blank=True, 
        help_text=_('Breve descrição da sua experiência e qualificações.')
    )
    sobre_a_aula = models.TextField(_('Sobre a Aula'), blank=True, 
        help_text=_('Detalhes sobre sua metodologia e formato de aula.')
    )
    
    # --- Mídias ---
    foto_profissional = models.ImageField(_('Foto Profissional'), upload_to='professor_pics/', null=True, blank=True, 
        help_text=_('Uma foto específica para seu perfil profissional.')
    )

    # --- Configurações e Status ---
    MODALIDADE_CHOICES = (
        ('P', 'Presencial'),
        ('O', 'Online'),
        ('AD', 'Domicílio do Aluno'),
        ('AP', 'Domicílio do Professor'),
        ('TO', 'Todos (Presencial e Online)')
    )
    modalidades = models.CharField(_('Modalidades de Aula'), max_length=2, choices=MODALIDADE_CHOICES, default='O', blank=True)
    is_voluntario = models.BooleanField(_('É Voluntário'), default=False)
    aceita_online = models.BooleanField(_('Aceita Aulas Online'), default=False)
    aceita_grupo = models.BooleanField(_('Aceita Aulas em Grupo'), default=False)
    status_ativo = models.BooleanField(_('Ativamente Aceitando Alunos'), default=True)
    data_validacao = models.DateField(_('Data de Ativação do Perfil'), null=True, blank=True)
    
    # --- Métricas (a serem calculadas por outra lógica) ---
    media_avaliacoes = models.DecimalField(_('Média de Avaliações'), max_digits=3, decimal_places=2, default=0.00)

    class Meta:
        verbose_name = _('Perfil de Professor')
        verbose_name_plural = _('Perfis de Professores')

    def __str__(self):
        return f"Perfil de {self.user.get_full_name()}"


# ==============================================================================
# 4. MODELO DE CONTATO: CONTACT PROFESSOR
# ==============================================================================

class ContactProfessor(models.Model):
    """
    Armazena cada mensagem enviada de um Aluno para um Professor.
    Funciona como o "histórico" de contatos da plataforma.
    """
    
    
    # --- Vínculos (Chaves Estrangeiras) ---
    
    # 'aluno': O remetente. 
    # 'on_delete=models.SET_NULL': Se o aluno for excluído, a mensagem 
    # é mantida, mas o campo 'aluno' fica nulo.
    aluno = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='mensagens_enviadas', 
        verbose_name=_('Aluno Remetente')
    )
    
    # 'professor': O destinatário.
    # 'on_delete=models.CASCADE': Se o professor for excluído, todas as 
    # mensagens recebidas por ele também são excluídas.
    professor = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='mensagens_recebidas', 
        verbose_name=_('Professor Destinatário')
    )
    
    # --- Conteúdo da Mensagem ---
    assunto = models.CharField(_('Assunto'), max_length=150)
    mensagem = models.TextField(_('Mensagem'))
    
    # --- Metadados ---
    lida = models.BooleanField(_('Lida pelo Professor'), default=False)
    data_envio = models.DateTimeField(_('Data de Envio'), auto_now_add=True) # Preenchido automaticamente
    
    class Meta:
        verbose_name = _('Mensagem de Contato')
        verbose_name_plural = _('Mensagens de Contato')
        # Ordena as mensagens da mais nova para a mais antiga por padrão
        ordering = ['-data_envio']

    def __str__(self):
        aluno_str = self.aluno.username if self.aluno else _("Usuário Excluído")
        return f"Mensagem de {aluno_str} para {self.professor.username}"


# ==============================================================================
# 5. SIGNALS (Automação entre Modelos)
# ==============================================================================

@receiver(post_save, sender=CustomUser)
def ensure_professor_profile(sender, instance, **kwargs):
    """
    Signal (disparado após 'CustomUser' ser salvo) para garantir que um
    'ProfessorProfile' exista se o usuário tiver 'is_professor' = True.
    
    Isso é mais eficiente e limpo do que os dois signals anteriores.
    O 'get_or_create' só cria o perfil se ele ainda não existir.
    """
    if instance.is_professor:
        # Tenta buscar o perfil; se não existir, cria um novo.
        ProfessorProfile.objects.get_or_create(user=instance)