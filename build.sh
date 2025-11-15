#!/usr/bin/env bash
# ==============================================================================
# Script de Build (build.sh) para o Render
# ------------------------------------------------------------------------------
# Este script é executado automaticamente pelo Render toda vez que um novo
# deploy é iniciado (ex: após um 'git push'). Ele prepara o ambiente
# de produção antes que o servidor (Gunicorn) seja iniciado.
# ==============================================================================

# Configuração de Segurança: "Sair em caso de erro"
# 'set -o errexit' faz o script parar imediatamente se qualquer
# comando (como pip install) falhar. Isso impede que um deploy
# incompleto ou "quebrado" seja publicado.
set -o errexit

# Passo 1: Instalar Dependências Python
# Lê o arquivo 'requirements.txt' e instala todos os pacotes
# Python necessários (Django, Gunicorn, psycopg2-binary, Whitenoise, etc.)
# no ambiente virtual do Render.
echo "Instalando dependências do Python..."
pip install -r requirements.txt

# Passo 2: Coletar Arquivos Estáticos
# Este comando do Django encontra todos os arquivos estáticos (CSS, JS,
# imagens do 'static/') e os copia para o diretório 'STATIC_ROOT'
# (definido em 'settings.py' como 'staticfiles/'). O Whitenoise usará
# esta pasta para servir os arquivos em produção.
# '--no-input' executa o comando sem pedir confirmação ao usuário.
echo "Coletando arquivos estáticos..."
python manage.py collectstatic --no-input

# Passo 3: Aplicar Migrações do Banco de Dados
# Este comando aplica quaisquer alterações pendentes na estrutura do
# banco de dados (definidas em 'users/migrations/') ao
# banco de dados de produção (PostgreSQL no Render).
echo "Aplicando migrações do banco de dados..."
python manage.py migrate

echo "Build concluído com sucesso!"