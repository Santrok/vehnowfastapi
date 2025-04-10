from sqladmin import ModelView
from models.car_v import CarV

class CarVAdmin(ModelView, model=CarV):
    column_list = [CarV.brand, CarV.model, CarV.vin, CarV.views, CarV.is_hidden, CarV.is_hidden_v2]
    column_searchable_list = [CarV.brand, CarV.model, CarV.vin, CarV.views, CarV.is_hidden, CarV.is_hidden_v2]
