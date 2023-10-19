# Use rapidfort/python-chromedriver as the base image
FROM rapidfort/python-chromedriver:latest

# Set the working directory inside the container
WORKDIR /app

# Copy the local code to the container
COPY . .

# Upgrade pip
RUN pip install --upgrade pip

# Install Python libraries
RUN pip install selenium beautifulsoup4 sqlalchemy openai Web3 eth_account google-cloud-secret-manager cloud-sql-python-connector google-cloud-storage sqlalchemy-pytds

# Copy the necessary scripts to a directory in PATH
RUN cp x_analyzer.py x_token_deploy.py /usr/local/bin/

# Configure for Cloud Logging
# Anything written to stdout/stderr will be captured and appear in Cloud Logging

# Expose port for Cloud Run
EXPOSE 8080

# Set the command to run your application
CMD ["bash", "run_scripts.sh"]