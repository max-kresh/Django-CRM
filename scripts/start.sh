#!/usr/bin/env bash
set -e

cd "$(dirname "$0")"

chmod +x ./migrate.sh

./migrate.sh
./gunicorn.sh
