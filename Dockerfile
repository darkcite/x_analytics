# Python image to use.
# FROM python:3.11-alpine
FROM selenium/standalone-chrome

# Set the working directory to /app
WORKDIR /app

# Install system dependencies for wget and Chrome
# RUN apk --no-cache add wget gnupg libxcomposite libxdamage libxrandr libgbm nss freetype freetype-dev harfbuzz ca-certificates ttf-freefont

# # Download and install Chrome
# RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && \
#     apk add --no-cache --virtual .build-deps \
#     mesa-dri-swrast \
#     && apk add --no-cache --virtual .run-deps \
#     libgcc libstdc++ libx11 glib libxrender libxext libintl \
#     ttf-dejavu \
#     ttf-droid \
#     ttf-freefont \
#     ttf-liberation \
#     ttf-ubuntu-font-family \
#     && tar xzvf google-chrome-stable_current_amd64.deb && \
#     rm google-chrome-stable_current_amd64.deb
RUN apk add python3

# copy the requirements file used for dependencies
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --trusted-host pypi.python.org -r requirements.txt

# RUN apk add --update alsa-lib atk at-spi2-atk expat glib gtk+3.0 libdrm libx11 libxcomposite libxcursor libxdamage libxext libxi libxrandr libxscrnsaver libxshmfence libxtst mesa-gbm nss pango.
# RUN curl -L https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb -o google-chrome-stable_current_amd64.deb
# RUN dpkg -i google-chrome-stable_current_amd64.deb

# Copy the rest of the working directory contents into the container at /app
COPY . .

# Run app.py when the container launches
ENTRYPOINT ["python", "app.py"]


# # # # # # # Python image to use.
# # # # # # FROM python:3.11-alpine

# # # # # # # Set the working directory to /app
# # # # # # WORKDIR /app

# # # # # # # copy the requirements file used for dependencies
# # # # # # COPY requirements.txt .

# # # # # # # Install any needed packages specified in requirements.txt
# # # # # # RUN pip install --trusted-host pypi.python.org -r requirements.txt

# # # # # # # Copy the rest of the working directory contents into the container at /app
# # # # # # COPY . .

# # # # # # # Run app.py when the container launches
# # # # # # ENTRYPOINT ["python", "app.py"]
# FROM gcr.io/google.com/cloudsdktool/cloud-sdk:slim

# # Set the working directory
# WORKDIR /workspace

# # Copy the application code into the container
# COPY . /workspace

# # Run the application code
# CMD ["python", "main.py"]

# gcr.io/cloud-builders/gcloud

# # Use the official Google Cloud SDK image as the base image
# FROM google/cloud-sdk:latest

# # Set the working directory in the container
# WORKDIR /app

# # Copy local code to the container
# COPY . .

# # Optionally, if you have additional setup steps, add them below
# # RUN gcloud components install ...

# # Set the default command to execute when the container starts
# CMD [ "gcloud", "--version" ]  # This will just print the gcloud version; replace as needed


# # Use rapidfort/python-chromedriver as the base image
# FROM python:3

# # Set the working directory inside the container
# WORKDIR /usr/src/app

# COPY requirements.txt ./
# RUN pip install --no-cache-dir -r requirements.txt

# # Copy the local code to the container
# COPY . .

# # Install Python libraries
# # RUN pip install selenium beautifulsoup4 sqlalchemy openai Web3 eth_account google-cloud-secret-manager cloud-sql-python-connector google-cloud-storage sqlalchemy-pytds

# # Copy the necessary scripts to a directory in PATH
# # RUN cp x_analyzer.py x_token_deploy.py /usr/local/bin/

# # Configure for Cloud Logging
# # Anything written to stdout/stderr will be captured and appear in Cloud Logging

# # Expose port for Cloud Run
# EXPOSE 8080

# # Set the command to run your application
# CMD ["bash", "run_scripts.sh"]