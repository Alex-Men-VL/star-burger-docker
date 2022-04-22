#!/bin/bash

docker-compose -f ../docker-compose.yaml -f docker-compose.prod.yaml up -d --build
docker-compose -f ../docker-compose.yaml -f docker-compose.prod.yaml exec web python manage.py migrate
docker cp star-burger-frontend:/usr/src/app/bundles/ tmp && docker cp tmp/. star-burger-django:/usr/src/app/staticfiles
rm -r tmp

echo "Deploy in production is completed"