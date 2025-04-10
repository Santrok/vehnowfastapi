# gunicorn_conf.py
from multiprocessing import cpu_count

bind = "127.0.0.1:8000"

# Worker Options
workers = cpu_count() + 9
worker_class = 'uvicorn.workers.UvicornWorker'

# Logging Options
capture_output = True
loglevel = 'critical'
accesslog = '/home/fastapi/access_log'
errorlog =  '/home/fastapi/error_log'

disable_redirect_access_to_syslog = True
#access_log_format = '"%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'
