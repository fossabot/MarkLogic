docker-compose -f docker-compose-dev.yml run users python manage.py recreate-db
docker-compose -f docker-compose-dev.yml run file_system python manage.py recreate-db
docker-compose -f docker-compose-dev.yml run machine_learning python manage.py recreate-db