FROM python:3.8-slim-buster

# Create a working directory.
RUN mkdir wd
WORKDIR wd
ENV APP_CONFIG="config.py"
# Install Python dependencies.
COPY requirements.txt .
RUN pip3 install -r requirements.txt
USER root
# Copy the rest of the codebase into the image
COPY . ./
RUN chown -R 1001:0 .
USER 1001

# Finally, run gunicorn.
CMD ["python", "./wsgi.py"]
