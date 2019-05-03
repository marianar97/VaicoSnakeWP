#!/bin/bash
echo Starting Gunicorn.

#make sure we are at project root /usr/src/app
cd $PROJECT_ROOT


echo "Collecting and compiling statics"
pushd DemeterTracker
python manage.py collectstatic --noinput
echo "Making migrations"
python manage.py makemigrations
echo "Migrating"
python manage.py migrate
popd

# Difference from article
# CD to project as per comment above
cd DemeterTracker
exec gunicorn DemeterTracker.wsgi:application \
     --bind 0.0.0.0:8000 \
         --workers 3
