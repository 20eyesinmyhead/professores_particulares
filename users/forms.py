"""
Definição dos Formulários (Forms) para o aplicativo 'users'.

Estes formulários são classes Python que gerenciam a renderização
e, o mais importante, a VALIDAÇÃO dos dados enviados pelo usuário
via HTML, antes que eles sejam processados pelas 'views' ou
salvos no banco de dados.
"""

from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser, ProfessorProfile, ContactProfessor
from django.utils.translation import gettext_lazy as _

# ==============================================================================
# 1. Formulário de Criação de Usuário (Registro)
# ==============================================================================

class CustomUserCreationForm(UserCreationForm):
    """
    Formulário para a criação de um novo 'CustomUser' (registro).
    Herda do 'UserCreationForm' padrão do Django, mas aponta
    para o nosso 'CustomUser' e define os campos específicos.
    """
    
    class Meta(UserCreationForm.Meta):
        # Aponta para o nosso modelo de usuário customizado
        model = CustomUser
        
        # Lista de campos que aparecerão no formulário de registro
        fields = (
            'username', 
            'email', 
            'nome_completo', 
            'como_deseja_ser_chamado',
            'telefone',
            'cpf',
            'cidade',
            'cep',
            'data_nascimento',
            'escolaridade',
            'interesses',
            'historico_aprendizagem',
            'biografia'
        )
    
    def __init__(self, *args, **kwargs):
        """
        Sobrescreve o método __init__ para customizações.
        """
        super().__init__(*args, **kwargs)
        
        # Garante que o email seja obrigatório no formulário (além de no modelo)
        self.fields['email'].required = True
        
        # Altera os widgets (tipo de campo HTML) para melhor usabilidade
        self.fields['data_nascimento'].widget = forms.DateInput(attrs={'type': 'date'})
        
        # Transforma campos de texto simples em 'Textarea' (caixas de texto maiores)
        text_fields = ['escolaridade', 'interesses', 'historico_aprendizagem', 'biografia']
        for field_name in text_fields:
            if field_name in self.fields:
                self.fields[field_name].widget = forms.Textarea(attrs={'rows': 3})

# ==============================================================================
# 2. Formulário de Edição de Usuário (Perfil Básico)
# ==============================================================================

