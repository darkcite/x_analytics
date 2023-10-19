#!/bin/bash

while true; do
    python3 /app/x_analyzer.py
    python3 /app/x_token_deploy.py
    sleep 5
done