from fastapi import APIRouter, Depends, Query, Path, HTTPException
import database
from logger import logger
from models.car import Car
#from models.recent_vin import RecentVin
import random

from models.pagination import AllCarPagination, BrandCarPagination
from tools import Tools
from sqlmodel import text

from models.view import View
from models.recent import Recent

#from models.car_views_v import CarViewsV

from sqlalchemy import update, desc

from models.car_v import CarV

from models.car_vc import CarVc
from models.car_rc import CarRc

from models.vv1 import Vv1
from models.vv2 import Vv2

from sqlmodel import select
from sqlalchemy.orm import aliased
from sqlalchemy import func

from sqlalchemy import and_
from sqlalchemy import or_

import time


router = APIRouter(
    prefix="/v1/carlist",
    tags=["items"],
    responses={404: {"description": "Not found"}},
)



@router.get(
    "/",
    response_model=dict,
    summary="Получить автомобили постранично",
    description="""
    Получает список автомобилей для указанной страницы.
    Использует предварительно сгенерированную пагинацию через таблицу AllCarPagination.
    """,
    responses={
        200: {
            "description": "Успешный ответ",
            "content": {
                "application/json": {
                    "example": {
                        "count": 100,
                        "next": "/?page=2&per_page=10",
                        "previous": None,
                        "results": [
                            {
                                "id": "int",
                                "year": "int",
                                "brand": "str",
                                "model": "str",
                                "vin": "str",
                                "odometer": "str",
                                "engine": "str",
                                "gearbox": "str",
                                "drive_train": "str",
                                "auction_date": "str",
                                "sale_type": "str",
                                "damage": "str",
                                "photo": ["str", "str"],
                                "is_hidden": "bool",
                                "is_hidden_v2": "bool",
                                "brand_id": "int"
                            }
                        ]
                    }
                }
            }
        },
        500: {
            "description": "Ошибка сервера",
            "content": {
                "application/json": {
                    "example": {"detail": "Internal Server Error"}
                }
            }
        }
    }
)
def get_all_items(
        page: int = Query(1, description="Номер страницы", ge=1),
        per_page: int = Query(10, description="Элементов на странице", ge=1, le=100),
        session: database.Session = Depends(database.get_session)
) -> dict:
    """
    Получение пагинированного списка автомобилей

    Args:
        page: Номер запрашиваемой страницы
        per_page: Количество элементов на странице
        session: Сессия базы данных

    Returns:
        Словарь с результатами и метаданными пагинации
    """
    try:
        # Получение ID автомобилей для страницы
        page_data = session.query(AllCarPagination) \
            .filter(AllCarPagination.page == page) \
            .first()

        if not page_data or not page_data.car_ids:
            return {
                "count": 0,
                "next": None,
                "previous": None,
                "results": []
            }

        # Получение автомобилей
        cars = session.query(Car) \
            .filter(
            Car.id.in_(page_data.car_ids),
            Car.is_hidden == False
        ) \
            .order_by(desc(Car.id)) \
            .all()

        # Обработка фото
        for car in cars:
            if car.photo:
                car.photo = [
                    photo.strip('{}').strip()
                    for photo in car.photo.split(',')
                ]

        # Получение общего количества страниц
        total_pages = session.query(func.max(AllCarPagination.page)).scalar()

        return {
            "count": len(cars),
            'total_pages': total_pages,
            "next": f"/?page={page + 1}&per_page={per_page}" if page < total_pages else None,
            "previous": f"/?page={page - 1}&per_page={per_page}" if page > 1 else None,
            "results": cars
        }

    except Exception as e:
        print(f"Ошибка: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Internal Server Error"
        )

@router.get("/l/")
def get_all_items_l(page: int = 1, per_page: int = 10, session: database.Session = Depends(database.get_session)):
    start = time.time()
    query = session.query(Car.vin, Car.brand, Car.model, Car.photo).filter(Car.is_hidden == False)

    total_items = query.count()

    #query = query.order_by(Car.id.desc())

    items = query.order_by(Car.id.desc()).limit(per_page).offset((page - 1) * per_page).all()
    #res = session.execute(query)
    #items = res.scalars().all()
    #items = query.all()

    itemsresult = []
    for item in items:
        newitem = dict(item)
        newitem['photo'] = newitem['photo'].split(',')[0].replace('{', '').replace('}', '').strip()
        itemsresult.append(newitem)
        #item.photo = [photo.replace('{', '').replace('}', '').strip() for photo in item.photo.split(',')] if item.photo else []
    end = time.time()
    return {
        "count": total_items,
        "next": f"/?page={page + 1}&per_page={per_page}" if total_items > 1 else None,
        "previous": f"/?page={page - 1}&per_page={per_page}" if page > 1 else None,
        "results": itemsresult,
        'execution_time': str(end-start)
    }

