# Importações essenciais
from django.shortcuts import render, redirect, get_object_or_404
# Corrigido: Importar login e logout explicitamente
from django.contrib.auth import login, logout, authenticate, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm 
from django.db.models import Q
from django.http import Http404, HttpResponseForbidden
from django.contrib import messages
from django.db import transaction 
from django.core.mail import send_mail, EmailMessage 
from django.template.loader import render_to_string 
from django.conf import settings 

# ADICIONADO: Importações para lógica anti-spam (timedelta e timezone)
from datetime import timedelta
from django.utils import timezone

# Importa o Modelo de Usuário configurado no settings.py
CustomUser = get_user_model() 

# Importação dos Models e Forms locais.
from .models import ProfessorProfile, ContactProfessor 
from .forms import (
    CustomUserCreationForm, 
    CustomUserEditForm, 
    ProfessorProfileForm, 
    ContactProfessorForm
)


# ==============================================================================
# 1. AUTENTICAÇÃO E REGISTRO
# ==============================================================================

def registro(request):
    """
    View de registro unificada que cria um CustomUser.
    """
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, request.FILES) # Adicionado request.FILES para foto
        if form.is_valid():
            with transaction.atomic():
                user = form.save(commit=False)
                # Garante que o usuário seja criado como NÃO professor inicialmente
                user.is_professor = False
                user.save()

                messages.success(request, f'Conta para {user.username} criada com sucesso! Você já pode fazer login.')
                return redirect('login')
        else:
            # Captura de erros de validação
            error_list = []
            for field, errors in form.errors.items():
                for error in errors:
                    if 'email' in field and 'já existe' in error:
                        error_list.append('Este e-mail já está cadastrado.')
                    elif 'username' in field and 'já existe' in error:
                        error_list.append('Este nome de usuário já está em uso.')
                    else:
                        error_list.append(f"{field}: {error}")
            
            unique_errors = sorted(list(set(error_list)))
            for err in unique_errors:
                messages.error(request, err)
            
    else:
        form = CustomUserCreationForm()

    return render(request, 'users/registro.html', {'form': form})

# ==============================================================================
# 2. EDIÇÃO E VISUALIZAÇÃO DE PERFIL
# ==============================================================================

@login_required
def editar_perfil(request):
    """
    View unificada para editar CustomUser e ProfessorProfile (se aplicável).
    """
    user = request.user
    
    # Tenta obter o perfil (pode ser None se 'is_professor' for False)
    try:
        professor_profile = user.professorprofile
    except ProfessorProfile.DoesNotExist:
        professor_profile = None

    if request.method == 'POST':
        user_form = CustomUserEditForm(request.POST, request.FILES, instance=user)
        
        profile_form = None
        # Instancia o profile_form apenas se o perfil já existia
        if professor_profile:
            profile_form = ProfessorProfileForm(request.POST, request.FILES, instance=professor_profile)

        # Valida o formulário principal do usuário
        if user_form.is_valid():
            try:
                # Inicia o bloco de transação
                with transaction.atomic():
                    updated_user = user_form.save() # Salva o CustomUser (is_professor é atualizado)

                    created_profile_now = False # Flag para saber se o perfil foi criado NESTA requisição
                    
                    # --- LÓGICA DE PERFIL PROFESSOR PÓS-SAVE ---
                    
                    # Caso 1: O usuário MARCOU 'is_professor' (ou já era professor)
                    if updated_user.is_professor:
                        
                        # Garante que o perfil exista (cria se for a primeira vez)
                        professor_profile, created_profile_now = ProfessorProfile.objects.get_or_create(user=updated_user)
                        
                        # Se o perfil foi recém-criado, o 'profile_form' anterior era None
                        # Precisamos instanciá-lo agora com os dados do POST
                        if created_profile_now:
                            profile_form = ProfessorProfileForm(request.POST, request.FILES, instance=professor_profile)
                        
                        # Validamos o formulário de professor (seja ele novo ou existente)
                        if profile_form and profile_form.is_valid():
                            profile_form.save()
                            
                            # Lógica de REATIVAÇÃO
                            if not professor_profile.status_ativo:
                                professor_profile.status_ativo = True
                                professor_profile.save(update_fields=['status_ativo'])
                            
                            if created_profile_now:
                                messages.info(request, 'Perfil de professor ativado! Preencha seus dados profissionais.')
                        
                        elif profile_form and not profile_form.is_valid():
                            # Se o user_form era válido mas o profile_form (recém-criado ou existente) não era
                            messages.error(request, 'Erro ao salvar o perfil profissional. Verifique os campos.')
                            raise transaction.Rollback # Força o rollback (desfaz o user_form.save())
                        
                    # Caso 2: O usuário DESMARCOU 'is_professor'
                    elif not updated_user.is_professor and professor_profile:
                        professor_profile.status_ativo = False # Desativa (não aparece na lista)
                        professor_profile.save(update_fields=['status_ativo'])
                        messages.info(request, 'Seu perfil de professor foi desativado.')

                # Se a transação foi bem-sucedida (não houve Rollback)
                messages.success(request, 'Seu perfil foi atualizado com sucesso!')
                return redirect('users:perfil_detalhe', username=user.username)
            
            except transaction.Rollback:
                # Se o rollback foi forçado (erro no profile_form),
                # A view continua para renderizar os formulários com erros.
                pass 

        else: # Se user_form não for válido
            messages.error(request, 'Erro ao salvar o perfil geral. Verifique os campos.')
        
        # Se a validação falhou (POST), renderiza os formulários com os erros
        context = {
            'user_form': user_form,
            'professor_form': profile_form, # Será None ou o formulário inválido
            'is_professor': user_form.cleaned_data.get('is_professor', user.is_professor),
        }
        return render(request, 'users/editar_perfil.html', context)

    
    # Lógica do GET request (quando a página é carregada)
    user_form = CustomUserEditForm(instance=user)
    if professor_profile:
        profile_form = ProfessorProfileForm(instance=professor_profile)
    else:
        profile_form = None

    context = {
        'user_form': user_form,
        'professor_form': profile_form,
        'is_professor': user.is_professor,
    }
    return render(request, 'users/editar_perfil.html', context)


