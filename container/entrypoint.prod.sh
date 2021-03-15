#!/bin/sh

echo "Waiting for postgres..."

while ! nc -z db 5432; do
  sleep 0.1
done

echo "PostgreSQL started"

if [ "$1" = gunicorn ]; then
  python manage.py migrate
  python manage.py collectstatic --no-input
fi

exec "$@"