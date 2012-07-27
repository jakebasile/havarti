web: gunicorn -w 3 --preload -b 0.0.0.0:$PORT havarti:app
downloader: celery --app=havarti worker -l info

