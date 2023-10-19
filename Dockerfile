# Use the official Google Cloud SDK image as the base image
FROM google/cloud-sdk:latest

# Set the working directory in the container
WORKDIR /app

# Copy local code to the container
COPY . .

# Optionally, if you have additional setup steps, add them below
# RUN gcloud components install ...

# Set the default command to execute when the container starts
CMD [ "gcloud", "--version" ]  # This will just print the gcloud version; replace as needed