@router.get("/search2/{vin}")
def get_search2(vin: str, page: int = 1, per_page: int = 10, session: database.Session = Depends(database.get_session)):
    #print('log info', flush=True)
    start = time.time()

    #M = aliased(Car, name='M')
    #B = aliased(Car, name='B')
    #C = aliased(Car, name='C')

    if 'FAVICON.ICO' == vin.upper():
        return {'facivon.ico':'favicon.ico'}

    query = session.query(Car).filter(Car.vin == vin.upper(), Car.is_hidden == False)

    #total_items = query.count()

    #query = query.order_by(Car.id.desc())

    items = query.limit(1).offset(0).all()

    if len(items) >= 1:

        for item in items:
            item.photo = [photo.replace('{', '').replace('}', '').replace('"', '').replace('\"', '').replace(']', '').replace('[','').replace("'","").strip() for photo in str(item.photo).split(',')] if item.photo else []

        if len(items) > 1:
            items = items[0]

        total_items = len(items)

        #session.commit()


        sub_query_model = session.query(Car.model).filter(Car.vin == vin.upper(), Car.is_hidden == False).scalar_subquery()

        query_model = session.query(Car).filter(Car.model == sub_query_model, Car.is_hidden == False)

        #query_model_count = session.query(Car).filter(Car.model == sub_query_model, Car.is_hidden == False).count()

        #query_model = query_model.order_by(Car.id.desc())

        items_model = query_model.order_by(Car.id.desc()).limit(per_page).offset((page - 1) * per_page).all()

        for item in items_model:
            if type(item.photo) is tuple or list:
                item.photo = [photo.replace('{', '').replace('}', '').replace('"', '').replace('\"', '').replace(']', '').replace('[','').replace("'","").strip() for photo in str(item.photo).split(',')] if item.photo else []
            else:
                item.photo = [photo.replace('{', '').replace('}', '').replace('"', '').replace('\"', '').replace(']', '').replace('[','').replace("'","").strip() for photo in item.photo.split(',')] if item.photo else []

        sub_query_brand = session.query(Car.brand).filter(Car.vin == vin.upper(), Car.is_hidden == False).scalar_subquery()

        query_brand = session.query(Car).filter(Car.brand == sub_query_brand, Car.is_hidden == False)

        #query_brand_count = session.query(Car).filter(Car.brand == sub_query_brand, Car.is_hidden == False).count()

        #query_brand = query_brand.order_by(Car.id.desc())

        items_brand = query_brand.order_by(Car.id.desc()).limit(per_page).offset((page - 1) * per_page).all()

        for item in items_brand:
            if type(item.photo) is tuple or list:
                item.photo = [photo.replace('{', '').replace('}', '').replace('"', '').replace('\"', '').replace(']', '').replace('[','').replace("'","").strip() for photo in str(item.photo).split(',')] if item.photo else []
            else:
                item.photo = [photo.replace('{', '').replace('}', '').replace('"', '').replace('\"', '').replace(']', '').replace('[','').replace("'","").strip() for photo in item.photo.split(',')] if item.photo else []

        #session.commit()
        end = time.time()

        return {
            "count": total_items,
            "result": items,
            "count_model": query_model.with_entities(func.count()).scalar(),
            'result_model': items_model,
            'count_brand': query_brand.with_entities(func.count()).scalar(),
            'result_brand': items_brand,
            'execution_time': str(end-start)
        }
    else:
        return {'404': []}


@router.get("/viewed/")
def get_viewed(page: int = 1, per_page: int = 10, session: database.Session = Depends(database.get_session)):
    start = time.time()
    query = session.query(CarVc).filter(CarVc.is_hidden == False, CarVc.apiv1 == True)

    #total_items = query.count()
    #total_items = 100
    total_items = query.with_entities(func.count()).scalar()

    #query = query.order_by(CarVc.views.desc())

    query_ = query.order_by(CarVc.views.desc()).limit(per_page).offset((page - 1) * per_page)
    #res = session.execute(query_)
    #items = res.scalars().all()
    items = query_.all()

    #session.query(CarVc).delete()
    #session.commit()


    for item in items:
        item.photo = [photo.replace('{', '').replace('}', '').replace('"', '').replace('\"', '').strip() for photo in item.photo.split(',')] if item.photo else []
    end = time.time()
    return {
        "count": total_items,
        "next": f"/?page={page + 1}&per_page={per_page}" if total_items > 1 else None,
        "previous": f"/?page={page - 1}&per_page={per_page}" if page > 1 else None,
        "results": items,
        'execution_time': str(end-start)

    }

