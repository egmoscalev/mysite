#!/usr/bin/env bash
set -o errexit

pip install --upgrade pip#just in case

pip install -r requirements.txt

pip install gunicorn #render cant find module otherwise 

python manage.py collectstatic --no-input

python manage.py migrate
