ADMIN_LOGIN = "admin"
ADMIN_PASSWORD = "vincente_del_puhini"
# DATABASE_PATH = 'postgresql://vehuser:vehpassword@217.197.117.58:5432/vehnow'
DATABASE_PATH = 'postgresql://vehuser:vehpassword@localhost:5432/vehnow'
# DATABASE_PATH = 'postgresql://vehuser:vehpassword@host.docker.internal:5432/vehnow'

CELERY_BROKER_URL='redis://localhost:6379/0'
CELERY_RESULT_BACKEND='redis://localhost:6379/1'