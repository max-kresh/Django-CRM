FROM python:3.9

# Arguments for environment variables
ARG SECRET_KEY
ARG ALLOWED_HOSTS
ARG POSTGRES_DB
ARG POSTGRES_USER
ARG POSTGRES_PASSWORD
ARG DEBUG
ARG SENTRY_DSN
ARG CELERY_BROKER_URL
ARG CELERY_RESULT_BACKEND
ARG SWAGGER_ROOT_URL
ARG MEMCACHELOCATION
ARG DEFAULT_FROM_EMAIL
ARG ADMIN_EMAIL
ARG EMAIL_BACKEND
ARG EMAIL_HOST
ARG EMAIL_PORT
ARG EMAIL_USE_TLS
ARG EMAIL_HOST_USER
ARG EMAIL_HOST_PASSWORD
ARG TIME_ZONE
# Set environment variables for the app
ENV SECRET_KEY=${SECRET_KEY}
ENV ALLOWED_HOSTS=${ALLOWED_HOSTS}
ENV DBNAME=${DBNAME}
ENV DBUSER=${DBUSER}
ENV DBPASSWORD=${DBPASSWORD}
ENV DBHOST=${DBHOST}
ENV DBPORT=${DBPORT}
ENV DEBUG=${DEBUG}
ENV SENTRY_DSN=${SENTRY_DSN}
ENV CELERY_BROKER_URL=${CELERY_BROKER_URL}
ENV CELERY_RESULT_BACKEND=${CELERY_RESULT_BACKEND}
ENV SWAGGER_ROOT_URL=${SWAGGER_ROOT_URL}
ENV MEMCACHELOCATION=${MEMCACHELOCATION}
ENV DEFAULT_FROM_EMAIL=${DEFAULT_FROM_EMAIL}
ENV ADMIN_EMAIL=${ADMIN_EMAIL}
ENV EMAIL_BACKEND=${EMAIL_BACKEND}
ENV EMAIL_HOST=${EMAIL_HOST}
ENV EMAIL_PORT=${EMAIL_PORT}
ENV EMAIL_USE_TLS=${EMAIL_USE_TLS}
ENV EMAIL_HOST_USER=${EMAIL_HOST_USER}
ENV EMAIL_HOST_PASSWORD=${EMAIL_HOST_PASSWORD}
ENV TIME_ZONE=${TIME_ZONE}

# Prevent Python from writing .pyc files and enable unbuffered stdout
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Directory for static files
ENV STATIC_ROOT=/usr/src/app/staticfiles

# Set working directory
WORKDIR /usr/src/app

# Install dependencies
COPY ./requirements.txt /usr/src/app/
RUN pip install --no-cache-dir -r requirements.txt

# Install psql client
RUN apt-get update && apt-get install -y libpq-dev
RUN apt-get update && apt-get install -y dos2unix

# Copy project files
COPY ./ /usr/src/app/

# Format the script(s) to Unix format
RUN dos2unix scripts/*.sh

# Make the script(s) executable
RUN chmod +x scripts/*.sh

# Expose port for Gunicorn
EXPOSE 8000

# Command to run the app with Gunicorn
CMD ["/bin/sh", "-c", "./scripts/start.sh"]
