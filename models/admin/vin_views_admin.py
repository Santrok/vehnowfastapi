from sqladmin import ModelView
from models.vin_views import VinViews

class VinViewsAdmin(ModelView, model=VinViews):
    column_list = [VinViews.vin, VinViews.views]
    column_searchable_list = [VinViews.vin, VinViews.views]