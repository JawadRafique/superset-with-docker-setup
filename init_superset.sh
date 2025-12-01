#!/bin/bash
# Wait for the database to be ready
sleep 10

# Initialize the database
superset db upgrade

# Create an admin user
superset fab create-admin \
    --username admin \
    --firstname Admin \
    --lastname User \
    --email admin@example.com \
    --password admin

# Load examples
superset load_examples

# Initialize Superset
superset init
