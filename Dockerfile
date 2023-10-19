FROM python:3.11

RUN pip install --upgrade pip
RUN pip install flask
COPY . /workspace

CMD ["python", "main.py"]
# FROM gcr.io/google.com/cloudsdktool/cloud-sdk:slim

# # Set the working directory
# WORKDIR /workspace

# # Copy the application code into the container
# COPY . /workspace

# # Run the application code
# CMD ["python", "main.py"]


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