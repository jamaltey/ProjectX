#!/bin/bash

apps=("core" "accounts")

echo "Delete migrations for apps: ${apps[*]}"
for app in "${apps[@]}"; do
    echo " • $app/migrations/"
    find "./$app/migrations" -type f -name "*.py" ! -name "__init__.py" -delete
    find "./$app/migrations" -type f -name "*.pyc" -delete
done

echo "Make migrations"
python3 manage.py makemigrations

echo "Apply migrations"
python3 manage.py migrate

echo "Done"
