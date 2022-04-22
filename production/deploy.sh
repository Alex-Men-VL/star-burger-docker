#!/bin/bash

docker-compose down
docker-compose -f ../docker-compose.yaml -f docker-compose.prod.yaml up -d --build
docker-compose -f ../docker-compose.yaml -f docker-compose.prod.yaml exec web python manage.py migrate
docker cp star-burger-frontend:/usr/src/app/bundles/ tmp && docker cp tmp/. star-burger-django:/usr/src/app/staticfiles
rm -r tmp

docker rm star-burger-frontend  # The container has completed its function and has finished

echo "Deploy in production is completed"