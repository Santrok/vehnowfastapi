from sqladmin import ModelView
from models.car_brand import CarBrand

class CarBrandAdmin(ModelView, model=CarBrand):
    column_list = [CarBrand.name]
    column_searchable_list = [CarBrand.name]