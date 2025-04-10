from sqladmin import ModelView
from models.view import View

class ViewAdmin(ModelView, model=View):
    column_list = [View.vin, View.views, View.is_hidden, View.is_hidden_v2]
    column_searchable_list = [View.vin, View.views, View.is_hidden, View.is_hidden_v2]