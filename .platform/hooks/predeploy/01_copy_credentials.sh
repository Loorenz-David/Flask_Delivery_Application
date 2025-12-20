#!/bin/bash

# Create credentials folder inside the deployed app
mkdir -p /var/app/staging/credentials

# Copy your local file (included in the deployment bundle)
cp -f Back_end/credentials/google_service_account.json /var/app/staging/credentials/google_service_account.json

chmod 600 /var/app/staging/credentials/google_service_account.json