@router.get("/viewed2_v2/")
def get_viewed_v2(page: int = 1, per_page: int = 10, session: database.Session = Depends(database.get_session)):
    start = time.time()
    query = session.query(Vv2)

    total_items = query.count()
    #total_items = 100
    #total_items = query.with_entities(func.count()).scalar()

    #query = query.order_by(CarVc.views.desc())

    query_ = query.order_by(Vv2.views.desc()).limit(per_page).offset((page - 1) * per_page)
    #res = session.execute(query_)
    #items = res.scalars().all()
    items = query_.all()
    #session.flush()
    #session.query(CarVc).delete()
    #session.commit()


    #for item in items:
        #item.photo = [photo.replace('{', '').replace('}', '').replace('"', '').replace('\"', '').strip() for photo in item.photo.split(',')] if item.photo else []

    filter_data = set()

    littledata = {}
    for item in items:
        littledata.update({str(item.vin): int(item.views)})
        filter_data.add(Car.vin == str(item.vin))

    #filter_data = {'vin': value for value in filter_data if value}

    queryincar = session.query(Car).filter(or_(*filter_data))

    items2 = queryincar.all()
    for item in items2:
        item.photo = [photo.replace('{', '').replace('}', '').replace('"', '').replace('\"', '').strip() for photo in item.photo.split(',')] if item.photo else []

    itemsdata = items2
    resultitems = []
    for item in itemsdata:
        item = dict(item)
        if item['vin'] in littledata:
            item.update({'views': littledata[item['vin']]})
        resultitems.append(item)

    end = time.time()
    return {
        "count": total_items,
        "next": f"/?page={page + 1}&per_page={per_page}" if total_items > 1 else None,
        "previous": f"/?page={page - 1}&per_page={per_page}" if page > 1 else None,
        "results":  sorted(resultitems, key=lambda x: x['views'], reverse=True),
        #"views": littledata,
        'execution_time': str(end-start)

    }

@router.get("/viewed2/")
def get_viewed(page: int = 1, per_page: int = 10, session: database.Session = Depends(database.get_session)):
    start = time.time()
    query = session.query(Vv1)

    total_items = query.count()
    #total_items = 100
    #total_items = query.with_entities(func.count()).scalar()

    #query = query.order_by(CarVc.views.desc())

    query_ = query.order_by(Vv1.views.desc()).limit(per_page).offset((page - 1) * per_page)
    #res = session.execute(query_)
    #items = res.scalars().all()
    items = query_.all()
    #session.flush()
    #session.query(CarVc).delete()
    #session.commit()


    #for item in items:
        #item.photo = [photo.replace('{', '').replace('}', '').replace('"', '').replace('\"', '').strip() for photo in item.photo.split(',')] if item.photo else []

    filter_data = set()

    littledata = {}
    for item in items:
        littledata.update({str(item.vin): int(item.views)})
        filter_data.add(Car.vin == str(item.vin))

    #filter_data = {'vin': value for value in filter_data if value}

    queryincar = session.query(Car).filter(or_(*filter_data))

    items2 = queryincar.all()
    for item in items2:
        item.photo = [photo.replace('{', '').replace('}', '').replace('"', '').replace('\"', '').strip() for photo in item.photo.split(',')] if item.photo else []

    itemsdata = items2
    resultitems = []
    for item in itemsdata:
        item = dict(item)
        if item['vin'] in littledata:
            item.update({'views': littledata[item['vin']]})
        resultitems.append(item)

    end = time.time()
    return {
        "count": total_items,
        "next": f"/?page={page + 1}&per_page={per_page}" if total_items > 1 else None,
        "previous": f"/?page={page - 1}&per_page={per_page}" if page > 1 else None,
        "results":  sorted(resultitems, key=lambda x: x['views'], reverse=True),
        #"views": littledata,
        'execution_time': str(end-start)

    }

