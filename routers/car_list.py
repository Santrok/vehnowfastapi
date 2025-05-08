from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy import func, desc
import database
from logger import logger

from models.car import Car
import random

from models.pagination import AllCarPagination2, BrandCarPagination2
from tools import Tools
from sqlmodel import text

from models.view import View
# from models.recent import Recent

from models.car_vv import CarVv

from models.car_vc import CarVc
from models.car_rc import CarRc

import time

router = APIRouter(
    prefix="/v2/carlist",
    tags=["items"],
    responses={404: {"description": "Not found"}},
)


@router.post("/add_recent/{vin}/")
def add_recent(vin: str, session: database.Session = Depends(database.get_session)):
    # car = session.query(Car).filter(Car.vin == vin.upper(), Car.is_hidden == False) #if is hidden/ don't show in api request (v1 or v2) ---
    # car = session.execute(select(Car).where(Car.vin == vin.upper(), Car.is_hidden == False)).first()
    # session.flush()
    # session.commit()
    query = session.query(Car).filter(Car.vin == vin.upper(), Car.is_hidden == False)
    # total_items = query.count()
    # query = query.order_by(Car.id.desc())
    items = query.limit(1).offset(0).all()
    # if len(items) >= 1:
    cardata = items[0]
    # cardata = car
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
                      photo=[cardata.photo, ],
                      apiv1=False
                      )  # don't pass is hidden_v1 bcz already has is_hidden for accessing it in api request for showing, also can be find by apiv1 column
        session.add(carrc)
        # session.flush()
        session.commit()

        return {
            "success": True
        }
    else:
        return {
            "success": False
        }

@router.get("/recent/")
def get_20_recent(session: database.Session = Depends(database.get_session)):
    start = time.time()

    query = session.query(CarRc.id).filter(CarRc.is_hidden == False, CarRc.apiv1 == False)

    # total_items = query.count()
    # query = query.order_by(CarRc.id.desc())

    items = query.order_by(CarRc.id.desc()).limit(1).offset(50).scalar_subquery()

    # session.flush()

    session.query(CarRc).filter(CarRc.id <= items - 1, CarRc.apiv1 == True).delete(synchronize_session=False)
    session.commit()

    # session.flush()

    query = session.query(CarRc).filter(CarRc.is_hidden == False, CarRc.apiv1 == False)

    query = query.order_by(CarRc.id.desc())
    items = query.limit(50).offset(0).all()

    # total_items = query.count()

    for item in items:
        item.photo = [photo.replace('{', '').replace('}', '').replace('"', '').replace('\"', '').strip() for photo in
                      item.photo.split(',')] if item.photo else []

    end = time.time()

    return {
        "count": query.count(),
        "results": items,
        'execution_time': str(end - start)
    }


# ---
# query = session.query(CarRc).filter(CarRc.is_hidden == False, CarRc.apiv1 == False)


# total_items = query.count()
# query = query.order_by(CarRc.id.desc())

# items = query.limit(20).offset(0).all()


# # session.flush()

# # #session.flush()

# # session.query(CarRc).filter(CarRc.id <= items[-1].id, CarRc.apiv1 == False).delete()
# # #session.query(CarRc).filter(CarRc.id <= items[-1].id, CarRc.apiv1 == False).delete()
# # session.commit()

# # #session.flush()

# query = session.query(CarRc).filter(CarRc.is_hidden == False, CarRc.apiv1 == False)


# # total_items = query.count()
# # query = query.order_by(CarRc.id.desc())

# items = query.limit(20).offset(0).all()


# for item in items:
#     item.photo = [photo.replace('{', '').replace('}', '').replace('"', '').replace('\"', '').strip() for photo in item.photo.split(',')] if item.photo else []

# return {
#     "count": total_items,
#     "results": items
# }

@router.get("/viewed/")
def get_viewed(page: int = 1, per_page: int = 10, session: database.Session = Depends(database.get_session)):
    query = session.query(CarVc).filter(CarVc.is_hidden == False, CarVc.apiv1 == False)

    total_items = query.count()

    query = query.order_by(CarVc.views.desc())

    query = query.limit(per_page).offset((page - 1) * per_page)
    res = session.execute(query)
    items = res.scalars().all()

    # session.query(CarVc).delete()
    # session.commit()

    for item in items:
        item.photo = [photo.replace('{', '').replace('}', '').replace('"', '').replace('\"', '').strip() for photo in
                      item.photo.split(',')] if item.photo else []

    return {
        "count": total_items,
        "next": f"/?page={page + 1}&per_page={per_page}" if total_items > 1 else None,
        "previous": f"/?page={page - 1}&per_page={per_page}" if page > 1 else None,
        "results": items
    }


