from sqladmin import ModelView
from models.vv1 import Vv1

class Vv1Admin(ModelView, model=Vv1):
    Car = Vv1
    column_list = [Car.vin, Car.views]
    column_searchable_list = [Car.vin,  Car.views]