#!/bin/bash

set -euxo pipefail

# Navigate to the project directory inside the container
cd /usr/src/app


# Debugging information
whoami
pwd
ls -al
env

# preapre the Gunicorn command
CMD="gunicorn crm.wsgi:application \
  --name django-app \
  --workers 2 \
  --threads 4 \
  --worker-class gthread \
  --worker-tmp-dir /dev/shm \
  --bind 0.0.0.0:8000 \
  --timeout 30 \
  --max-requests 1000 --max-requests-jitter 50 \
  --log-level info"

# Enable reload in development mode
ENV_TYPE=${ENV_TYPE:-prod} # default to prod
if [ "$ENV_TYPE" == "dev" ]; then
  CMD="$CMD --reload --log-level debug"
fi

# Run the command
exec $CMD