@router.get(
    "/",
    response_model=dict,
    summary="Получить автомобили постранично",
    description="""
    Получает список автомобилей для указанной страницы.
    Использует предварительно сгенерированную пагинацию через таблицу AllCarPagination2.
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
        page_data = session.query(AllCarPagination2) \
            .filter(AllCarPagination2.page == page) \
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
            Car.is_hidden_v2 == False
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
        total_pages = session.query(func.max(AllCarPagination2.page)).scalar()

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


@router.get("/all_vin/")
def get_all_vin(page: int = 1, per_page: int = 10, session: database.Session = Depends(database.get_session)):
    query = session.query(Car.vin).filter(Car.is_hidden_v2 == False)

    total_items = query.count()

    query = query.order_by(Car.id.desc())

    query = query.limit(per_page).offset((page - 1) * per_page)
    res = session.execute(query)
    items = res.scalars().all()

    # for item in items:
    # item.photo = [photo.replace('{', '').replace('}', '').strip() for photo in item.photo.split(',')] if item.photo else []

    return {
        "count": total_items,
        "next": f"/?page={page + 1}&per_page={per_page}" if total_items > 1 else None,
        "previous": f"/?page={page - 1}&per_page={per_page}" if page > 1 else None,
        "results": items
    }


@router.get("/views/")
def get_all_views(page: int = 1, per_page: int = 10, session: database.Session = Depends(database.get_session)):
    query = session.query(CarVv).filter(CarVv.is_hidden_v2 == False)

    total_items = query.count()

    query = query.order_by(CarVv.views.desc())

    query = query.limit(per_page).offset((page - 1) * per_page)
    res = session.execute(query)
    items = res.scalars().all()

    # for item in items:
    # item.photo = [photo.replace('{', '').replace('}', '').strip() for photo in item.photo.split(',')] if item.photo else []

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
    Использует предварительно сгенерированную пагинацию через таблицу BrandCarPagination2.
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
        brand_pagination = session.query(BrandCarPagination2) \
            .filter(BrandCarPagination2.brand == brand, BrandCarPagination2.page_num == page) \
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
            Car.is_hidden_v2 == False
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
        total_pages = session.query(func.count(BrandCarPagination2.page_num)) \
            .filter(BrandCarPagination2.brand == brand) \
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


@router.get("/{brand}/{model}/")
def get_model(brand: str, model: str, page: int = 1, per_page: int = 10,
              session: database.Session = Depends(database.get_session)):
    query = session.query(Car).filter(Car.brand == brand.upper(), Car.model == model.upper(), Car.is_hidden_v2 == False)

    total_items = query.count()
    query = query.order_by(Car.id.desc())

    items = query.limit(per_page).offset((page - 1) * per_page).all()

    for item in items:
        item.photo = [photo.replace('{', '').replace('}', '').strip() for photo in
                      item.photo.split(',')] if item.photo else []

    return {
        "count": total_items,
        "next": f"/?page={page + 1}&per_page={per_page}" if total_items > 1 else None,
        "previous": f"/?page={page - 1}&per_page={per_page}" if page > 1 else None,
        "results": items
    }


@router.get("/{brand}/{model}/{vin}/")
def get_vin(brand: str, model: str, vin: str, page: int = 1, per_page: int = 10,
            session: database.Session = Depends(database.get_session)):
    query = session.query(Car).filter(Car.brand == brand.upper(), Car.model == model.upper(), Car.vin == vin.upper(),
                                      Car.is_hidden_v2 == False)

    total_items = query.count()

    query = query.order_by(Car.id.desc())

    items = query.limit(per_page).offset((page - 1) * per_page).all()

    for item in items:
        item.photo = [photo.replace('{', '').replace('}', '').strip() for photo in
                      item.photo.split(',')] if item.photo else []

    if len(items) > 1:
        items = items[0]

    return {
        "count": total_items,
        "next": f"/?page={page + 1}&per_page={per_page}" if total_items > 1 else None,
        "previous": f"/?page={page - 1}&per_page={per_page}" if page > 1 else None,
        "results": items
    }


@router.get("/models/{brand}")
def get_models_by_brand(brand: str, page: int = 1, per_page: int = 10,
                        session: database.Session = Depends(database.get_session)):
    query = session.query(Car.model).filter(Car.brand == brand.upper(), Car.is_hidden_v2 == False)

    total_items = query.count()
    query = query.order_by(Car.id.desc())

    items = query.limit(per_page).offset((page - 1) * per_page).all()

    # for item in items:
    # item.photo = [photo.replace('{', '').replace('}', '').strip() for photo in item.photo.split(',')] if item.photo else []

    newmodels = []

    for item in items:
        try:
            doublein = str(item.model).split(' ')[0]
            nextin = str(item.model).split(' ', 1)[1]
            if doublein in nextin:
                newmodels.append(str(nextin))
            else:
                newmodels.append(str(item.model))
        except:
            newmodels.append(str(item.model))

    return {
        "count": total_items,
        "next": f"/?page={page + 1}&per_page={per_page}" if total_items > 1 else None,
        "previous": f"/?page={page - 1}&per_page={per_page}" if page > 1 else None,
        "results": newmodels
    }


@router.get("/search/{vin}")
def get_all_vin(vin: str, page: int = 1, per_page: int = 10, session: database.Session = Depends(database.get_session)):
    # remove this
    if False and vin != 'favicon.ico':  # turn #collecting views
        car = session.query(Car).filter(Car.vin == vin.upper(),
                                        Car.is_hidden_v2 == False)  # if is hidden/ don't show in api request (v1 or v2) ---
        if car.count() > 0:
            cardata = car.first()
            # print(cardata.photo)
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
                          photo=[cardata.photo, ],
                          apiv1=False
                          )  # don't pass is hidden_v1 bcz already has is_hidden for accessing it in api request for showing, also can be find by apiv1 column
            session.add(carrc)
            session.commit()

            '''
            inview = session.query(CarVc.views).filter(CarVc.vin == vin.upper(), CarVc.apiv1 == False).first()
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
                    photo=[cardata.photo,], 
                    apiv1=False #to mark that it came from api v2, also won't write if is already hidden in table Car
                    ) 
                    #don't pass is hidden_v1 bcz already has is_hidden for accessing it in api request for showing, also can be find by apiv1 column
                session.add(carvc)
                session.commit()

            '''

        '''
        if car.count() > 0:
            inview = session.query(CarVc.views).filter(CarVc.vin == vin.upper(), CarVc.apiv1 == False).first()
            if inview: #increment
                session.query(CarVc.views).filter(CarVc.vin == vin.upper()).update({'views': inview.views+1})
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
                    photo=[cardata.photo,], 
                    apiv1=False #to mark that it came from api v2, also won't write if is already hidden in table Car
                    ) 
                    #don't pass is hidden_v1 bcz already has is_hidden for accessing it in api request for showing, also can be find by apiv1 column
                session.add(carvc)
                session.commit()
                #session.refresh(carvc)
                '''

        # add to rc

        # session.refresh(carrc)

        # session.query(CarRc).filter(CarRc.apiv1 == False, CarRc.id <= carrc.id - 20).delete()
        # session.commit()

    '''
    if False and vin != 'favicon.ico': #turn #TEMPORARY TURNED OFF
        car = session.query(Car).filter(Car.vin == vin.upper(), Car.is_hidden_v2 == False) #if is hidden/ don't show in api request (v1 or v2)
        if car.count() > 0:

            #recent update

            inview = session.query(View).filter(View.vin == vin.upper()).first()
            if inview: #increment
                session.query(View).filter(View.vin == vin.upper()).update({'views': inview.views+1})
                session.commit()
            else: #add
                view = View(vin=vin)
                session.add(view)
                session.commit()
                session.refresh(view)

    
    if True and vin != 'favicon.ico': #turn #collecting views #TURNED OFF
        car = session.query(Car).filter(Car.vin == vin.upper(), Car.is_hidden_v2 == False) #if is hidden/ don't show in api request (v1 or v2) ---
        if car.count() > 0:                                     #if car is hidden in db it won't add to view and won't increase views

            inview = session.query(CarVv).filter(CarVv.vin == vin.upper()).first()
            if inview: #increment
                session.query(CarVv).filter(CarVv.vin == vin.upper()).update({'views': inview.views+1})
                session.commit()
                #session.refresh(CarV)
            else: #add
                cardata = car.first()
                carvv = CarVv(brand=cardata.brand, model=cardata.model, vin=cardata.vin)
                session.add(carvv)
                session.commit()
                session.refresh(carvv)

    '''

    query = session.query(Car).filter(Car.vin == vin.upper(), Car.is_hidden_v2 == False)

    total_items = query.count()

    query = query.order_by(Car.id.desc())

    items = query.limit(per_page).offset((page - 1) * per_page).all()

    for item in items:
        item.photo = [photo.replace('{', '').replace('}', '').strip() for photo in
                      item.photo.split(',')] if item.photo else []

    if len(items) > 1:
        items = items[0]

    total_items = len(items)

    return {
        "count": total_items,
        "next": f"/?page={page + 1}&per_page={per_page}" if total_items > 1 else None,
        "previous": f"/?page={page - 1}&per_page={per_page}" if page > 1 else None,
        "results": items
    }
