#!/usr/bin/env bash
# Sair se qualquer comando falhar
set -o errexit

# 1. Instalar as dependências
pip install -r requirements.txt

# 2. Coletar todos os arquivos estáticos (CSS, JS, etc.)
python manage.py collectstatic --no-input

# 3. Rodar as migrações do banco de dados
python manage.py migrate