@router.get("/viewed2_l/")
def get_viewed_l(page: int = 1, per_page: int = 10, session: database.Session = Depends(database.get_session)):
    start = time.time()
    query = session.query(Vv1)

    total_items = query.count()
    #total_items = 100
    #total_items = query.with_entities(func.count()).scalar()

    #query = query.order_by(CarVc.views.desc())

    query_ = query.order_by(Vv1.views.desc()).limit(per_page).offset((page - 1) * per_page)
    #res = session.execute(query_)
    #items = res.scalars().all()
    items = query_.all()
    #session.flush()
    #session.query(CarVc).delete()
    #session.commit()


    #for item in items:
        #item.photo = [photo.replace('{', '').replace('}', '').replace('"', '').replace('\"', '').strip() for photo in item.photo.split(',')] if item.photo else []

    filter_data = set()

    littledata = {}
    for item in items:
        littledata.update({str(item.vin): int(item.views)})
        filter_data.add(Car.vin == str(item.vin))

    #filter_data = {'vin': value for value in filter_data if value}

    queryincar = session.query(Car).filter(or_(*filter_data))

    items2 = queryincar.all()
    for item in items2:
        item.photo = [photo.replace('{', '').replace('}', '').replace('"', '').replace('\"', '').strip() for photo in item.photo.split(',')] if item.photo else []

    itemsdata = items2
    resultitems = []
    for item in itemsdata:
        item = dict(item)
        if item['vin'] in littledata:
            item.update({'views': littledata[item['vin']]})
        resultitems.append(item)

    end = time.time()
    return {
        "count": total_items,
        "next": f"/?page={page + 1}&per_page={per_page}" if total_items > 1 else None,
        "previous": f"/?page={page - 1}&per_page={per_page}" if page > 1 else None,
        "results":  sorted(resultitems, key=lambda x: x['views'], reverse=True),
        #"views": littledata,
        'execution_time': str(end-start)

    }

@router.get("/models/{brand}")
def get_models_by_brand(brand: str, page: int = 1, per_page: int = 10, session: database.Session = Depends(database.get_session)):
    #brand = brand.replace('%2F', '/').replace('%20', ' ')
    query = session.query(Car.model).filter(Car.brand == brand.upper(), Car.is_hidden == False)

    total_items = query.count()
    query = query.order_by(Car.id.desc())

    #items = query.limit(per_page).offset((page - 1) * per_page).all()
    items = query.all()

    #for item in items:
        #item.photo = [photo.replace('{', '').replace('}', '').strip() for photo in item.photo.split(',')] if item.photo else []

    newmodels = []

    for item in items:
        newmodels.append(str(item.model))
        #try:
        #    doublein = str(item.model).split(' ')[0]
        #    nextin = str(item.model).split(' ', 1)[1]
        #    if doublein in nextin:
        #        newmodels.append(str(nextin))
        #    else:
        #        newmodels.append(str(item.model))
        #except:
        #    newmodels.append(str(item.model))

    newmodels = list(set(newmodels))

    return {
        "count": total_items,
        "next": f"/?page={page + 1}&per_page={per_page}" if total_items > 1 else None,
        "previous": f"/?page={page - 1}&per_page={per_page}" if page > 1 else None,
        "results": newmodels
    }

@router.get("/recent/")
def get_20_recent(session: database.Session = Depends(database.get_session)):
    start = time.time()

    query = session.query(CarRc.id).filter(CarRc.is_hidden == False, CarRc.apiv1 == True)




    #total_items = query.count()
    #query = query.order_by(CarRc.id.desc())

    items = query.order_by(CarRc.id.desc()).limit(1).offset(50).scalar_subquery()


    #session.flush()

    session.query(CarRc).filter(CarRc.id <= items-1, CarRc.apiv1 == True).delete(synchronize_session=False)
    session.commit()

    #session.flush()

    query = session.query(CarRc).filter(CarRc.is_hidden == False, CarRc.apiv1 == True)




    query = query.order_by(CarRc.id.desc())
    items = query.limit(50).offset(0).all()

    #total_items = query.count()


    for item in items:
        item.photo = [photo.replace('{', '').replace('}', '').replace('"', '').replace('\"', '').strip() for photo in item.photo.split(',')] if item.photo else []
    
    end = time.time()

    return {
        "count": query.count(),
        "results": items,
        'execution_time': str(end-start)
    }



@router.get("/all_vin/")
def get_all_vin(page: int = 1, per_page: int = 10, session: database.Session = Depends(database.get_session)):

    query = session.query(Car.vin).filter(Car.is_hidden == False)

    total_items = query.count()

    query = query.order_by(Car.id.desc())

    query = query.limit(per_page).offset((page - 1) * per_page)
    res = session.execute(query)
    items = res.scalars().all()


    #for item in items:
        #item.photo = [photo.replace('{', '').replace('}', '').strip() for photo in item.photo.split(',')] if item.photo else []

    return {
        "count": total_items,
        "next": f"/?page={page + 1}&per_page={per_page}" if total_items > 1 else None,
        "previous": f"/?page={page - 1}&per_page={per_page}" if page > 1 else None,
        "results": items
    }


