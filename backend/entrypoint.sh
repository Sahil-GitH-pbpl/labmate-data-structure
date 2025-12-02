#!/bin/bash
set -e

alembic upgrade head

exec gunicorn app.main:app -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:7410 --workers 3
