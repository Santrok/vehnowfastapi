from sqlmodel import Session, create_engine, SQLModel
import settings
from models.car_model import CarModel
from models.car import Car

from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from typing import Union, Callable

#from models.view import View #new table
#from models.recent_vin import RecentVin
#from models.all_vin import AllVin
#from models.recent import Recent

#from models.car_views_v import CarViewsV
#from models.car_views_vv import CarViewsVv
#from models.car_vv import CarVv
#from models.car_v import CarV

#from models.car_rc import CarRc
#from models.car_vc import CarVc
#from models.vv import Vv
#from models.vv1 import Vv1
#from models.vv2 import Vv2

import time

#import logging
#logging.basicConfig()
#logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

engine = create_engine(settings.DATABASE_PATH, pool_size=10000, max_overflow=1000)




#Vv2.metadata.create_all(engine) #new table
#Recent.metadata.create_all(engine)
#AllVin.metadata.create_all(engine)

#CarVc.metadata.create_all(engine)
#CarRc.metadata.create_all(engine)

#Vv.metadata.create_all(engine)
#CarV.metadata.create_all(engine)
#CarVv.metadata.create_all(engine)

#print('here')

# CarModel.metadata.create_all(engine)
'''
def get_session():
    with Session(engine) as session:
        yield session
'''
SessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine, expire_on_commit=False
)
def get_session():
    try:
        session = SessionLocal()
        yield session
    finally:
        session.close()

# Для Celery задач (обычная функция)
def get_db_session() -> Session:
    """Создает и возвращает новую сессию для Celery.
    Важно всегда закрывать вручную."""
    return SessionLocal()
'''
SessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine, expire_on_commit=False
)

def get_session(scope_func: Union[Callable, None] = None):
    with scoped_session(SessionLocal, scopefunc=scope_func) as session:
        yield session
'''
# with Session(engine) as session:
#     for i in range(0, 5):
#         start = time.time()
#         query = session.query(Car).filter(Car.brand == "JEEP")

#         total_items = query.count()
#         total_pages = (total_items - 1) // 10 + 1

#         items = query.limit(10).offset((1 - 1) * 10).all()

#         print(time.time() - start)

"""def x(from_x, to_x):
    with Session(engine) as session:
        for i in range(0, 5000):
            car = Car()
            car.year = 1995+1
            car.brand = f"mazda {i}"
            car.model = f"Model {i}"
            car.vin = f"hello {i}"
            car.odometer = f"odomert {i}"
            car.engine = f"engine {i}"
            car.gearbox = f"gearbox {i}"
            car.drive_train = f"automatic {i}"
            car.auction_date = f"12.05.202{i}"
            car.sale_type = f"sale type {i}"
            car.damage = f"{i}0%"
            car.photo = [f"can be a photo {i}"]
            car.is_hidden = False
            session.add(car)
            print(i)
        session.commit()
        print("commited")

x(5, 10)"""
