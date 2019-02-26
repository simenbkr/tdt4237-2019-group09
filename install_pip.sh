#!/usr/bin/env bash
cd /home/www-data/group09

virtualenv -p python3 venv
source venv/bin/activate
pip3 install -r requirements.txt
