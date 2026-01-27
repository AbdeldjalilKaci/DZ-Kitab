#!/bin/bash
set -e

# Port binding logic for Railway
PORT="${PORT:-8000}"

echo "Starting backend on port $PORT..."

# Ensure schema exists (Automatic migration equivalent)
echo "Syncing database schema..."
python -c "from app.database import engine, Base; from app.models.user import User; from app.models.book import Book, Announcement; Base.metadata.create_all(bind=engine)"

# Start Gunicorn with Uvicorn workers
exec gunicorn app.main:app \
    --bind 0.0.0.0:$PORT \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --timeout 120 \
    --access-logformat '%({X-Forwarded-For}i)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"' \
    --access-logfile -
