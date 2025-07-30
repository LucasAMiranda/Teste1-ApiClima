import pytest
from unittest.mock import patch, Mock
from django.core.cache import cache
from weather.services import WeatherService
from weather.models import WeatherQuery

@pytest.fixture(autouse=True)
def clear_cache():
    """Limpa o cache antes e depois de cada teste"""
    cache.clear()
    yield
    cache.clear()

@pytest.mark.django_db
@patch('weather.services.requests.get')
def test_fetch_from_api_success(mock_get):
    """Test successful API call"""
    service = WeatherService()

    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        'name': 'São Paulo',
        'sys': {'country': 'BR'},
        'main': {
            'temp': 25.5,
            'humidity': 60,
            'pressure': 1013
        },
        'weather': [{'description': 'clear sky'}],
        'wind': {'speed': 5.2}
    }
    mock_get.return_value = mock_response

    result = service._fetch_from_api('São Paulo', 'BR')

    assert result['city'] == 'São Paulo'
    assert result['country'] == 'BR'
    assert result['temperature'] == 25.5
    assert result['description'] == 'Clear Sky'

@pytest.mark.django_db
@patch('weather.services.requests.get')
def test_fetch_from_api_city_not_found(mock_get):
    """Test API call with city not found"""
    service = WeatherService()
    mock_response = Mock()
    mock_response.status_code = 404
    mock_get.return_value = mock_response

    with pytest.raises(ValueError, match="not found"):
        service._fetch_from_api('InvalidCity')

@pytest.mark.django_db
@patch('weather.services.requests.get')
def test_get_weather_with_cache(mock_get):
    """Test weather retrieval with caching"""
    service = WeatherService()

    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        'name': 'São Paulo',
        'sys': {'country': 'BR'},
        'main': {'temp': 25.5, 'humidity': 60, 'pressure': 1013},
        'weather': [{'description': 'clear sky'}],
        'wind': {'speed': 5.2}
    }
    mock_get.return_value = mock_response

    # First call - hits API
    result1, cached1 = service.get_weather('São Paulo', 'BR')
    assert cached1 is False
    assert mock_get.call_count == 1

    # Second call - hits cache
    result2, cached2 = service.get_weather('São Paulo', 'BR')
    assert cached2 is True
    assert mock_get.call_count == 1  # no extra API call
    assert result1['city'] == result2['city']
    assert result1['temperature'] == result2['temperature']

def test_get_cache_key():
    """Test cache key generation"""
    service = WeatherService()
    key1 = service._get_cache_key('São Paulo', 'BR')
    key2 = service._get_cache_key('são paulo', 'br')
    key3 = service._get_cache_key('São Paulo')

    assert key1 == 'weather:são paulo:br'
    assert key1 == key2  # Case insensitive
    assert key3 == 'weather:são paulo'

@pytest.mark.django_db
def test_get_query_history():
    """Test getting query history"""
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

    history = WeatherService.get_query_history(3)
    assert len(history) == 3
    assert history[0].city == 'City4'  # Most recent first
