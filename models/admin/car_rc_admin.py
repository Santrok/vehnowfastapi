from sqladmin import ModelView
from models.car_rc import CarRc

class CarRcAdmin(ModelView, model=CarRc):
    Car = CarRc
    column_list = [Car.brand, Car.model, Car.year, Car.engine, Car.gearbox, Car.vin, Car.is_hidden, Car.apiv1]
    column_searchable_list = [Car.brand, Car.model, Car.year, Car.engine, Car.gearbox, Car.vin, Car.is_hidden, Car.apiv1]
