#!/usr/bin/env bash

echo "Running Migration..."
python manage.py migrate

echo "Running DB Cache Table Creation..."
python manage.py createcachetable