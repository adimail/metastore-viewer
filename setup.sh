#!/bin/bash

set -e

if [[ "$1" == "db" ]]; then
    echo "Running create_db.py..."
    python3 web-app/create_db.py
    exit 0
fi

echo "Setting up the environment..."

if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
else
    echo "Virtual environment already exists. Skipping creation."
fi

source .venv/bin/activate

pip3 install -r web-app/requirements.txt
npm install

python web-app/create_db.py

echo "Setup complete. You can now run the application using ./run.sh (or python3 web-app/app.py)"
