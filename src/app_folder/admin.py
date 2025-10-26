from django.contrib import admin

# Register your models here.
from .models import NewsDB
from .models import MallsDB
from .models import StoresDB
from .models import ExecuteLogsDB
from .models import InventoriesDB
from .models import DeliveriesDB

admin.site.register(NewsDB)
admin.site.register(MallsDB)
admin.site.register(StoresDB)
admin.site.register(ExecuteLogsDB)
admin.site.register(InventoriesDB)
admin.site.register(DeliveriesDB)