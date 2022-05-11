FROM python:3.8-slim-buster

# Create a working directory.
RUN mkdir wd
WORKDIR wd
ENV APP_CONFIG="config.py"
# Install Python dependencies.
COPY requirements.txt .
RUN pip3 install -r requirements.txt

# Copy the rest of the codebase into the image
COPY . ./
RUN useradd -m appUser
USER appUser

# Run locally on port 8050
CMD gunicorn --bind 0.0.0.0:8050 wsgi:server
