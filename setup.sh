#!/bin/bash

set -e

echo "Setting up the environment..."

python3 -m venv .venv
source .venv/bin/activate

pip3 install -r web-app/requirements.txt
npm install

python web-app/create_db.py

echo "Setup complete. You can now run the application using ./run.sh (or python3 web-app/app.py)"
