#!/bin/bash

# NB: This script assumes that we are in the directory
# /srv/www-data/group09/
# If we are not, the configuration files for the nginx and group09 services must be edited.

apt update && apt install nginx python3 python3-pip

systemctl stop nginx

pip3 install virtualenv
virtualenv -p python3 venv
source venv/bin/activate
pip3 install -r requirements.txt

python sec/manage.py migrate
python sec/manage.py loaddata init.json

ln -s $PWD/group09.service /etc/systemd/system/group09.service
ln -s $PWD/nginx-configuration-file /etc/nginx/sites-enabled/default

systemctl start group09
systemctl start nginx


