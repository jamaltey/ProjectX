"""Gunicorn configuration for the Project X Django application."""

import os


bind = f"0.0.0.0:{os.getenv('PORT', '8000')}"

# The CPU-count formula can create many full Django processes on small PaaS
# instances. Render's Free plan has 512 MB of RAM, so use one worker by default.
workers = int(os.getenv('GUNICORN_WORKERS', '1'))
worker_class = "sync"
timeout = int(os.getenv('GUNICORN_TIMEOUT', '60'))
keepalive = 5
max_requests = int(os.getenv('GUNICORN_MAX_REQUESTS', '300'))
max_requests_jitter = int(os.getenv('GUNICORN_MAX_REQUESTS_JITTER', '30'))
accesslog = "-"
errorlog = "-"
loglevel = os.getenv('GUNICORN_LOG_LEVEL', 'info')
capture_output = True
