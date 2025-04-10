from sqladmin import ModelView
from models.vv2 import Vv2

class Vv2Admin(ModelView, model=Vv2):
    Car = Vv2
    column_list = [Car.vin, Car.views]
    column_searchable_list = [Car.vin,  Car.views]