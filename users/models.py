from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import gettext_lazy as _
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings # Para usar settings.AUTH_USER_MODEL

# ==============================================================================
# 1. CUSTOM USER MANAGER
# ==============================================================================

class CustomUserManager(BaseUserManager):
    """
    Manager de modelo customizado para o CustomUser.
    Sobrescreve create_user e create_superuser.
    """
    def create_user(self, email, password=None, **extra_fields):
        """Cria e salva um usuário com o email e senha fornecidos."""
        if not email:
            raise ValueError(_('O email deve ser fornecido'))
        email = self.normalize_email(email)

        # Garante que 'username' seja tratado corretamente.
        # Remove 'username' de extra_fields para evitar o erro de argumento duplicado.
        username = extra_fields.pop('username', None)
        if not username:
            # Se o username não for fornecido, usa a parte local do email como padrão.
            username = email.split('@')[0]

        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """Cria e salva um superusuário com o email e senha fornecidos."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser deve ter is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser deve ter is_superuser=True.'))
            
        return self.create_user(email, password, **extra_fields)

# ==============================================================================
# 2. CUSTOM USER MODEL (Substituindo o User padrão do Django)
# ==============================================================================

class CustomUser(AbstractUser):
    
    # Sobrescrevendo email para usá-lo como campo obrigatório e único
    email = models.EmailField(_('endereço de email'), unique=True)
    
    # Remove a obrigatoriedade dos campos de nome do AbstractUser (first/last_name)
    first_name = None
    last_name = None
    
    # Adicionamos os campos customizados
    nome_completo = models.CharField(_('Nome Completo'), max_length=150, blank=False)
    como_deseja_ser_chamado = models.CharField(_('Como Deseja Ser Chamado'), max_length=50, blank=True)
    cpf = models.CharField(_('CPF'), max_length=14, unique=True, null=True, blank=True)
    telefone = models.CharField(_('Telefone'), max_length=20, blank=True)
    data_nascimento = models.DateField(_('Data de Nascimento'), null=True, blank=True)
    
    # Localização
    cidade = models.CharField(_('Cidade'), max_length=100, blank=True)
    cep = models.CharField(_('CEP'), max_length=10, blank=True)
    
    # Perfil Geral
    foto_perfil = models.ImageField(_('Foto de Perfil'), upload_to='profile_pics/', null=True, blank=True)
    escolaridade = models.TextField(_('Escolaridade'), blank=True)
    interesses = models.TextField(_('Interesses e Hobbies'), blank=True)
    historico_aprendizagem = models.TextField(_('Histórico de Aprendizagem (Aluno)'), blank=True)
    biografia = models.TextField(_('Biografia Pessoal'), blank=True)
    
    # Campo Chave de Role
    is_professor = models.BooleanField(_('É Professor'), default=False, 
        help_text=_('Designa se este usuário ativou a modalidade professor.')
    )
    
    # Gerenciador customizado
    objects = CustomUserManager()
    
    # Definindo o campo de login padrão como 'username' (padrão do AbstractUser)
    # Mas definindo email como único e required.
    USERNAME_FIELD = 'email'
    # Campos que serão solicitados ao criar usuário via createsuperuser
    REQUIRED_FIELDS = ['username', 'nome_completo'] 

    class Meta:
        verbose_name = _('Usuário')
        verbose_name_plural = _('Usuários')

    def __str__(self):
        return self.email

    def get_full_name(self):
        return self.nome_completo
    
# ==============================================================================
# 3. PERFIL DE EXTENSÃO: PROFESSOR PROFILE
# ==============================================================================

class ProfessorProfile(models.Model):
    MODALIDADE_CHOICES = (
        ('P', 'Presencial'),
        ('O', 'Online'),
        ('AD', 'Domicílio do Aluno'),
        ('AP', 'Domicílio do Professor'),
        ('TO', 'Todos (Presencial e Online)') # Adiciona opção consolidada
    )
    
    # Conexão: One-to-One com o CustomUser
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='professorprofile')
    
    # Detalhes Profissionais
    disciplinas = models.TextField(_('Disciplinas Lecionadas'), 
        help_text=_('Ex: Matemática, Física, Português. Separe por vírgulas.')
    )
    tarifa_hora = models.DecimalField(_('Tarifa por Hora (R$)'), max_digits=6, decimal_places=2, null=True, blank=True)
    curriculum = models.TextField(_('Conteúdo do Currículo'), blank=True, 
        help_text=_('Experiência profissional relevante, certificações, etc.')
    )
    bio_profissional = models.TextField(_('Bio Profissional'), blank=True, 
        help_text=_('Breve descrição da sua experiência e qualificações como professor.')
    )
    sobre_a_aula = models.TextField(_('Sobre a Aula'), blank=True, 
        help_text=_('Detalhes sobre sua metodologia e formato de aula.')
    )

    # Opções e Status
    is_voluntario = models.BooleanField(_('É Voluntário'), default=False)
    aceita_online = models.BooleanField(_('Aceita Aulas Online'), default=False)
    aceita_grupo = models.BooleanField(_('Aceita Aulas em Grupo'), default=False)
    status_ativo = models.BooleanField(_('Ativamente Aceitando Alunos'), default=True)
    data_validacao = models.DateField(_('Data de Ativação do Perfil'), null=True, blank=True)
    
    # Modalidades (Escolhas)
    modalidades = models.CharField(_('Modalidades de Aula'), max_length=2, choices=MODALIDADE_CHOICES, default='O', blank=True)
    
    # Mídias
    foto_profissional = models.ImageField(_('Foto Profissional'), upload_to='professor_pics/', null=True, blank=True, 
        help_text=_('Uma foto específica para seu perfil profissional, se diferente da foto geral.')
    )

    # Métricas (Calculadas)
    media_avaliacoes = models.DecimalField(_('Média de Avaliações'), max_digits=3, decimal_places=2, default=0.00)

    class Meta:
        verbose_name = _('Perfil de Professor')
        verbose_name_plural = _('Perfis de Professores')

    def __str__(self):
        return f"Perfil de {self.user.get_full_name()}"


# ==============================================================================
# 4. MODELO DE CONTATO: CONTACT PROFESSOR (ADICIONADO)
# ==============================================================================

class ContactProfessor(models.Model):
    # O aluno que enviou a mensagem (pode ser apagado - SET_NULL)
    aluno = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, 
                              related_name='mensagens_enviadas', verbose_name=_('Aluno Remetente'))
    # O professor que recebeu a mensagem (se o professor for apagado, a mensagem se apaga - CASCADE)
    professor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, 
                                  related_name='mensagens_recebidas', verbose_name=_('Professor Destinatário'))
    
    assunto = models.CharField(_('Assunto'), max_length=150)
    mensagem = models.TextField(_('Mensagem'))
    
    lida = models.BooleanField(_('Lida pelo Professor'), default=False)
    data_envio = models.DateTimeField(_('Data de Envio'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('Mensagem de Contato')
        verbose_name_plural = _('Mensagens de Contato')
        ordering = ['-data_envio']

    def __str__(self):
        aluno_str = self.aluno.username if self.aluno else _("Usuário Excluído")
        return f"Mensagem de {aluno_str} para {self.professor.username}"


# ==============================================================================
# 5. SIGNALS (Conectando os modelos)
# ==============================================================================

@receiver(post_save, sender=CustomUser)
def create_professor_profile(sender, instance, created, **kwargs):
    """
    Cria um ProfessorProfile quando um CustomUser é criado E é um professor.
    """
    if instance.is_professor:
        # Tenta pegar o perfil existente
        try:
            profile = instance.professorprofile
        except ProfessorProfile.DoesNotExist:
            profile = None
            
        # Se não existe e deve existir (is_professor=True), cria.
        if not profile:
            ProfessorProfile.objects.create(user=instance)

@receiver(post_save, sender=CustomUser)
def save_professor_profile(sender, instance, **kwargs):
    """
    Salva o ProfessorProfile quando o CustomUser for salvo, se existir.
    """
    if instance.is_professor:
        try:
            instance.professorprofile.save()
        except ProfessorProfile.DoesNotExist:
            # Não faz nada se o perfil ainda não foi criado pelo signal de criação acima.
            pass
