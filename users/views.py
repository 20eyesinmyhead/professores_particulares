"""
Definição das Views (Lógica de Negócios) para o aplicativo 'users'.

Este arquivo recebe requisições web (ex: cliques em botões) e decide o que
fazer: renderizar uma página HTML, processar um formulário, salvar dados
no banco de dados ou enviar um e-mail.
"""

# --- Importações Essenciais ---

# Funções do Django para renderizar páginas, redirecionar e buscar objetos
from django.shortcuts import render, redirect, get_object_or_404
# Funções de autenticação (login, logout) e para obter o modelo de usuário
from django.contrib.auth import login, logout, authenticate, get_user_model
# Decorador para proteger páginas que exigem login
from django.contrib.auth.decorators import login_required
# Formulário de login padrão
from django.contrib.auth.forms import AuthenticationForm 
# Para consultas complexas no banco (ex: "OU")
from django.db.models import Q
# Para exibir mensagens de feedback (sucesso, erro, aviso)
from django.contrib import messages
# Para garantir que operações de banco de dados sejam seguras (ou tudo ou nada)
from django.db import transaction 
# Funções para construir e enviar e-mails
from django.core.mail import send_mail, EmailMessage 
# Para carregar templates de e-mail em HTML
from django.template.loader import render_to_string 
# Para acessar o 'settings.py' (ex: chaves de API, DEBUG)
from django.conf import settings 
# Para lógica de tempo (ex: anti-spam)
from datetime import timedelta
from django.utils import timezone

# --- Importações Locais (do próprio app) ---

# Obtém o modelo de usuário ('CustomUser') definido no 'settings.py'
CustomUser = get_user_model() 

# Importa os modelos (tabelas) e formulários deste aplicativo
from .models import ProfessorProfile, ContactProfessor 
from .forms import (
    CustomUserCreationForm, 
    CustomUserEditForm, 
    ProfessorProfileForm, 
    ContactProfessorForm
)


# ==============================================================================
# 0. PÁGINAS ESTÁTICAS
# ==============================================================================

def sobre_nos(request):
    """
    Renderiza a página estática 'Sobre Nós'.
    """
    return render(request, 'users/sobre_nos.html')


# ==============================================================================
# 1. AUTENTICAÇÃO E REGISTRO
# ==============================================================================

def registro(request):
    """
    View de registro: lida com a criação de novas contas de usuário.
    
    - Se GET: Mostra um formulário de registro em branco.
    - Se POST: Processa os dados do formulário, cria o usuário e redireciona para login.
    """
    if request.method == 'POST':
        # Instancia o formulário com os dados enviados (POST) e arquivos (FILES, ex: foto)
        form = CustomUserCreationForm(request.POST, request.FILES)
        
        if form.is_valid():
            # 'transaction.atomic' garante que a operação só é concluída se
            # todas as etapas (ex: criar usuário, criar perfil) funcionarem.
            with transaction.atomic():
                user = form.save(commit=False)
                # Garante que todo novo usuário começa como um aluno
                user.is_professor = False
                user.save()

            messages.success(request, f'Conta para {user.username} criada com sucesso! Você já pode fazer login.')
            # Redireciona para a URL com o nome 'login' (definida em urls.py)
            return redirect('login')
        else:
            # Se o formulário for inválido, coleta os erros para exibir
            error_list = []
            for field, errors in form.errors.items():
                for error in errors:
                    # Formata erros comuns para serem mais amigáveis
                    if 'email' in field and 'já existe' in error:
                        error_list.append('Este e-mail já está cadastrado.')
                    elif 'username' in field and 'já existe' in error:
                        error_list.append('Este nome de usuário já está em uso.')
                    else:
                        error_list.append(f"{field}: {error}")
            
            # Exibe cada erro único como uma mensagem
            unique_errors = sorted(list(set(error_list)))
            for err in unique_errors:
                messages.error(request, err)
            
    else: # Se for uma requisição GET
        form = CustomUserCreationForm()

    # Renderiza o template de registro, passando o formulário (novo ou com erros)
    return render(request, 'users/registro.html', {'form': form})

# Nota: As views de login e logout são tratadas pelo 'django.contrib.auth.urls'
# no 'core/urls.py', por isso não precisam ser escritas aqui.

# ==============================================================================
# 2. EDIÇÃO E VISUALIZAÇÃO DE PERFIL
# ==============================================================================

