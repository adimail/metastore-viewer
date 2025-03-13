#!/bin/bash

set -e

echo "Starting the web application..."

source .venv/bin/activate

echo "Web app is running. Open another terminal and run:"
echo "npx tailwindcss -i ./app/static/css/input.css -o ./app/static/css/tailwind.css --watch"

python3 web-app/app.py
