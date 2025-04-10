from sqladmin import ModelView
from models.car_vc import CarVc

class CarVcAdmin(ModelView, model=CarVc):
    Car = CarVc
    column_list = [Car.brand, Car.model, Car.year, Car.engine, Car.gearbox, Car.vin, Car.is_hidden, Car.views, Car.apiv1]
    column_searchable_list = [Car.brand, Car.model, Car.year, Car.engine, Car.gearbox, Car.vin, Car.is_hidden, Car.views, Car.apiv1]