@login_required # Protege a página: só usuários logados podem editar
def editar_perfil(request):
    """
    View unificada para editar o perfil do usuário (CustomUser) e o
    perfil de professor (ProfessorProfile) ao mesmo tempo.
    """
    user = request.user
    
    # Tenta buscar o perfil de professor vinculado a este usuário
    try:
        professor_profile = user.professorprofile
    except ProfessorProfile.DoesNotExist:
        professor_profile = None # O usuário é um aluno ou ainda não ativou o perfil

    if request.method == 'POST':
        # Popula os formulários com os dados enviados
        user_form = CustomUserEditForm(request.POST, request.FILES, instance=user)
        
        # O formulário de professor só é instanciado se o usuário já for professor
        # ou se ele estiver tentando se tornar um (marcando o checkbox)
        if user.is_professor or 'is_professor' in request.POST:
            profile_form = ProfessorProfileForm(request.POST, request.FILES, instance=professor_profile)
        else:
            profile_form = None

        # Validação: O formulário principal (user_form) deve ser válido
        if user_form.is_valid():
            try:
                with transaction.atomic():
                    # 1. Salva o CustomUser (isso atualiza o campo 'is_professor')
                    updated_user = user_form.save()
                    
                    # 2. Lógica para o Perfil de Professor
                    if updated_user.is_professor:
                        # 2a. Se o usuário marcou "É Professor":
                        # Garante que o perfil exista (cria se for a primeira vez)
                        # O 'signal' no models.py também faz isso, mas é bom garantir aqui.
                        professor_profile, created = ProfessorProfile.objects.get_or_create(user=updated_user)
                        
                        # Re-instancia o formulário de perfil para garantir que estamos
                        # salvando a instância correta (a que acabamos de criar/buscar)
                        if profile_form is None:
                             profile_form = ProfessorProfileForm(request.POST, request.FILES, instance=professor_profile)
                        else:
                             profile_form.instance = professor_profile

                        if profile_form.is_valid():
                            profile_form.save()
                            # Se o perfil estava inativo, reativa
                            if not professor_profile.status_ativo:
                                professor_profile.status_ativo = True
                                professor_profile.save(update_fields=['status_ativo'])
                            
                            if created:
                                messages.info(request, 'Perfil de professor ativado! Preencha seus dados profissionais.')
                        else:
                            # Se o formulário de perfil tiver erros, avisa o usuário
                            messages.error(request, 'Erro ao salvar o perfil profissional. Verifique os campos.')

                    elif not updated_user.is_professor and professor_profile:
                        # 2b. Se o usuário desmarcou "É Professor":
                        # Desativa o perfil (não o exclui, para manter o histórico)
                        professor_profile.status_ativo = False
                        professor_profile.save(update_fields=['status_ativo'])
                        messages.info(request, 'Seu perfil de professor foi desativado.')

                messages.success(request, 'Seu perfil foi atualizado com sucesso!')
                return redirect('users:perfil_detalhe', username=user.username)
            
            except Exception as e: # Captura qualquer erro inesperado durante a transação
                messages.error(request, f"Ocorreu um erro inesperado ao salvar: {e}")

        else: # Se o user_form não for válido
            messages.error(request, 'Erro ao salvar o perfil geral. Verifique os campos.')
            
    else: # Se for uma requisição GET (primeira vez que carrega a página)
        # Popula os formulários com os dados existentes do banco
        user_form = CustomUserEditForm(instance=user)
        if professor_profile:
            profile_form = ProfessorProfileForm(instance=professor_profile)
        else:
            profile_form = None

    # Contexto para renderizar o template
    context = {
        'user_form': user_form,
        'professor_form': profile_form,
        'is_professor': user.is_professor,
    }
    return render(request, 'users/editar_perfil.html', context)


def perfil_detalhe(request, username):
    """
    Exibe a página de perfil pública de um usuário (aluno ou professor).
    Esta view é somente leitura.
    """
    # Busca o usuário pelo 'username' na URL, ou retorna Erro 404
    user_perfil = get_object_or_404(CustomUser, username=username)
    perfil_extensao = None
    tipo_perfil = 'aluno' # Assume que é aluno por padrão

    # Se o usuário for um professor, busca seu perfil de extensão
    if user_perfil.is_professor:
        try:
            perfil_extensao = user_perfil.professorprofile
            tipo_perfil = 'professor'
        except ProfessorProfile.DoesNotExist:
            # Caso raro: 'is_professor' é True, mas o perfil não foi criado
            pass 

    context = {
        'user_perfil': user_perfil,       # O objeto CustomUser
        'perfil_extensao': perfil_extensao, # O objeto ProfessorProfile (ou None)
        'tipo_perfil': tipo_perfil,       # String 'aluno' ou 'professor'
    }
    return render(request, 'users/perfil_detalhe.html', context)


