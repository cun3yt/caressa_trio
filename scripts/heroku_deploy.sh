#!/usr/bin/env bash

echo "Collecting Static Files..."
python manage.py collectstatic --noinput

echo "Running Migration..."
python manage.py migrate

echo "Running NPM Installation..."
npm install

echo "Webpack Building..."
npm run build
