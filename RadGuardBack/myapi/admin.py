from django.contrib import admin
from .models import *
from django.contrib.auth.models import User as use


admin.site.unregister(use)

admin.site.register(User)
admin.site.register(Report)
admin.site.register(Alert)
admin.site.register(Sensor)
admin.site.register(RadiationData)
admin.site.register(Location)