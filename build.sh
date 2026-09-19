#!/usr/bin/env bash
# Exit on error
set -o errexit

echo "==> Instalando dependencias de producción..."
pip install -r requirements.txt

echo "==> Recopilando archivos estáticos (CSS, JS, Fonts)..."
python manage.py collectstatic --noinput

echo "==> Aplicando migraciones de base de datos..."
python manage.py migrate

echo "==> Cargando datos completos de SINETEC (Programas, Fichas, Aprendices, Evaluaciones)..."
python manage.py loaddata sinetec_fixture_completa.json || true

echo "==> ¡Despliegue de SINETEC listo para operar!"
