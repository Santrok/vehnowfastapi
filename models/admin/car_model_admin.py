from sqladmin import ModelView
from models.car_model import CarModel

class CarModelAdmin(ModelView, model=CarModel):
    column_list = [CarModel.name]
    column_searchable_list = [CarModel.name]