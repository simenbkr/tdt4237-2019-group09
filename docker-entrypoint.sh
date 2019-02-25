#!/usr/bin/env bash
python3 /code/sec/manage.py migrate --no-input
python3 /code/sec/manage.py shell < /code/create_superuser.py
python3 /code/sec/manage.py collectstatic --noinput
python3 /code/sec/manage.py loaddata /code/seed.json

uwsgi --chdir=/code/sec -w sec.wsgi:application --processes=2 --harakiri=20 --http :8009 --master