@router.get("/norecent/")#/recent/
def get_recent(page: int = 1, per_page: int = 10, session: database.Session = Depends(database.get_session)):

    query = session.query(Recent)

    total_items = query.count()

    query = query.order_by(Recent.id.desc())

    query = query.limit(per_page).offset((page - 1) * per_page)
    res = session.execute(query)
    items = res.scalars().all()


    #for item in items:
        #item.photo = [photo.replace('{', '').replace('}', '').strip() for photo in item.photo.split(',')] if item.photo else []

    return {
        "count": total_items,
        "next": f"/?page={page + 1}&per_page={per_page}" if total_items > 1 else None,
        "previous": f"/?page={page - 1}&per_page={per_page}" if page > 1 else None,
        "results": items
    }


@router.get(
    "/{brand}/",
    response_model=dict,
    summary="Получить автомобили бренда постранично",
    description="""
    Получает список автомобилей указанного бренда для конкретной страницы.
    Использует предварительно сгенерированную пагинацию через таблицу BrandCarPagination.
    """,
    responses={
        200: {
            "description": "Успешный ответ",
            "content": {
                "application/json": {
                    "example": {
                        "brand": "Toyota",
                        "current_page": 1,
                        "total_pages": 5,
                        "next": "/Toyota/?page=2&per_page=10",
                        "previous": None,
                        "results": [
                            {
                                "id": "int",
                                "year": "int",
                                "brand": "str",
                                "model": "str",
                                "vin": "str",
                                "odometer": "str",
                                "engine": "str",
                                "gearbox": "str",
                                "drive_train": "str",
                                "auction_date": "str",
                                "sale_type": "str",
                                "damage": "str",
                                "photo": ["str", "str"],
                                "is_hidden": "bool",
                                "is_hidden_v2": "bool",
                                "brand_id": "int"
                            }
                        ]
                    }
                }
            }
        },
        404: {
            "description": "Бренд не найден",
            "content": {
                "application/json": {
                    "example": {"detail": "Данные пагинации для бренда не найдены"}
                }
            }
        },
        500: {
            "description": "Ошибка сервера",
            "content": {
                "application/json": {
                    "example": {"detail": "Internal Server Error"}
                }
            }
        }
    }
)
def get_brand(
        brand: str = Path(..., description="Название бренда", example="Toyota"),
        page: int = Query(1, description="Номер страницы", ge=1),
        per_page: int = Query(10, description="Элементов на странице", ge=1, le=100),
        session: database.Session = Depends(database.get_session)
) -> dict:
    """
    Получение пагинированного списка автомобилей по бренду

    Args:
        brand: Название бренда (из пути URL)
        page: Номер запрашиваемой страницы
        per_page: Количество элементов на странице
        session: Сессия базы данных

    Returns:
        Словарь с результатами и метаданными пагинации:
        {
            "brand": str,
            "current_page": int,
            "total_pages": int,
            "next": str | None,
            "previous": str | None,
            "results": List[Car]
        }

    Raises:
        HTTPException 404: Если данные пагинации для бренда не найдены
        HTTPException 500: При внутренних ошибках сервера
    """
    try:
        # Получение данных пагинации для бренда
        brand_pagination = session.query(BrandCarPagination) \
            .filter(BrandCarPagination.brand == brand, BrandCarPagination.page_num == page) \
            .first()

        if not brand_pagination:
            raise HTTPException(
                status_code=404,
                detail="Данные пагинации для бренда не найдены"
            )

        # Получение ID автомобилей для запрошенной страницы
        page_ids = brand_pagination.car_ids

        # Получение автомобилей
        items = session.query(Car) \
            .filter(
            Car.id.in_(page_ids),
            Car.is_hidden == False
        ) \
            .order_by(desc(Car.id)) \
            .all()

        # Обработка фото
        for car in items:
            if car.photo:
                car.photo = [
                    photo.strip('{}').strip()
                    for photo in car.photo.split(',')
                ]

        # Получение общего количества страниц
        total_pages = session.query(func.count(BrandCarPagination.page_num)) \
            .filter(BrandCarPagination.brand == brand) \
            .scalar()

        return {
            "brand": brand_pagination.brand,
            "current_page": page,
            "total_pages": total_pages,
            "next": f"/{brand}/?page={page + 1}&per_page={per_page}" if page < total_pages else None,
            "previous": f"/{brand}/?page={page - 1}&per_page={per_page}" if page > 1 else None,
            "results": items
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка при получении данных бренда: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Internal Server Error"
        )

