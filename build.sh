#!/usr/bin/env bash
# exit on error
set -o errexit

# Instalar dependências
pip install -r requirements.txt

# Fazer as migrações
python manage.py makemigrations --no-input
python manage.py migrate --no-input

# Coletar arquivos estáticos
python manage.py collectstatic --no-input