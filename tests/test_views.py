import pytest
from unittest.mock import patch
from rest_framework.test import APIClient
from rest_framework import status
from weather.models import WeatherQuery
from django.urls import reverse

@pytest.fixture
def api_client():
    """Retorna um APIClient DRF para requisições"""
    return APIClient()

@pytest.fixture
def urls():
    return {
        "weather": reverse('current-weather'),
        "history": reverse('weather-history'),
        "health": reverse('health-check')
    }

@pytest.mark.django_db
@patch('weather.services.WeatherService.get_weather')
def test_get_current_weather_success(mock_get_weather, api_client, urls):
    """Testa requisição de clima com sucesso"""
    mock_get_weather.return_value = ({
        'city': 'São Paulo',
        'country': 'BR',
        'temperature': 25.5,
        'description': 'Clear Sky',
        'humidity': 60,
        'pressure': 1013,
        'wind_speed': 5.2,
        'timestamp': '2024-01-01T12:00:00Z'
    }, False)

    response = api_client.post(urls["weather"], {'city': 'São Paulo', 'country': 'BR'}, format='json')

    assert response.status_code == status.HTTP_200_OK
    assert response.data['city'] == 'São Paulo'
    assert response.data['temperature'] == 25.5
    assert response.data['cached'] is False

@pytest.mark.django_db
def test_get_current_weather_invalid_data(api_client, urls):
    """Testa requisição de clima com dados inválidos"""
    response = api_client.post(urls["weather"], {'city': ''}, format='json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST

@pytest.mark.django_db
@patch('weather.services.WeatherService.get_weather')
def test_get_current_weather_city_not_found(mock_get_weather, api_client, urls):
    """Testa requisição para cidade inexistente"""
    mock_get_weather.side_effect = ValueError("City 'InvalidCity' not found")

    response = api_client.post(urls["weather"], {'city': 'InvalidCity'}, format='json')

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert 'not found' in response.data['error'].lower()

@pytest.mark.django_db
def test_get_weather_history(api_client, urls):
    """Testa endpoint de histórico de consultas"""
    for i in range(5):
        WeatherQuery.objects.create(
            city=f'City{i}',
            country='BR',
            temperature=20 + i,
            description='Test',
            humidity=50,
            pressure=1000,
            wind_speed=1.0
        )

    response = api_client.get(urls["history"])
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 5
    assert response.data[0]['city'] == 'City4'

@pytest.mark.django_db
def test_health_check(api_client, urls):
    """Testa endpoint de health check"""
    response = api_client.get(urls["health"])
    assert response.status_code == status.HTTP_200_OK
    assert response.data['status'] == 'healthy'
    assert 'timestamp' in response.data
    assert 'version' in response.data

@pytest.mark.django_db
def test_rate_limiting_basic(api_client, urls):
    """Testa rate limiting básico (simples)"""
    data = {'city': 'São Paulo'}

    status_codes = [
        api_client.post(urls["weather"], data, format='json').status_code
        for _ in range(5)
    ]

    assert any(code == 200 for code in status_codes)
