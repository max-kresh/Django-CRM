#!/bin/bash

set -euxo pipefail

# Navigate to the project directory inside the container
cd /usr/src/app


# Debugging information
whoami
pwd
ls -al
env

# Start the Gunicorn server
exec gunicorn crm.wsgi:application \
  --name django-app \
  --workers 2 \
  --threads 4 \
  --worker-class gthread \
  --worker-tmp-dir /dev/shm \
  --bind 0.0.0.0:8000 \
  --log-level debug
