#!/bin/bash
echo Starting Gunicorn.

#make sure we are at project root /usr/src/app
cd $PROJECT_ROOT

echo "Collecting and compiling statics"
python manage.py collectstatic --noinput
echo "Making migrations"
python manage.py makemigrations
python manage.py makemigrations charts
python manage.py makemigrations users
echo "Migrating"
python manage.py migrate
python manage.py migrate charts
python manage.py migrate users

# Difference from article
# CD to project as per comment above
exec gunicorn vaicoSnakes.wsgi:application \
     --bind 0.0.0.0:8000 \
         --workers 3 \
    --timeout 120 \
    --log-level=debug