@router.post("/add_view/{vin}/")
def add_view(vin: str, session: database.Session = Depends(database.get_session)):
    #return {'success': None}

    start = time.time()

    query = session.query(Car).filter(Car.vin == vin.upper(), Car.is_hidden == False)


    items = query.limit(1).offset(0).all()

    cardata = items[0]

    if len(items) >= 1:

        query = session.query(Vv1).filter(Vv1.vin == vin.upper())



        items = query.limit(1).offset(0).all()



        if len(items) == 0:

            vv1 = Vv1(vin=cardata.vin) 
            session.add(vv1)
            
            session.commit()
            
            end = time.time()
            return {
                "success_add": True,
                'execution_time': str(end-start)
                #"query": str(q)
            }
        else:
            session.query(Vv1).filter(Vv1.vin == vin.upper()).update({Vv1.views: Vv1.views+1})

            session.commit()

            end = time.time()
            return {
                "success_view": True,
                'execution_time': str(end-start)
                #"query": str(q)
            }
    else:
        end = time.time()
        return {
            "success": False,
            'execution_time': str(end-start)
        }

@router.post("/add_view_v2/{vin}/")
def add_view_v2(vin: str, session: database.Session = Depends(database.get_session)):
    #return {'success': None}

    start = time.time()

    query = session.query(Car).filter(Car.vin == vin.upper(), Car.is_hidden == False)


    items = query.limit(1).offset(0).all()

    cardata = items[0]

    if len(items) >= 1:

        query = session.query(Vv2).filter(Vv2.vin == vin.upper())



        items = query.limit(1).offset(0).all()



        if len(items) == 0:

            vv2 = Vv2(vin=cardata.vin) 
            session.add(vv2)
            
            session.commit()
            
            end = time.time()
            return {
                "success_add": True,
                'execution_time': str(end-start)
                #"query": str(q)
            }
        else:
            session.query(Vv2).filter(Vv2.vin == vin.upper()).update({Vv2.views: Vv2.views+1})

            session.commit()

            end = time.time()
            return {
                "success_view": True,
                'execution_time': str(end-start)
                #"query": str(q)
            }
    else:
        end = time.time()
        return {
            "success": False,
            'execution_time': str(end-start)
        }

@router.post("/add_recent/{vin}/")
def add_recent(vin: str, session: database.Session = Depends(database.get_session)):
    #car = session.query(Car).filter(Car.vin == vin.upper(), Car.is_hidden == False) #if is hidden/ don't show in api request (v1 or v2) ---
    #car = session.execute(select(Car).where(Car.vin == vin.upper(), Car.is_hidden == False)).first()
    #session.flush()
    #session.commit()
    query = session.query(Car).filter(Car.vin == vin.upper(), Car.is_hidden == False)
    #total_items = query.count()
    #query = query.order_by(Car.id.desc())
    items = query.limit(1).offset(0).all()
    #if len(items) >= 1:
    cardata = items[0]
    #cardata = car
    if len(items) >= 1:
        carrc = CarRc(brand=cardata.brand, 
        year=cardata.year,
        model=cardata.model, 
        vin=cardata.vin, 
        odometer=cardata.odometer, 
        engine=cardata.engine, 
        gearbox=cardata.gearbox, 
        drive_train=cardata.drive_train, 
        auction_date=cardata.auction_date, 
        sale_type=cardata.sale_type, 
        damage=cardata.damage, 
        photo=[cardata.photo,]
        ) #don't pass is hidden_v1 bcz already has is_hidden for accessing it in api request for showing, also can be find by apiv1 column
        session.add(carrc)
        #session.flush()
        session.commit()

        return {
            "success": True
        }
    else:
        return {
            "success": False
        }




@router.get("/{brand}/{model}/")
def get_model(brand: str, model: str, page: int = 1, per_page: int = 10, session: database.Session = Depends(database.get_session)):
    #print('model: ' + model)
    #print('brand: ' + brand)
    model = model.replace('_', '/')
    query = session.query(Car).filter(Car.brand == brand.upper(), Car.model == model.upper(), Car.is_hidden == False)

    total_items = query.count()
    query = query.order_by(Car.id.desc())

    items = query.limit(per_page).offset((page - 1) * per_page).all()

    for item in items:
        item.photo = [photo.replace('{', '').replace('}', '').strip() for photo in item.photo.split(',')] if item.photo else []

    return {
        "count": total_items,
        "next": f"/?page={page + 1}&per_page={per_page}" if total_items > 1 else None,
        "previous": f"/?page={page - 1}&per_page={per_page}" if page > 1 else None,
        "results": items
    }

