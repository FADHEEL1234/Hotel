#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt
python Tourism/manage.py collectstatic --no-input
python Tourism/manage.py migrate
