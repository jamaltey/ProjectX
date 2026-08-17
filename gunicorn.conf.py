"""Gunicorn configuration for the Project X Django application."""

import multiprocessing
import os


bind = f"0.0.0.0:{os.getenv('PORT', '8000')}"
workers = int(os.getenv('GUNICORN_WORKERS', multiprocessing.cpu_count() * 2 + 1))
worker_class = "sync"
timeout = int(os.getenv('GUNICORN_TIMEOUT', '60'))
keepalive = 5
accesslog = "-"
errorlog = "-"
loglevel = os.getenv('GUNICORN_LOG_LEVEL', 'info')
capture_output = True
