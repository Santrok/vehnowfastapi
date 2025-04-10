from sqladmin import ModelView
from models.car_vv import CarVv

class CarVvAdmin(ModelView, model=CarVv):
    column_list = [CarVv.brand, CarVv.model, CarVv.vin, CarVv.views, CarVv.is_hidden, CarVv.is_hidden_v2]
    column_searchable_list = [CarVv.brand, CarVv.model, CarVv.vin, CarVv.views, CarVv.is_hidden, CarVv.is_hidden_v2]