def perfil_detalhe(request, username):
    """
    Exibe o perfil detalhado de qualquer usuário (CustomUser).
    """
    user_perfil = get_object_or_404(CustomUser, username=username)
    perfil_extensao = None
    tipo_perfil = 'aluno'

    if user_perfil.is_professor:
        try:
            perfil_extensao = user_perfil.professorprofile
            tipo_perfil = 'professor'
        except ProfessorProfile.DoesNotExist:
            pass

    context = {
        'user_perfil': user_perfil,
        'perfil_extensao': perfil_extensao,
        'tipo_perfil': tipo_perfil,
    }
    return render(request, 'users/perfil_detalhe.html', context)


# ==============================================================================
# 3. LISTAGEM E BUSCA DE PROFESSORES
# ==============================================================================

def lista_professores(request, somente_voluntarios=False):
    """
    Lista todos os professores ativos, com opção de filtrar por voluntários.
    """
    professores_base = CustomUser.objects.filter(is_professor=True)
    
    ativos_pks = ProfessorProfile.objects.filter(status_ativo=True).values_list('user_id', flat=True)
    professores = professores_base.filter(pk__in=ativos_pks).select_related('professorprofile')

    titulo = "Encontre a Pessoa Certa!"
    if somente_voluntarios:
        voluntarios_pks = ProfessorProfile.objects.filter(is_voluntario=True).values_list('user_id', flat=True)
        professores = professores.filter(pk__in=voluntarios_pks)
        titulo = "Professores Voluntários (Aulas Gratuitas)"

    query = request.GET.get('q')
    if query:
        professores = professores.filter(
            Q(username__icontains=query) |
            Q(nome_completo__icontains=query) |
            Q(professorprofile__disciplinas__icontains=query) |
            Q(cidade__icontains=query)
        ).distinct()

    context = {
        'professores': professores.order_by('username'),
        'titulo': titulo,
        'somente_voluntarios': somente_voluntarios
    }
    return render(request, 'users/lista_professores.html', context)


# ==============================================================================
# 4. FUNCIONALIDADE DE CONTATO (COM LÓGICA ANTI-SPAM)
# ==============================================================================

