from fastapi import FastAPI
from sqladmin import Admin
from database import engine
import models.admin
from fastapi import FastAPI, Request
import routers
from auth import AdminAuth
import time
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from starlette.middleware.cors import CORSMiddleware

app = FastAPI()
admin = Admin(app, engine, authentication_backend=AdminAuth("7XTW2E5CKm"))
#admin = Admin(app, engine, authentication_backend=AdminAuth())


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://vincheck.by/", 'https://vincheck.by/', 'http://217.197.117.75/'],
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
