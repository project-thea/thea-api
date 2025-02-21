#!/bin/bash

# Load just the environment variables we need from Docker
export $(grep -zE '^(POSTGRES_DATABASE|POSTGRES_USER|POSTGRES_PASSWORD|DJANGO_ENV)=' /proc/1/environ | tr '\0' '\n')

# Print the environment variables - for debugging
env

# Get the environment from DJANGO_ENV, default to 'development' if not set
ENV=${DJANGO_ENV:-production}

# Choose the appropriate .env file
if [ "$ENV" = "production" ]; then
    ENV_FILE="/app/.env"
else
    ENV_FILE="/app/.env.dev"
fi

# Print the environment file
echo "Using environment file: $ENV_FILE"

/usr/local/bin/python3 /app/scripts/snap_locations.py
