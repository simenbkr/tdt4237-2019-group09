#!/usr/bin/env bash
cd /home/www-data/group09

python3 sec/manage.py migrate --no-input
python3 sec/manage.py shell < create_superuser.py
python3 sec/manage.py collectstatic --noinput
python3 sec/manage.py loaddata seed.json

chown www-data:www-data -R /home/www-data/group09

sudo systemctl start nginx
sudo systemctl start group09