@login_required
def minhas_mensagens(request):
    """
    Exibe uma lista de todas as mensagens enviadas E recebidas
    pelo usuário logado.
    """
    user = request.user
    
    # Usa Q object para buscar mensagens ONDE o usuário é o remetente (aluno)
    # OU o destinatário (professor).
    mensagens = ContactProfessor.objects.filter(
        Q(aluno=user) | Q(professor=user)
    ).select_related('aluno', 'professor') # Otimiza a query
    
    # A ordenação (da mais nova para a mais antiga) é definida no models.py
    
    context = {
        'mensagens': mensagens
    }
    return render(request, 'users/minhas_mensagens.html', context)


# ==============================================================================
# 3. LISTAGEM E BUSCA DE PROFESSORES
# ==============================================================================

def lista_professores(request, somente_voluntarios=False):
    """
    Página principal que lista todos os professores ativos.
    Inclui funcionalidade de busca e filtro para voluntários.
    """
    # Começa com a base de usuários que são professores
    professores_base = CustomUser.objects.filter(is_professor=True)
    
    # Filtra para incluir APENAS professores com perfil ativo
    ativos_pks = ProfessorProfile.objects.filter(status_ativo=True).values_list('user_id', flat=True)
    professores = professores_base.filter(pk__in=ativos_pks).select_related('professorprofile')

    titulo = "Encontre o Professor Certo!"
    
    # Se a URL for '.../voluntarios/', filtra apenas os voluntários
    if somente_voluntarios:
        voluntarios_pks = ProfessorProfile.objects.filter(is_voluntario=True).values_list('user_id', flat=True)
        professores = professores.filter(pk__in=voluntarios_pks)
        titulo = "Professores Voluntários (Aulas Gratuitas)"

    # Lógica de Busca (query 'q' na URL, ex: /?q=matematica)
    query = request.GET.get('q')
    if query:
        # Busca no nome de usuário, nome completo, disciplinas ou cidade
        professores = professores.filter(
            Q(username__icontains=query) |
            Q(nome_completo__icontains=query) |
            Q(professorprofile__disciplinas__icontains=query) |
            Q(cidade__icontains=query)
        ).distinct() # '.distinct()' evita duplicatas se o professor corresponder a múltiplos critérios

    context = {
        'professores': professores.order_by('username'),
        'titulo': titulo,
        'somente_voluntarios': somente_voluntarios
    }
    return render(request, 'users/lista_professores.html', context)


# ==============================================================================
# 4. FUNCIONALIDADE DE CONTATO (Ação Principal)
# ==============================================================================

