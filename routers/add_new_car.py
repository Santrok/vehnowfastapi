from fastapi import APIRouter, Depends, HTTPException
import database
from models.car import Car
from models.car_brand import CarBrand
from models.car_model import CarModel
from sqlmodel import select


router = APIRouter(
    prefix="/add",
    tags=["items"],
    responses={404: {"description": "Not found"}},
)

@router.post("/cars")
def add_new_car(car_data: Car, session: database.Session = Depends(database.get_session)):
    try:
        car_data_dict = car_data.dict()
        for key, value in car_data_dict.items():
            if isinstance(value, str):
                car_data_dict[key] = value


        model_name = car_data_dict['model']
        brand_name = car_data_dict['brand']

        car_model = session.query(CarModel).where(CarModel.name == model_name).first()
        if not car_model:
            car_model = CarModel(name=model_name, brand=brand_name)
            session.add(car_model)

        car_brand = session.query(CarBrand).where(CarBrand.name == brand_name).first()
        if not car_brand:
            car_brand = CarBrand(name=brand_name)
            session.add(car_brand)
        car_data_dict["brand_id"] = car_brand.id

        car = session.query(Car).where(Car.vin == car_data_dict['vin']).first()
        if car:
            raise Exception('exists')

        car = Car(**car_data_dict)
        session.add(car)
        session.commit()
        session.refresh(car)
        return car
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=str(e))

