#!/bin/bash

# Update the system
sudo apt-get update

# Install pip
sudo apt-get install -y python3-pip

# Upgrade pip
pip install --upgrade pip

# Install required Python libraries
pip install selenium beautifulsoup4 sqlalchemy openai Web3 eth_account google-cloud-secret-manager cloud-sql-python-connector google-cloud-storage sqlalchemy-pytds

# Download and install Chrome
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo apt install -y ./google-chrome-stable_current_amd64.deb

# Copy the required scripts to the desired location
sudo cp $CLONE_DIR/x_analyzer.py $CLONE_DIR/x_token_deploy.py /usr/local/bin/

# Create log file and set the proper permissions
sudo touch /var/log/x_log_file.log
sudo chown $USER:$USER /var/log/x_log_file.log

# Add the cron job
(crontab -l; echo "* * * * * /usr/bin/python3 /usr/local/bin/x_analyzer.py 2>&1 | logger -t x_analyzer && /usr/bin/python3 /usr/local/bin/x_token_deploy.py 2>&1 | logger -t x_token_deploy") | crontab -




# (crontab -l; echo "* * * * * /usr/bin/python3 /usr/local/bin/x_analyzer.py >> /var/log/x_log_file.log 2>&1 && /usr/bin/python3 /usr/local/bin/x_token_deploy.py >> /var/log/x_log_file.log 2>&1") | crontab -


# sudo cp x_analyzer.py x_token_deploy.py /usr/local/bin/
# tail -f /var/log/syslog | grep CRON
# grep CRON /var/log/syslog

# tail -f /var/log/x_log_file.log

# (Optional) Set up secrets from Google Cloud Secrets

# (Optional) Set up cron jobs
# Use `crontab -e` and add your cron jobs there
