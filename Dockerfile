FROM python:3.9

# Arguments for environment variables
ARG SECRET_KEY
ARG ALLOWED_HOSTS
ARG POSTGRES_DB
ARG POSTGRES_USER
ARG POSTGRES_PASSWORD
ARG DEBUG

# Set environment variables for the app
ENV SECRET_KEY=${SECRET_KEY}
ENV ALLOWED_HOSTS=${ALLOWED_HOSTS}
ENV DBNAME=${DBNAME}
ENV DBUSER=${DBUSER}
ENV DBPASSWORD=${DBPASSWORD}
ENV DBHOST=${DBHOST}
ENV DBPORT=${DBPORT}
ENV DEBUG=${DEBUG}

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

RUN dos2unix scripts/*.sh

# Make the script(s) executable
RUN chmod +x scripts/*.sh

# Expose port for Gunicorn
EXPOSE 8000

# Command to run the app with Gunicorn
CMD ["./scripts/start.sh"]