class CustomUserEditForm(UserChangeForm):
    """
    Formulário para a edição do perfil 'CustomUser' pelo próprio usuário.
    
    Este formulário contém uma lógica customizada para o campo 'pausar_conta',
    que é um "campo virtual" para controlar o campo 'is_active' do modelo.
    """
    
    # Remove o formulário de mudança de senha da página de edição de perfil.
    # A mudança de senha é tratada pelo fluxo de 'accounts/' do Django.
    password = None 

    # 1. Campo para ativar o modo Professor
    is_professor = forms.BooleanField(
        label=_("Habilitar o perfil profissional"),
        required=False,
        help_text=_("Marque esta opção para ativar seu perfil de professor.")
    )

    # 2. Campo Virtual: "Pausar Conta"
    # Este campo não existe no banco de dados. Ele é usado para inverter
    # a lógica do campo 'is_active' (que é confuso para o usuário).
    pausar_conta = forms.BooleanField(
        label=_("Pausar minha conta"),
        required=False,
        help_text=_("Se marcado, sua conta será desativada e você não poderá fazer login.")
    )

    class Meta:
        model = CustomUser
        # Lista de campos que o usuário pode editar em seu perfil
        fields = [
            'username', 'nome_completo', 'como_deseja_ser_chamado', 'email', 
            'cpf', 'telefone', 'data_nascimento', 'cidade', 'cep', 
            'foto_perfil', 'escolaridade', 'interesses', 
            'historico_aprendizagem', 'biografia', 
            'is_professor', # Campo de ativação do professor
            'pausar_conta'  # Campo virtual para pausar a conta
        ]
        # Widgets para melhorar a experiência de preenchimento
        widgets = {
            'data_nascimento': forms.DateInput(attrs={'type': 'date'}),
            'biografia': forms.Textarea(attrs={'rows': 3}),
            'historico_aprendizagem': forms.Textarea(attrs={'rows': 3}),
            'escolaridade': forms.Textarea(attrs={'rows': 3}),
            'interesses': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        """
        Inicializa o formulário e define o estado inicial do checkbox 'pausar_conta'.
        """
        super().__init__(*args, **kwargs)
        # Lógica Invertida (Inicial):
        # Se a conta está INATIVA (is_active=False),
        # o checkbox "Pausar" deve vir MARCADO (initial=True).
        self.fields['pausar_conta'].initial = not self.instance.is_active

    def clean_pausar_conta(self):
        """
        Processa o valor do campo virtual 'pausar_conta' durante a validação.
        """
        # Lógica Invertida (Clean):
        # Pega o valor do checkbox (True se marcado, False se desmarcado)
        pausar = self.cleaned_data.get('pausar_conta')
        # Retorna o valor OPOSTO, que é o valor que 'is_active' deve ter.
        # Se 'pausar' = True, 'is_active' deve ser False.
        return not pausar 

    def save(self, commit=True):
        """
        Salva o formulário, aplicando o valor limpo de 'pausar_conta'
        ao campo 'is_active' da instância.
        """
        # Lógica Invertida (Save):
        # O 'cleaned_data' de 'pausar_conta' já contém o valor invertido (graças ao clean)
        # que é o valor correto para 'is_active'.
        self.instance.is_active = self.cleaned_data.get('pausar_conta', self.instance.is_active)
        return super().save(commit)

# ==============================================================================
# 3. Formulário de Perfil de Professor
# ==============================================================================

class ProfessorProfileForm(forms.ModelForm):
    """
    Formulário para editar os dados específicos do 'ProfessorProfile'.
    Este formulário aparece na página 'editar_perfil' junto com o 'CustomUserEditForm'.
    """
    class Meta:
        model = ProfessorProfile
        # Exclui campos que são gerenciados automaticamente pelo sistema
        # 'user' é vinculado pela view/signal.
        # 'media_avaliacoes' é calculada (futuramente).
        # 'data_validacao' é definida pelo admin (futuramente).
        exclude = ('user', 'media_avaliacoes', 'data_validacao')
        
        # Widgets para melhorar a aparência de campos de texto
        widgets = {
            'disciplinas': forms.Textarea(attrs={'rows': 2}),
            'curriculum': forms.Textarea(attrs={'rows': 4}),
            'bio_profissional': forms.Textarea(attrs={'rows': 3}),
            'sobre_a_aula': forms.Textarea(attrs={'rows': 3}),
        }
        
        # Textos de ajuda para campos específicos
        help_texts = {
            'tarifa_hora': _("Deixe 0.00 ou em branco se for apenas Voluntário."),
        }

# ==============================================================================
# 4. Formulário de Contato com o Professor
# ==============================================================================

class ContactProfessorForm(forms.ModelForm):
    """
    Formulário usado por alunos (usuários logados) para enviar
    uma mensagem de contato para um professor.
    """
    
    # Campo extra que não está no modelo 'ContactProfessor'.
    # Usado para que o aluno confirme o e-mail de resposta (usado no 'reply_to' da view).
    confirmar_email = forms.EmailField(
        label=_('Seu E-mail para Contato'),
        help_text=_("O professor usará este e-mail para responder a você."),
        required=True
    )
    
    # Campos do formulário que vêm do modelo
    class Meta:
        model = ContactProfessor
        # A view preenche 'aluno' e 'professor' automaticamente.
        # O usuário só precisa preencher 'assunto' e 'mensagem'.
        fields = ('assunto', 'mensagem')
        widgets = {
            'mensagem': forms.Textarea(attrs={'rows': 5}),
        }

    def __init__(self, *args, **kwargs):
        """
        Sobrescreve o __init__ para lidar com o argumento 'user'
        passado pela 'contato_professor' (view).
        """
        # 1. Captura e remove o argumento 'user'
        #    A view passa 'user=request.user', mas o ModelForm padrão
        #    não espera esse argumento, o que causava um Erro 500.
        #    'kwargs.pop()' remove 'user' do dicionário antes de
        #    passá-lo para a classe pai.
        self.user = kwargs.pop('user', None)
        
        # 2. Chama o __init__ pai (agora sem o argumento 'user' inesperado)
        super().__init__(*args, **kwargs)
        
        # 3. Lógica para pré-preencher o e-mail
        #    (Se a view passou 'initial={'confirmar_email': ...}')
        if 'initial' in kwargs and 'confirmar_email' in kwargs['initial']:
                self.fields['confirmar_email'].initial = kwargs['initial']['confirmar_email']