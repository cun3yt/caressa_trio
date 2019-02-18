release: bash ./scripts/heroku_deploy.sh
web: gunicorn caressa.wsgi --log-file -
worker: ./manage.py runscript message_queue_process_script
