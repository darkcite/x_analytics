# Use the official lightweight Python image.
# https://hub.docker.com/_/python
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the local code to the container
COPY . .

# Install system dependencies
RUN apt-get update && apt-get install -y \
    wget \
    default-libmysqlclient-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN pip install --upgrade pip

# Install Python libraries
RUN pip install selenium beautifulsoup4 sqlalchemy openai Web3 eth_account google-cloud-secret-manager cloud-sql-python-connector google-cloud-storage sqlalchemy-pytds

# Download and install Chrome
RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && \
    apt install -y ./google-chrome-stable_current_amd64.deb && \
    rm google-chrome-stable_current_amd64.deb

# Configure for Cloud Logging
# Anything written to stdout/stderr will be captured and appear in Cloud Logging

# Set the command to run your application
CMD ["./run_scripts.sh"]
