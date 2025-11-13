from django import forms
# Importamos o UserCreationForm e UserChangeForm do Django
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
# Importamos os novos modelos
from .models import CustomUser, ProfessorProfile, ContactProfessor
from django.utils.translation import gettext_lazy as _

# ==============================================================================
# 1. Formulário de Criação de Usuário (Registro)
# ==============================================================================
class CustomUserCreationForm(UserCreationForm):
    """
    Formulário para a criação de um novo CustomUser.
    (Simplificado para não incluir 'is_professor' no registro inicial)
    """
    
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        # Campos que o formulário de criação irá exibir
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
        super().__init__(*args, **kwargs)
        self.fields['email'].required = True
        
        # Widgets para campos de data e texto longo
        self.fields['data_nascimento'].widget = forms.DateInput(attrs={'type': 'date'})
        
        text_fields = ['escolaridade', 'interesses', 'historico_aprendizagem', 'biografia']
        for field_name in text_fields:
            if field_name in self.fields:
                self.fields[field_name].widget = forms.Textarea(attrs={'rows': 3})

# ==============================================================================
# 2. Formulário de Edição de Usuário (Perfil Básico)
# ==============================================================================
class CustomUserEditForm(UserChangeForm):
    """
    Formulário para edição dos dados básicos do CustomUser.
    """
    
    # Removendo o campo de senha da edição de perfil
    password = None 

    # 1. Sobrescrevendo o label de 'is_professor'
    is_professor = forms.BooleanField(
        label=_("Habilitar o perfil profissional"),
        required=False,
        help_text=_("Marque esta opção para ativar seu perfil de professor e poder cadastrar suas aulas.")
    )

    # 2. Sobrescrevendo 'is_active' para "Pausar Conta"
    #    Para "Pausar Conta", o usuário deve MARCAR o checkbox (is_active=False).
    #    Invertemos a lógica na view ou no clean_ method.
    pausar_conta = forms.BooleanField(
        label=_("Pausar minha conta"),
        required=False,
        help_text=_("Se marcado, sua conta será desativada e você não poderá fazer login.")
    )

    class Meta:
        model = CustomUser
        fields = [
            'username', 'nome_completo', 'como_deseja_ser_chamado', 'email', 
            'cpf', 'telefone', 'data_nascimento', 'cidade', 'cep', 
            'foto_perfil', 'escolaridade', 'interesses', 
            'historico_aprendizagem', 'biografia', 
            'is_professor', # 1. Campo com label alterado
            'pausar_conta'  # 2. Campo novo (virtual)
        ]
        widgets = {
            'data_nascimento': forms.DateInput(attrs={'type': 'date'}),
            'biografia': forms.Textarea(attrs={'rows': 3}),
            'historico_aprendizagem': forms.Textarea(attrs={'rows': 3}),
            'escolaridade': forms.Textarea(attrs={'rows': 3}),
            'interesses': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Define o valor inicial de 'pausar_conta' baseado no inverso de 'is_active'
        # Se a conta está INATIVA (is_active=False), o checkbox "Pausar" deve vir MARCADO (True)
        self.fields['pausar_conta'].initial = not self.instance.is_active

    def clean_pausar_conta(self):
        # Converte a lógica: Se "Pausar Conta" (pausar_conta) for True, 'is_active' deve ser False.
        pausar = self.cleaned_data.get('pausar_conta')
        return not pausar # Retorna o valor que será salvo em 'is_active'

    def save(self, commit=True):
        # Mapeia o valor limpo de 'pausar_conta' (que já é o valor de 'is_active') para a instância
        self.instance.is_active = self.cleaned_data.get('pausar_conta', self.instance.is_active)
        return super().save(commit)

# ==============================================================================
# 3. Formulário de Perfil de Professor
# ==============================================================================
class ProfessorProfileForm(forms.ModelForm):
    class Meta:
        model = ProfessorProfile
        # Exclui campos gerenciados pelo sistema
        exclude = ('user', 'media_avaliacoes', 'data_validacao')
        widgets = {
            'disciplinas': forms.Textarea(attrs={'rows': 2}),
            'curriculum': forms.Textarea(attrs={'rows': 4}),
            'bio_profissional': forms.Textarea(attrs={'rows': 3}),
            'sobre_a_aula': forms.Textarea(attrs={'rows': 3}),
        }
        help_texts = {
            'tarifa_hora': _("Deixe 0.00 ou em branco se for apenas Voluntário."),
        }

# ==============================================================================
# 4. Formulário de Contato com o Professor (*** CÓDIGO CORRIGIDO ***)
# ==============================================================================
class ContactProfessorForm(forms.ModelForm):
    """
    Formulário usado por alunos para contatar professores.
    """
    confirmar_email = forms.EmailField(
        label=_('Seu E-mail para Contato'),
        help_text=_("O professor usará este e-mail para responder a você."),
        required=True
    )
    
    class Meta:
        model = ContactProfessor
        # A view preenche 'aluno' e 'professor'.
        fields = ('assunto', 'mensagem')
        widgets = {
            'mensagem': forms.Textarea(attrs={'rows': 5}),
        }

    def __init__(self, *args, **kwargs):
        # 1. CAPTURA O 'user' ANTES DE CHAMAR O SUPER()
        #    Sua view estava passando 'user=request.user', mas o __init__
        #    não estava esperando por isso, causando o Erro 500 (TypeError).
        #    kwargs.pop() remove o argumento 'user' para evitar o erro.
        self.user = kwargs.pop('user', None)
        
        # 2. CHAMA O __init__ PAI (agora sem o 'user' inesperado)
        super().__init__(*args, **kwargs)
        
        # 3. LÓGICA ORIGINAL PARA PRÉ-PREENCHER O E-MAIL
        #    Pré-preenche o e-mail de confirmação se for passado
        if 'initial' in kwargs and 'confirmar_email' in kwargs['initial']:
                self.fields['confirmar_email'].initial = kwargs['initial']['confirmar_email']