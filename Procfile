web: gunicorn wsgi:app --bind 0.0.0.0:$PORT --workers 2 --timeout 60
release: flask db upgrade
