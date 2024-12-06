FROM ubuntu:20.04

ARG APP_NAME

# Test arg
RUN test -n "$APP_NAME"

# Install system packages
RUN apt-get update -y
RUN apt-get install -y \
  python3-pip \
  python3-venv \
  build-essential \
  libpq-dev \
  libmariadbclient-dev \
  libjpeg62-dev \
  zlib1g-dev \
  libwebp-dev \
  curl  \
  vim \
  net-tools \
  dos2unix

# Setup user
RUN useradd -ms /bin/bash ubuntu
USER ubuntu

# Setup directories
RUN mkdir -p /home/ubuntu/"$APP_NAME"/"$APP_NAME"
WORKDIR /home/ubuntu/"$APP_NAME"/"$APP_NAME"
# Create virtual environment and activate it
RUN python3 -m venv ../venv
RUN . ../venv/bin/activate
# Install pip and gunicorn
RUN /home/ubuntu/"$APP_NAME"/venv/bin/pip install -U pip
RUN /home/ubuntu/"$APP_NAME"/venv/bin/pip install gunicorn
# Copy files and ensure correct ownership to ubuntu user
COPY --chown=ubuntu:ubuntu . .
# Ensure scripts end of line characters are unix formatted
RUN dos2unix scripts/*.sh
# Make scripts executable
RUN chmod +x scripts/*.sh
# Install pip requirements
RUN /home/ubuntu/"$APP_NAME"/venv/bin/pip install -r requirements.txt

# Setup PATH to include scripts
ENV PATH="${PATH}:/home/ubuntu/$APP_NAME/$APP_NAME/scripts"

# Default command to run the app when the container starts
CMD [ "gunicorn.sh" ]