@router.get("/{brand}/{model}/{vin}/")
def get_vin(brand: str, model: str, vin: str, page: int = 1, per_page: int = 10, session: database.Session = Depends(database.get_session)):

    query = session.query(Car).filter(Car.brand == brand.upper(), Car.model == model.upper(), Car.vin == vin.upper(), Car.is_hidden == False)

    total_items = query.count()

    query = query.order_by(Car.id.desc())

    items = query.limit(per_page).offset((page - 1) * per_page).all()

    for item in items:
        item.photo = [photo.replace('{', '').replace('}', '').strip() for photo in item.photo.split(',')] if item.photo else []

    if len(items) > 1:
        items = items[0]

    return {
        "count": total_items,
        "next": f"/?page={page + 1}&per_page={per_page}" if total_items > 1 else None,
        "previous": f"/?page={page - 1}&per_page={per_page}" if page > 1 else None,
        "results": items
    }

def inc(vin: str, session: database.Session = Depends(database.get_session)):
    inview = session.query(CarVc.views).filter(CarVc.vin == vin.upper()).first()
    currentviews = int(inview.views)
    session.query(CarVc).filter(CarVc.vin == vin.upper()).update({'views': currentviews+1}, synchronize_session = False)
    session.flush()
    session.commit()

@router.get("/search/{vin}")
def get_all_vin(vin: str, page: int = 1, per_page: int = 10, session: database.Session = Depends(database.get_session)):
    #start = time.time()
    if False and vin != 'favicon.ico': #turn #collecting views
        #car = session.query(Car).filter(Car.vin == vin.upper(), Car.is_hidden == False) #if is hidden/ don't show in api request (v1 or v2) ---
        car = session.execute(select(Car).where(Car.vin == vin.upper(), Car.is_hidden == False)).first()
        session.flush()
        session.commit()
        cardata = car
        if car:
            carrc = CarRc(brand=cardata.brand, 
            year=cardata.year,
            model=cardata.model, 
            vin=cardata.vin, 
            odometer=cardata.odometer, 
            engine=cardata.engine, 
            gearbox=cardata.gearbox, 
            drive_train=cardata.drive_train, 
            auction_date=cardata.auction_date, 
            sale_type=cardata.sale_type, 
            damage=cardata.damage, 
            photo=[cardata.photo,]
            ) #don't pass is hidden_v1 bcz already has is_hidden for accessing it in api request for showing, also can be find by apiv1 column
            session.add(carrc)
            session.flush()
            session.commit()

            if True:
                #inview = session.query(CarVc).filter(CarVc.vin == vin.upper()).first()
                inview = session.execute(select(CarVc).where(CarVc.vin == vin.upper())).first()
                session.flush()
                session.commit()
                session.expire_all()
                if not inview: #increment
                    carvc = CarVc(brand=cardata.brand, 
                    year=cardata.year,
                    model=cardata.model, 
                    vin=cardata.vin, 
                    odometer=cardata.odometer, 
                    engine=cardata.engine, 
                    gearbox=cardata.gearbox, 
                    drive_train=cardata.drive_train, 
                    auction_date=cardata.auction_date, 
                    sale_type=cardata.sale_type, 
                    damage=cardata.damage, 
                    photo=[cardata.photo,]
                    ) #don't pass is hidden_v1 bcz already has is_hidden for accessing it in api request for showing, also can be find by apiv1 column
                    session.add(carvc)
                    session.flush()
                    session.commit()
                    session.expire_all()
                else:
                    session.query(CarVc).filter(CarVc.vin == vin.upper()).update({'views': CarVc.views+1})
                    session.flush()
                    session.commit()
        #session.close() 
        #session.commit()
        session.expire_all()
        session.expunge_all()

        '''
        if False:
        inview = session.query(CarVc.views).filter(CarVc.vin == vin.upper()).first()
        if inview: #increment
            session.query(CarVc).filter(CarVc.vin == vin.upper()).update({'views': inview.views+1})
            session.commit()
            #session.refresh(CarV)
        else: #add
            cardata = car.first()
            carvc = CarVc(brand=cardata.brand, 
            year=cardata.year,
            model=cardata.model, 
            vin=cardata.vin, 
            odometer=cardata.odometer, 
            engine=cardata.engine, 
            gearbox=cardata.gearbox, 
            drive_train=cardata.drive_train, 
            auction_date=cardata.auction_date, 
            sale_type=cardata.sale_type, 
            damage=cardata.damage, 
            photo=[cardata.photo,]
            ) #don't pass is hidden_v1 bcz already has is_hidden for accessing it in api request for showing, also can be find by apiv1 column
            session.add(carvc)
            session.commit()

        if False:
            if car.count() > 0:
                inview = session.query(CarVc).filter(CarVc.vin == vin.upper()).first()
                if inview: #increment
                    cardata = car.first()
                    carvc = CarVc(brand=cardata.brand, 
                    year=cardata.year,
                    model=cardata.model, 
                    vin=cardata.vin, 
                    odometer=cardata.odometer, 
                    engine=cardata.engine, 
                    gearbox=cardata.gearbox, 
                    drive_train=cardata.drive_train, 
                    auction_date=cardata.auction_date, 
                    sale_type=cardata.sale_type, 
                    damage=cardata.damage, 
                    photo=[cardata.photo,]
                    ) #don't pass is hidden_v1 bcz already has is_hidden for accessing it in api request for showing, also can be find by apiv1 column
                    session.add(carvc)
                    session.commit()
                    #session.refresh(carvc)

            #add to rc
            #print(cardata.photo)
        '''
            
            
            
            #photolist = photolist[-1].replace('\"', '')
            
            #session.refresh(carrc)
            
            #session.query(CarRc).filter(CarRc.id <= carrc.id - 20).delete()
            #session.commit()
            

    '''
    if True and vin != 'favicon.ico': #turn #collecting views #TURNED OFF
        car = session.query(Car).filter(Car.vin == vin.upper(), Car.is_hidden == False) #if is hidden/ don't show in api request (v1 or v2) ---
        if car.count() > 0:                                     #if car is hidden in db it won't add to view and won't increase views

            inview = session.query(CarV).filter(CarV.vin == vin.upper()).first()
            if inview: #increment
                session.query(CarV).filter(CarV.vin == vin.upper()).update({'views': inview.views+1})
                session.commit()
                #session.refresh(CarV)
            else: #add
                cardata = car.first()
                carv = CarV(brand=cardata.brand, model=cardata.model, vin=cardata.vin)
                session.add(carv)
                session.commit()
                session.refresh(carv)


            
            #recent
            recent = Recent(vin=vin)
            session.add(recent)
            session.commit()
            session.refresh(recent)
            #recent

            inview = session.query(View).filter(View.vin == vin.upper()).first()
            if inview: #increment
                session.query(View).filter(View.vin == vin.upper()).update({'views': inview.views+1})
                session.commit()
            else: #add
                view = View(vin=vin)
                session.add(view)
                session.commit()
                session.refresh(view)
            
    '''
    #count views
    #if False:
        #add_to_v_inc(items[0].brand, items[0].model, items[0].vin)



    query = session.query(Car).filter(Car.vin == vin.upper(), Car.is_hidden == False)

    total_items = query.count()

    query = query.order_by(Car.id.desc())

    items = query.limit(per_page).offset((page - 1) * per_page).all()

    for item in items:
        item.photo = [photo.replace('{', '').replace('}', '').strip() for photo in item.photo.split(',')] if item.photo else []

    if len(items) > 1:
        items = items[0]

    total_items = len(items)


    #recent_vin = session.exec(select(RecentVin).where(RecentVin.vin == vin)).first()

    #recent_vin = RecentVin(vin)
    #session.add(recent_vin)
    #session.commit()
    #session.refresh(recent_vin)

    #car_brand = session.exec(select(CarBrand).where(CarBrand.name == brand_name)).first()
    
    #recent_vin = RecentVin(vin=vin)
    #session.add(recent_vin)
    #session.commit()
    #session.refresh(recent_vin)

    #add_to_views_inc(items['brand'], items['model'], items[''])

    #if False:
        #session = add_to_v_inc(session, items[0].brand, items[0].model, items[0].vin)
    '''
    if False:
        inview = session.query(CarV).filter(CarV.vin == vin.upper()).first()
        if inview: #increment
            session.query(CarV).filter(CarV.vin == vin.upper()).update({'views': inview.views+1})
            session.commit()
            #session.refresh(CarV)
        else: #add
            carv = CarV(brand=brand, model=model, vin=vin)
            session.add(carv)
            session.commit()
            #session.refresh(CarV)
    '''
    #end = time.time()
    return {
        "count": total_items,
        "next": f"/?page={page + 1}&per_page={per_page}" if total_items > 1 else None,
        "previous": f"/?page={page - 1}&per_page={per_page}" if page > 1 else None,
        "results": items,
        #"execution_time": str(end-start)
    }