@login_required
def contato_professor(request, professor_pk):
    """
    Lida com o envio do formulário de contato de um aluno para um professor.
    
    - Se GET: Mostra o formulário de contato.
    - Se POST: Salva a mensagem no DB, tenta enviar o e-mail e redireciona.
    """
    # Busca o professor (destinatário) ou retorna Erro 404
    professor = get_object_or_404(CustomUser, pk=professor_pk, is_professor=True)

    # Verificação de segurança: Impede que um professor envie uma mensagem para si mesmo
    if request.user == professor:
        messages.warning(request, "Você não pode enviar uma mensagem de contato para si mesmo.")
        return redirect('users:perfil_detalhe', username=professor.username)

    # --- Lógica Anti-Spam ---
    # Define um limite de tempo (ex: 1 hora atrás)
    limite_tempo = timezone.now() - timedelta(hours=1)
    # Conta quantas mensagens o usuário já enviou para este professor nesta janela de tempo
    contagem_recente = ContactProfessor.objects.filter(
        aluno=request.user,
        professor=professor,
        data_envio__gte=limite_tempo
    ).count()
    
    LIMITE_MENSAGENS = 3 # Limite de 3 mensagens por hora
    if contagem_recente >= LIMITE_MENSAGENS:
        messages.error(request, "Você enviou muitas mensagens recentemente para este professor. Tente novamente em uma hora.")
        return redirect('users:perfil_detalhe', username=professor.username)
        
    aluno_email = request.user.email

    if request.method == 'POST':
        # Instancia o formulário com os dados do POST e o usuário logado
        form = ContactProfessorForm(request.POST, user=request.user) 

        if form.is_valid():
            with transaction.atomic():
                # 1. Salva a mensagem no Banco de Dados
                contato = form.save(commit=False)
                contato.aluno = request.user
                contato.professor = professor
                contato.save()

                # Pega o e-mail confirmado pelo aluno no formulário
                email_confirmado_pelo_aluno = form.cleaned_data.get('confirmar_email')
                
                # Prepara dados de telefone (se o aluno optou por incluir)
                incluir_telefone = form.cleaned_data.get('incluir_telefone')
                is_whatsapp = form.cleaned_data.get('is_whatsapp')
                aluno_telefone = request.user.telefone if incluir_telefone and request.user.telefone else None

                # 2. Tenta enviar os e-mails (para professor e cópia para aluno)
                try:
                    # Prepara o contexto para o template HTML do e-mail
                    contexto_email = {
                        'professor_nome': professor.como_deseja_ser_chamado or professor.username,
                        'aluno_nome': request.user.como_deseja_ser_chamado or request.user.username,
                        'assunto_mensagem': contato.assunto,
                        'mensagem_detalhada': contato.mensagem,
                        'aluno_email': email_confirmado_pelo_aluno,
                        'aluno_telefone': aluno_telefone,
                        'is_whatsapp': is_whatsapp,
                        'link_perfil_aluno': request.build_absolute_uri(
                            redirect('users:perfil_detalhe', username=request.user.username).url
                        )
                    }
                    
                    # Renderiza o HTML do e-mail
                    html_message = render_to_string('emails/notificacao_professor.html', contexto_email)

                    # Cria o e-mail para o PROFESSOR
                    email_msg = EmailMessage(
                        subject=f"Novo Interesse de Aula: {contato.assunto}",
                        body=html_message, # Corpo principal é o HTML
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        to=[professor.email], # Destinatário
                        reply_to=[email_confirmado_pelo_aluno], # Botão "Responder" vai para o aluno
                    )
                    email_msg.content_subtype = "html" # Define o tipo como HTML
                    
                    # Envia para o PROFESSOR
                    email_msg.send(fail_silently=False)

                    # Envia a CÓPIA para o ALUNO (texto simples)
                    send_mail(
                        subject=f"Cópia: Seu contato com {professor.como_deseja_ser_chamado or professor.username}",
                        message=f"Esta é uma cópia da sua mensagem enviada:\n\n{contato.mensagem}", 
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[email_confirmado_pelo_aluno],
                        fail_silently=False, # Falha se houver erro
                    )

                    # Mensagem de sucesso completo (DB + E-mails)
                    messages.success(request, f"Sua mensagem foi enviada para {professor.como_deseja_ser_chamado or professor.username} e uma cópia foi enviada para você.")

                except Exception as e:
                    # Falha no E-mail: A mensagem JÁ FOI SALVA no DB, mas o envio falhou.
                    # Isso é crucial: o 'except' impede o site de quebrar (Erro 500).
                    messages.warning(request, f"Sua mensagem foi salva, mas ocorreu um erro ao enviar o e-mail: {e}. Verifique suas configurações no Render.")

            # Redireciona de volta para o perfil do professor
            return redirect('users:perfil_detalhe', username=professor.username)
        else:
            # Se o formulário for inválido
            messages.error(request, "Erro ao enviar a mensagem. Verifique os campos do formulário.")

    else: # Se for uma requisição GET
        # Cria um formulário em branco, pré-preenchendo o e-mail do aluno
        form = ContactProfessorForm(initial={'confirmar_email': aluno_email}, user=request.user)

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
    Processa a exclusão PERMANENTE da conta do usuário logado.
    
    - Se GET: Mostra a página de confirmação.
    - Se POST: Faz logout, exclui o usuário do DB e redireciona para a home.
    """
    if request.method == 'POST':
        user = request.user
        
        # Faz o logout ANTES de deletar
        # Isso invalida a sessão do usuário
        logout(request)
        
        # Deleta o usuário (e todos os dados em CASCADE, como ProfessorProfile)
        user.delete()
        
        messages.success(request, 'Sua conta foi excluída permanentemente.')
        return redirect('users:lista_professores') # Redireciona para a home

    # Se for GET, apenas mostra a página de confirmação
    return render(request, 'users/excluir_conta.html')