from django.contrib import admin
from .models import *


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'username', 'role', 'is_active', 'is_staff', 'created_at')
    search_fields = ('email', 'username')
    ordering = ('email',)


admin.site.register(Report)
admin.site.register(Alert)
admin.site.register(Sensor)
admin.site.register(RadiationData)
admin.site.register(Location)
