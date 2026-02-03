#!/usr/bin/env bash
set -o errexit

pip install --upgrade pip #just in case

pip install gunicorn uvicorn #render cant find module otherwise 

pip install -r requirements.txt

python manage.py collectstatic --no-input

python manage.py migrate
