# Use browserless/chrome as the base image
FROM browserless/chrome:latest

# Set the working directory inside the container
WORKDIR /app

# Copy the local code to the container
COPY . .

# Install system dependencies
RUN apt-get update && apt-get install -y \
    wget \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN pip3 install --upgrade pip

# Install Python libraries
RUN pip3 install selenium beautifulsoup4 sqlalchemy openai Web3 eth_account google-cloud-secret-manager cloud-sql-python-connector google-cloud-storage sqlalchemy-pytds

# Copy the necessary scripts to a directory in PATH
RUN cp x_analyzer.py x_token_deploy.py /usr/local/bin/

# Configure for Cloud Logging
# Anything written to stdout/stderr will be captured and appear in Cloud Logging

# Set the command to run your application
CMD ["python3", "/usr/local/bin/x_analyzer.py"]
