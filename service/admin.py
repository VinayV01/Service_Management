from django.contrib import admin

from .models import Services


@admin.register(Services)
class ServicesAdmin(admin.ModelAdmin):
    list_display = ('id', 'service_name', 'price', 'duration', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('service_name',)
