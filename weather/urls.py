from django.urls import path
from . import views

urlpatterns = [
    path('weather/', views.get_current_weather, name='current-weather'),
    path('weather/history/', views.get_weather_history, name='weather-history'),
    path('health/', views.health_check, name='health-check'),
]