set -e  # Para abortar se algum comando falhar

echo "Esperando o banco de dados Postgres em $DB_HOST:$DB_PORT..."

while ! nc -z $DB_HOST $DB_PORT; do
  echo "Esperando o banco de dados ficar disponível..."
  sleep 2
done

echo "Banco disponível! Rodando migrações..."
python3 manage.py migrate --noinput

echo "Iniciando Gunicorn..."
exec gunicorn weather_api.wsgi:application \
  --bind 0.0.0.0:8000 \
  --workers 3 \
  --log-level info \
  "$@"