@login_required
def contato_professor(request, professor_pk):
    """
    Permite a um usuário logado (aluno) enviar uma mensagem para um professor.
    """
    professor = get_object_or_404(CustomUser, pk=professor_pk, is_professor=True)

    if request.user == professor:
        messages.warning(request, "Você não pode enviar uma mensagem de contato para si mesmo.")
        return redirect('users:perfil_detalhe', username=professor.username)

    # --- LÓGICA ANTI-SPAM ---
    limite_tempo = timezone.now() - timedelta(hours=1)
    contagem_recente = ContactProfessor.objects.filter(
        aluno=request.user,
        professor=professor,
        data_envio__gte=limite_tempo
    ).count()
    LIMITE_MENSAGENS = 3
    if contagem_recente >= LIMITE_MENSAGENS:
        messages.error(request, "Você enviou muitas mensagens recentemente para este professor. Tente novamente em uma hora.")
        return redirect('users:perfil_detalhe', username=professor.username)
    # --- FIM DA LÓGICA ANTI-SPAM ---
        
    aluno_email = request.user.email

    if request.method == 'POST':
        form = ContactProfessorForm(request.POST)

        if form.is_valid():
            with transaction.atomic():
                contato = form.save(commit=False)
                contato.aluno = request.user
                contato.professor = professor
                contato.save()

                email_confirmado_pelo_aluno = form.cleaned_data.get('confirmar_email')

                try:
                    # Renderiza o corpo do email a partir do template HTML
                    html_message = render_to_string('emails/notificacao_professor.html', {
                        'professor_nome': professor.como_deseja_ser_chamado or professor.username,
                        'aluno_nome': request.user.como_deseja_ser_chamado or request.user.username,
                        'assunto_mensagem': contato.assunto,
                        'mensagem_detalhada': contato.mensagem,
                        'aluno_email': email_confirmado_pelo_aluno,
                        'link_perfil_aluno': request.build_absolute_uri(
                            redirect('users:perfil_detalhe', username=request.user.username).url
                        )
                    })

                    # Cria o objeto EmailMessage para enviar HTML
                    email_msg = EmailMessage(
                        subject=f"Novo Interesse de Aula: {contato.assunto}",
                        body=f"Você recebeu uma nova mensagem de {request.user.username}. Veja os detalhes no email HTML.",
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        to=[professor.email],
                        reply_to=[email_confirmado_pelo_aluno],
                    )
                    email_msg.content_subtype = "html"
                    email_msg.body = html_message
                    email_msg.send(fail_silently=False)

                    messages.success(request, f"Sua mensagem foi enviada para {professor.como_deseja_ser_chamado or professor.username}!")

                    # Opcional: Enviar cópia para o Aluno
                    try:
                        send_mail(
                            subject=f"Cópia: Seu contato com {professor.como_deseja_ser_chamado or professor.username}",
                            message=f"Sua mensagem:\n\n{contato.mensagem}", 
                            from_email=settings.DEFAULT_FROM_EMAIL,
                            recipient_list=[email_confirmado_pelo_aluno],
                            fail_silently=True,
                        )
                    except Exception:
                        pass 

                except Exception as e:
                    messages.warning(request, f"Sua mensagem foi salva, mas ocorreu um erro ao enviar o e-mail: {e}. Por favor, verifique as configurações de EMAIL no settings.py.")

            return redirect('users:perfil_detalhe', username=professor.username)
        else:
            messages.error(request, "Erro ao enviar a mensagem. Verifique os campos do formulário.")

    else: # GET request
        form = ContactProfessorForm(initial={'confirmar_email': aluno_email})

    context = {
        'professor': professor,
        'form': form,
    }
    return render(request, 'users/contato_professor.html', context)


# ==============================================================================
# 5. ZONA DE PERIGO (EXCLUSÃO DE CONTA)
# ==============================================================================

@login_required
def excluir_conta(request):
    """
    Processa a exclusão permanente da conta do usuário.
    """
    if request.method == 'POST':
        # Pega o usuário logado
        user = request.user
        
        # Faz o logout ANTES de deletar para invalidar a sessão
        logout(request)
        
        # Deleta o usuário do banco de dados
        user.delete()
        
        # Envia uma mensagem de sucesso (será exibida na próxima página)
        messages.success(request, 'Sua conta foi excluída permanentemente.')
        
        # CORREÇÃO: Redireciona para o nome da rota da lista de professores,
        # que é a nossa página inicial.
        return redirect('users:lista_professores')

    # Se for um GET (primeira vez que o usuário visita a página),
    # apenas mostra o template de confirmação.
    return render(request, 'users/excluir_conta.html')

