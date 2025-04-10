from sqladmin import ModelView
from models.recent_vin import RecentVin

class RecentVinAdmin(ModelView, model=RecentVin):
    column_list = [RecentVin.vin]
    column_searchable_list = [RecentVin.vin]