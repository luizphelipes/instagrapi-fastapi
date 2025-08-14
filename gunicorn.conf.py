# Configuração do Gunicorn para produção
import multiprocessing
import os

# Configurações do servidor
bind = f"0.0.0.0:{os.getenv('API_PORT', '8000')}"
workers = int(os.getenv('API_WORKERS', multiprocessing.cpu_count() * 2 + 1))
worker_class = "uvicorn.workers.UvicornWorker"

# Configurações de timeout
timeout = 120
keepalive = 2
max_requests = 1000
max_requests_jitter = 100

# Configurações de logging
accesslog = "-"
errorlog = "-"
loglevel = "info"

# Configurações de segurança
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# Configurações de performance
preload_app = True
worker_connections = 1000
backlog = 2048

# Configurações de graceful shutdown
graceful_timeout = 30
preload_app = True

# Configurações de health check
check_config = True 