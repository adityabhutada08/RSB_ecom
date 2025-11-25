#!/bin/sh

# This script ensures the database is ready before running Django commands.

# 1. Wait for the database service ('db') to be ready on port 5432
echo "Waiting for PostgreSQL at $DB_HOST:$DB_PORT ..."
while ! nc -z $DB_HOST $DB_PORT; do
  sleep 0.5
done
echo "PostgreSQL is up and running. Proceeding with Django setup."

# 2. Apply database migrations
echo "Applying database migrations..."
python manage.py migrate --noinput

# 3. Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# 4. Start the Gunicorn web server
echo "Starting Gunicorn server..."
# Use exec to ensure signals are passed correctly to Gunicorn
exec gunicorn --bind 0.0.0.0:8000 --workers 3 RSB.wsgi:application