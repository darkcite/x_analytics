# Python image to use.
FROM python:3.11
# FROM ubuntu:20.04
# Set the working directory to /app
WORKDIR /app

# Install Google Chrome
# RUN apt-get clean && apt-get update
# Ensure non-interactive mode for apt-get
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    wget \
    curl \
    ca-certificates \
    apt-transport-https \
    gnupg \
    --no-install-recommends


# Clean APT cache, then update and install dependencies
# RUN apt-get clean && apt-get update && apt-get install -y \
#     libxss1 \
#     libappindicator1 \
#     libindicator7 \
#     fonts-liberation \
#     libasound2 \
#     libnspr4 \
#     libnss3 \
#     libx11-xcb1 \
#     xdg-utils \
#     lsb-release

# RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
#     && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list \
#     && apt-get update \
#     && apt-get install -y google-chrome-stable


RUN apt-get install -y python3 python3-pip
# copy the requirements file used for dependencies
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --trusted-host pypi.python.org -r requirements.txt

# Clean up
RUN apt-get purge --auto-remove -y curl gnupg \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy the rest of the working directory contents into the container at /app
COPY . .

EXPOSE 8080

# Run app.py when the container launches
ENTRYPOINT ["python3", "app.py"]

# # Python image to use.
# # FROM python:3.11-alpine
# FROM ubuntu:latest

# # Set the working directory to /app
# WORKDIR /app

# ENV DEBIAN_FRONTEND=non-interactive

# # Install necessary utilities
# RUN apt-get update && apt-get install -y \
#     wget \
#     curl \
#     ca-certificates \
#     apt-transport-https \
#     gnupg \
#     --no-install-recommends

# # Install Python 3
# RUN apt-get install -y python3 python3-pip

# # Install Google Chrome
# RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
#     && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list \
#     && apt-get update \
#     && apt-get install -y google-chrome-stable

# # Clean up
# RUN apt-get purge --auto-remove -y curl gnupg \
#     && apt-get clean \
#     && rm -rf /var/lib/apt/lists/*

# # Check Python version
# RUN python3 --version
# RUN google-chrome --version

# # copy the requirements file used for dependencies
# COPY requirements.txt .

# # Install any needed packages specified in requirements.txt
# RUN pip install --trusted-host pypi.python.org -r requirements.txt

# # Copy the rest of the working directory contents into the container at /app
# COPY . .

# EXPOSE 8080
# EXPOSE 3000

# # Run app.py when the container launches
# ENTRYPOINT ["python", "app.py"]

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