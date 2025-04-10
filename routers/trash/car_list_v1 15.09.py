from fastapi import APIRouter, Depends
import database
from models.car import Car
#from models.recent_vin import RecentVin
import random
from tools import Tools
from sqlmodel import text

from models.view import View
from models.recent import Recent

#from models.car_views_v import CarViewsV

from sqlalchemy import update


from models.car_v import CarV

from models.car_vc import CarVc
from models.car_rc import CarRc

from sqlmodel import select


router = APIRouter(
    prefix="/v1/carlist",
    tags=["items"],
    responses={404: {"description": "Not found"}},
)



@router.get("/")
def get_all_items(page: int = 1, per_page: int = 10, session: database.Session = Depends(database.get_session)):

    query = session.query(Car).filter(Car.is_hidden == False)

    total_items = query.count()

    query = query.order_by(Car.id.desc())

    query = query.limit(per_page).offset((page - 1) * per_page)
    res = session.execute(query)
    items = res.scalars().all()


    for item in items:
        item.photo = [photo.replace('{', '').replace('}', '').strip() for photo in item.photo.split(',')] if item.photo else []

    return {
        "count": total_items,
        "next": f"/?page={page + 1}&per_page={per_page}" if total_items > 1 else None,
        "previous": f"/?page={page - 1}&per_page={per_page}" if page > 1 else None,
        "results": items
    }

@router.get("/viewed/")
def get_viewed(page: int = 1, per_page: int = 10, session: database.Session = Depends(database.get_session)):

    query = session.query(CarVc).filter(CarVc.is_hidden == False, CarVc.apiv1 == True)

    total_items = query.count()

    query = query.order_by(CarVc.views.desc())

    query = query.limit(per_page).offset((page - 1) * per_page)
    res = session.execute(query)
    items = res.scalars().all()

    #session.query(CarVc).delete()
    #session.commit()


    for item in items:
        item.photo = [photo.replace('{', '').replace('}', '').replace('"', '').replace('\"', '').strip() for photo in item.photo.split(',')] if item.photo else []
    
    return {
        "count": total_items,
        "next": f"/?page={page + 1}&per_page={per_page}" if total_items > 1 else None,
        "previous": f"/?page={page - 1}&per_page={per_page}" if page > 1 else None,
        "results": items
    }

@router.get("/models/{brand}")
def get_models_by_brand(brand: str, page: int = 1, per_page: int = 10, session: database.Session = Depends(database.get_session)):

    query = session.query(Car.model).filter(Car.brand == brand.upper(), Car.is_hidden == False)

    total_items = query.count()
    query = query.order_by(Car.id.desc())

    items = query.limit(per_page).offset((page - 1) * per_page).all()

    #for item in items:
        #item.photo = [photo.replace('{', '').replace('}', '').strip() for photo in item.photo.split(',')] if item.photo else []

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

    newmodels = list(set(newmodels))

    return {
        "count": total_items,
        "next": f"/?page={page + 1}&per_page={per_page}" if total_items > 1 else None,
        "previous": f"/?page={page - 1}&per_page={per_page}" if page > 1 else None,
        "results": newmodels
    }

@router.get("/recent/")
def get_20_recent(session: database.Session = Depends(database.get_session)):

    
    query = session.query(CarRc).filter(CarRc.is_hidden == False, CarRc.apiv1 == True)




    total_items = query.count()
    query = query.order_by(CarRc.id.desc())

    items = query.limit(50).offset(0).all()


    session.flush()

    session.query(CarRc).filter(CarRc.id <= int(items[-1].id)-1, CarRc.apiv1 == True).delete()
    session.commit()

    #session.flush()

    query = session.query(CarRc).filter(CarRc.is_hidden == False, CarRc.apiv1 == True)




    query = query.order_by(CarRc.id.desc())

    items = query.limit(50).offset(0).all()

    total_items = query.count()


    for item in items:
        item.photo = [photo.replace('{', '').replace('}', '').replace('"', '').replace('\"', '').strip() for photo in item.photo.split(',')] if item.photo else []

    return {
        "count": total_items,
        "results": items
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


@router.get("/{brand}/")
def get_brand(brand: str, page: int = 1, per_page: int = 10, session: database.Session = Depends(database.get_session)):

    query = session.query(Car).filter(Car.brand == brand.upper(), Car.is_hidden == False)

    total_items = query.count()
    query = query.order_by(Car.id.desc())

    items = query.limit(per_page).offset((page - 1) * per_page).all()

    for item in items:
        item.photo = [photo.replace('{', '').replace('}', '').strip() for photo in item.photo.split(',')] if item.photo else []
        try:
            item.model = item.model.split('/')[0]
        except:
            pass

    return {
        "count": total_items,
        "next": f"/?page={page + 1}&per_page={per_page}" if total_items > 1 else None,
        "previous": f"/?page={page - 1}&per_page={per_page}" if page > 1 else None,
        "results": items
    }

@router.post("/add_view/{vin}/")
def add_view(vin: str, session: database.Session = Depends(database.get_session)):
    car = session.exec(select(Car).where(Car.vin == vin.upper(), Car.is_hidden == False)).first()
    session.flush()
    session.commit()

    cardata = car
    if car:
        inview = session.exec(select(CarVc).where(CarVc.vin == vin.upper())).first()
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

        return {
            "success": True
        }
    else:
        return {
            "success": False
        }

@router.post("/add_recent/{vin}/")
def add_recent(vin: str, session: database.Session = Depends(database.get_session)):
    #car = session.query(Car).filter(Car.vin == vin.upper(), Car.is_hidden == False) #if is hidden/ don't show in api request (v1 or v2) ---
    car = session.exec(select(Car).where(Car.vin == vin.upper(), Car.is_hidden == False)).first()
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

        return {
            "success": True
        }
    else:
        return {
            "success": False
        }




@router.get("/{brand}/{model}/")
def get_model(brand: str, model: str, page: int = 1, per_page: int = 10, session: database.Session = Depends(database.get_session)):
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
    
    if False and vin != 'favicon.ico': #turn #collecting views
        #car = session.query(Car).filter(Car.vin == vin.upper(), Car.is_hidden == False) #if is hidden/ don't show in api request (v1 or v2) ---
        car = session.exec(select(Car).where(Car.vin == vin.upper(), Car.is_hidden == False)).first()
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
                inview = session.exec(select(CarVc).where(CarVc.vin == vin.upper())).first()
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
    return {
        "count": total_items,
        "next": f"/?page={page + 1}&per_page={per_page}" if total_items > 1 else None,
        "previous": f"/?page={page - 1}&per_page={per_page}" if page > 1 else None,
        "results": items
    }
