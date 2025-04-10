from sqladmin import ModelView
from models.recent import Recent

class RecentAdmin(ModelView, model=Recent):
    column_list = [Recent.vin]
    column_searchable_list = [Recent.vin]