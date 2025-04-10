from sqladmin import ModelView
from models.car import Car

class CarAdmin(ModelView, model=Car):
    column_list = [Car.brand, Car.model, Car.year, Car.engine, Car.gearbox, Car.vin, Car.is_hidden, Car.is_hidden_v2]
    column_searchable_list = [Car.brand, Car.model, Car.year, Car.engine, Car.gearbox, Car.vin, Car.is_hidden, Car.is_hidden_v2]
