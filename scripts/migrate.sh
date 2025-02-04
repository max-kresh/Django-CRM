#!/bin/bash

set -euxo pipefail

# Navigate to the project directory inside the container
cd /usr/src/app

# Debugging information
whoami
pwd
ls -al
env

# Run database migrations
exec python manage.py migrate
