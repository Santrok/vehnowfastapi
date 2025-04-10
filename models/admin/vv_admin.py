from sqladmin import ModelView
from models.vv import Vv

class VvAdmin(ModelView, model=Vv):
    Car = Vv
    column_list = [Car.vin, Car.views, Car.apiv1]
    column_searchable_list = [Car.vin,  Car.views, Car.apiv1]