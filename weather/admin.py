from django.contrib import admin
from .models import WeatherQuery

@admin.register(WeatherQuery)
class WeatherQueryAdmin(admin.ModelAdmin):
    list_display = ['city', 'country', 'temperature', 'description', 'timestamp', 'ip_address']
    list_filter = ['country', 'timestamp']
    search_fields = ['city', 'country', 'description']
    readonly_fields = ['timestamp']
    ordering = ['-timestamp']
    
    def has_add_permission(self, request):
        return False  # Prevent manual creation through admin
