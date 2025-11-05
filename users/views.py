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
# 0. PÁGINAS ESTÁTICAS (Sobre Nós)
# ==============================================================================

def sobre_nos(request):
    """
    Renderiza a página 'Sobre Nós'.
    """
    return render(request, 'users/sobre_nos.html')


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

# ... (suas importações e outras views) ...

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
        
        # Sempre instancia o profile_form se o usuário é ou pretende ser professor
        # Isso garante que ele esteja disponível para validação mesmo se recém-criado
        profile_form = ProfessorProfileForm(request.POST, request.FILES, instance=professor_profile) if user.is_professor or 'is_professor' in request.POST else None

        if user_form.is_valid():
            try:
                with transaction.atomic():
                    updated_user = user_form.save() # Salva o CustomUser (is_professor é atualizado)

                    created_profile_now = False
                    
                    if updated_user.is_professor:
                        # Garante que o perfil exista (cria se for a primeira vez)
                        professor_profile, created_profile_now = ProfessorProfile.objects.get_or_create(user=updated_user)
                        
                        # Se o perfil foi recém-criado ou já existia, agora temos que garantir que
                        # o profile_form está instanciado com a instância correta
                        if not profile_form: # Se não foi instanciado antes (e o user agora é professor)
                            profile_form = ProfessorProfileForm(request.POST, request.FILES, instance=professor_profile)
                        else: # Se já existia, atualiza a instância para garantir que estamos usando o objeto salvo ou recém-criado
                            profile_form.instance = professor_profile 
                        
                        if profile_form.is_valid():
                            profile_form.save()
                            
                            # Lógica de REATIVAÇÃO
                            if not professor_profile.status_ativo:
                                professor_profile.status_ativo = True
                                professor_profile.save(update_fields=['status_ativo'])
                            
                            if created_profile_now:
                                messages.info(request, 'Perfil de professor ativado! Preencha seus dados profissionais.')
                        
                        else: # Se o profile_form não for válido
                            messages.error(request, 'Erro ao salvar o perfil profissional. Verifique os campos.')
                            # Não precisa de raise transaction.Rollback aqui, pois se não houver redirect,
                            # a view irá renderizar o template com os erros no final do bloco POST.
                            # Se quisermos forçar o rollback e parar tudo, poderíamos, mas a renderização
                            # com os erros do profile_form é mais amigável.
                    
                    elif not updated_user.is_professor and professor_profile:
                        # Se o usuário desmarcou is_professor e já tinha um perfil
                        professor_profile.status_ativo = False # Desativa (não aparece na lista)
                        professor_profile.save(update_fields=['status_ativo'])
                        messages.info(request, 'Seu perfil de professor foi desativado.')

                messages.success(request, 'Seu perfil foi atualizado com sucesso!')
                return redirect('users:perfil_detalhe', username=user.username)
            
            except Exception as e: # Captura qualquer exceção dentro da transação
                messages.error(request, f"Ocorreu um erro inesperado ao salvar: {e}")
                # A transação será revertida automaticamente se houver uma exceção não tratada aqui.
                # Não precisamos de um `pass` vazio que leva a um `return None`.

        else: # Se user_form não for válido
            messages.error(request, 'Erro ao salvar o perfil geral. Verifique os campos.')
        
        # Este bloco de renderização agora é o fallback para qualquer falha de validação ou erro na transação
        # dentro do método POST, garantindo que SEMPRE haja um HttpResponse.
        context = {
            'user_form': user_form,
            'professor_form': profile_form,
            'is_professor': user_form.cleaned_data.get('is_professor', user.is_professor if user_form.is_valid() else False),
        }
        return render(request, 'users/editar_perfil.html', context)
    
    else: # GET request (quando a página é carregada)
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


# ADICIONADO: Nova view para "Minhas Mensagens"
@login_required
def minhas_mensagens(request):
    """
    Exibe todas as mensagens enviadas E recebidas pelo usuário logado.
    """
    user = request.user
    
    # Filtra mensagens onde o usuário é o remetente (aluno) OU o destinatário (professor)
    # O .select_related() otimiza a consulta, buscando os dados do aluno e professor
    # na mesma query.
    mensagens = ContactProfessor.objects.filter(
        Q(aluno=user) | Q(professor=user)
    ).select_related('aluno', 'professor')
    
    # A ordenação (ordering = ['-data_envio']) já está definida no Meta do modelo ContactProfessor.

    context = {
        'mensagens': mensagens
    }
    return render(request, 'users/minhas_mensagens.html', context)


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
        form = ContactProfessorForm(request.POST, user=request.user) # Passa o usuário para o form

        if form.is_valid():
            with transaction.atomic():
                contato = form.save(commit=False)
                contato.aluno = request.user
                contato.professor = professor
                contato.save()

                email_confirmado_pelo_aluno = form.cleaned_data.get('confirmar_email')

                # -----------------------------------------------------------------
                # Captura os novos campos (telefone e whatsapp)
                # -----------------------------------------------------------------
                incluir_telefone = form.cleaned_data.get('incluir_telefone')
                is_whatsapp = form.cleaned_data.get('is_whatsapp')
                
                aluno_telefone = None
                if incluir_telefone and request.user.telefone:
                    aluno_telefone = request.user.telefone
                # -----------------------------------------------------------------

                try:
                    # Renderiza o corpo do email a partir do template HTML
                    html_message = render_to_string('emails/notificacao_professor.html', {
                        'professor_nome': professor.como_deseja_ser_chamado or professor.username,
                        'aluno_nome': request.user.como_deseja_ser_chamado or request.user.username,
                        'assunto_mensagem': contato.assunto,
                        'mensagem_detalhada': contato.mensagem,
                        'aluno_email': email_confirmado_pelo_aluno,
                        
                        # Passa as novas variáveis para o template de e-mail
                        'aluno_telefone': aluno_telefone, # (Pode ser None)
                        'is_whatsapp': is_whatsapp, # (True/False)
                        
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
        form = ContactProfessorForm(initial={'confirmar_email': aluno_email}, user=request.user) # Passa o usuário

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
        
        # Redireciona para a nova página Home
        return redirect('users:lista_professores')

    # Se for um GET (primeira vez que o usuário visita a página),
    # apenas mostra o template de confirmação.
    return render(request, 'users/excluir_conta.html')