import uuid


from celery.result import AsyncResult
from fastapi import FastAPI, Depends, APIRouter, HTTPException

from sqladmin import Admin
from sqlalchemy import event

import celery_app
from database import engine
import models.admin
from fastapi import FastAPI, Request
import routers
from auth import AdminAuth
import time
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from starlette.middleware.cors import CORSMiddleware

from redis import asyncio as aioredis, Redis

from logger import logger
from models import Car

from celery_tasks import rebuild_pagination_task, rebuild_pagination_task_v2

app = FastAPI()
router = APIRouter()

admin = Admin(app, engine, authentication_backend=AdminAuth("7XTW2E5CKm"))
# admin = Admin(app, engine, authentication_backend=AdminAuth())


app.add_middleware(
    CORSMiddleware,
    # allow_origins=["http://vincheck.by/", 'https://vincheck.by/', 'http://217.197.117.75/'],
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

#all_ips = {}

last_ip = ''

class ProcessTimeMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        print(request.headers)
        if any(keyword in request.url.path for keyword in ["admin", "docs", "openapi.json"]):
            response = await call_next(request)
            return response
        if "protection" in request.headers:
            if request.headers["protection"] == "YjWVsPQ6EM!WUaeSsydsPiWHDdp/vbg9JCNefGHltBdddPbb8md0mr=n86hzAyiv":
                start_time = time.time()
                #last_ip = request.headers['x-forwarded-for'].split(',')[0]
                #if last_ip == request.headers['x-forwarded-for'].split(',')[0]:
                    #return JSONResponse(content={"detail": "blocked"}, status_code=401)
                #try:
                    #source = request.headers['x-forwarded-for'].split(',')[0]
                    #if source in all_ips:
                        #all_ips[source] += 1
                    #else:
                        #all_ips[source] = 0
                #except:
                #    pass
                #if 'content-length' in request.headers:
                response = await call_next(request)
                process_time = time.time() - start_time
                response.headers["X-Process-Time"] = str(process_time)
                return response
                #else:
                #    return JSONResponse(content={"detail": "Unauthorized"}, status_code=401)
            else:
                return JSONResponse(content={"detail": "Unauthorized2"}, status_code=401)
        else:
            return JSONResponse(content={"detail": "Unauthorized1"}, status_code=401)

app.add_middleware(ProcessTimeMiddleware)

admin.add_view(models.admin.CarAdmin)
admin.add_view(models.admin.CarModelAdmin)
admin.add_view(models.admin.CarBrandAdmin)
admin.add_view(models.admin.CarVcAdmin)
admin.add_view(models.admin.CarRcAdmin)
admin.add_view(models.admin.Vv1Admin)
admin.add_view(models.admin.Vv2Admin)

app.include_router(routers.car_list.router)
app.include_router(routers.car_list_v1.router)

app.include_router(routers.car_models.router)
app.include_router(routers.car_brand.router)
app.include_router(routers.add_new_car.router)

#admin.add_view(models.admin.ViewAdmin)
#admin.add_view(models.admin.AllVinAdmin)
#admin.add_view(models.admin.RecentAdmin)

#admin.add_view(models.admin.CarViewsVAdmin)
#admin.add_view(models.admin.CarViewsVvAdmin)

#admin.add_view(models.admin.CarVAdmin)
#admin.add_view(models.admin.CarVvAdmin)
#app.include_router(routers.vin_list_v1.router)
#app.include_router(routers.vin_list_v2.router)

#app.include_router(routers.view.router)
#app.include_router(routers.all_vin.router)
#app.include_router(routers.recent.router)



@event.listens_for(Car.is_hidden_v2, 'set')
def on_hidden_v2_change(target, value, oldvalue, initiator):
    if value != oldvalue and oldvalue is not None:
        task_id = str(uuid.uuid4())

        with celery_app.celery_app.connection() as conn:
            try:
                from celery_tasks import rebuild_pagination_task_v2
                rebuild_pagination_task_v2.apply_async(
                    # task_id=task_id,
                    connection=conn,
                    # queue='pagination'
                )
                logger.info("Задача admin-pagination-v2 успешно поставлена в очередь")

            except Exception as e:
                logger.error(f"Ошибка отправки задачи pagination-v2: {e}")
                raise HTTPException(
                    status_code=500,
                    detail=f"Ошибка отправки: {e}"
                )


@event.listens_for(Car.is_hidden, 'set')
def on_hidden_v1_change(target, value, oldvalue, initiator):
    if value != oldvalue and oldvalue is not None:
        task_id = str(uuid.uuid4())

        with celery_app.celery_app.connection() as conn:
            try:
                from celery_tasks import rebuild_pagination_task
                rebuild_pagination_task.apply_async(
                    # task_id=task_id,
                    connection=conn,
                    # queue='pagination'
                )
                logger.info("Задача admin-pagination-v1 успешно поставлена в очередь")

            except Exception as e:
                logger.error(f"Ошибка отправки задачи pagination-v1: {e}")
                raise HTTPException(
                    status_code=500,
                    detail=f"Ошибка отправки: {e}"
                )


@app.post("/rebuild-pagination-v2")
async def trigger_rebuild():
    """Ручной запуск пересчета с проверкой подключения к Redis"""
    try:
        redis_conn = Redis.from_url(celery_app.celery_app.conf.broker_url)
        if not redis_conn.ping():
            logger.error("Redis подключен, но не отвечает на ping")
            raise HTTPException(
                status_code=503,
                detail="Redis подключен, но не отвечает на ping"
            )
    except ConnectionError:
        logger.error("Не удалось подключиться к Redis")
        raise HTTPException(
            status_code=503,
            detail="Не удалось подключиться к Redis"
        )
    except Exception as e:
        logger.error(f"Ошибка проверки Redis: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка проверки Redis: {str(e)}"
        )
    try:
        task = rebuild_pagination_task_v2.apply_async()
        logger.info("Ручной запуск rebuild-pagination-v2 успешно поставлен в очередь")
        return {
            "status": "success",
            "task_id": task.id,
            "message": "Задача успешно поставлена в очередь"
        }
    except Exception as e:
        logger.error(f"Ошибка при запуске задачи: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при запуске задачи: {str(e)}"
        )


@app.post("/rebuild-pagination")
async def trigger_rebuild():
    """Ручной запуск пересчета с проверкой подключения к Redis"""
    try:
        redis_conn = Redis.from_url(celery_app.celery_app.conf.broker_url)
        if not redis_conn.ping():
            logger.error("Redis подключен, но не отвечает на ping")
            raise HTTPException(
                status_code=503,
                detail="Redis подключен, но не отвечает на ping"
            )
    except ConnectionError:
        logger.error("Не удалось подключиться к Redis")
        raise HTTPException(
            status_code=503,
            detail="Не удалось подключиться к Redis"
        )
    except Exception as e:
        logger.error(f"Ошибка проверки Redis: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка проверки Redis: {str(e)}"
        )
    try:
        task = rebuild_pagination_task.apply_async()
        logger.info("Ручной запуск rebuild-pagination-v1 успешно поставлен в очередь")
        return {
            "status": "success",
            "task_id": task.id,
            "message": "Задача успешно поставлена в очередь"
        }
    except Exception as e:
        logger.error(f"Ошибка при запуске задачи: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при запуске задачи: {str(e)}"
        )


@app.get("/task-status/{task_id}")
async def get_task_status(task_id: str):
    """Проверка статуса задачи"""
    task = AsyncResult(task_id)

    if task.state == 'FAILURE':
        return {
            "status": "failed",
            "error": str(task.result)
        }

    return {
        "status": task.state,
        "result": task.result,
        "ready": task.ready()
    }