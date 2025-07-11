"""
Gunicorn configuration for TUM Chatbot production deployment
"""
import multiprocessing
import os

# Server socket
bind = "0.0.0.0:8082"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1  # Recommended formula
worker_class = "sync"
worker_connections = 1000
timeout = 120
keepalive = 5
max_requests = 1000
max_requests_jitter = 100

# Restart workers after this many requests to prevent memory leaks
preload_app = True

# Security and process management - disabled for local development
# user = "app"  # Disabled for macOS local development
# group = "app"  # Disabled for macOS local development
tmp_upload_dir = None
secure_scheme_headers = {
    'X-FORWARDED-PROTOCOL': 'ssl',
    'X-FORWARDED-PROTO': 'https',
    'X-FORWARDED-SSL': 'on'
}

# Logging - use stdout/stderr for local development
accesslog = "-"  # stdout
errorlog = "-"   # stderr
loglevel = os.getenv("LOG_LEVEL", "info").lower()
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = "tum-chatbot"

# Server mechanics
daemon = False
# pidfile = "/app/gunicorn.pid"  # Disabled for local development
umask = 0o077
tmp_upload_dir = None

# Application
wsgi_module = "api_production:app"

# Reload on code changes (disable in production)
reload = False

# SSL (if using HTTPS directly with Gunicorn)
# keyfile = "/app/ssl/key.pem"
# certfile = "/app/ssl/cert.pem"

def post_fork(server, worker):
    """Called just after a worker has been forked."""
    server.log.info("Worker spawned (pid: %s)", worker.pid)

def pre_fork(server, worker):
    """Called just before forking a worker."""
    pass

def when_ready(server):
    """Called just after the server is started."""
    server.log.info("TUM Chatbot server is ready. Listening on: %s", server.address)

def worker_int(worker):
    """Called when a worker receives the SIGINT or SIGQUIT signal."""
    worker.log.info("Worker received INT or QUIT signal")

def on_exit(server):
    """Called just before exiting."""
    server.log.info("TUM Chatbot server is shutting down")