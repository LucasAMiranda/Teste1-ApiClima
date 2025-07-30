import pytest
from weather.models import WeatherQuery

@pytest.mark.django_db
def test_create_weather_query():
    """Test creating a weather query"""
    data = {
        'city': 'São Paulo',
        'country': 'BR',
        'temperature': 25.5,
        'description': 'Clear Sky',
        'humidity': 60,
        'pressure': 1013,
        'wind_speed': 5.2,
        'ip_address': '192.168.1.1'
    }
    query = WeatherQuery.objects.create(**data)

    assert query.city == 'São Paulo'
    assert query.country == 'BR'
    assert query.temperature == 25.5
    assert query.timestamp is not None


@pytest.mark.django_db
def test_string_representation():
    """Test string representation of weather query"""
    query = WeatherQuery.objects.create(
        city='São Paulo',
        country='BR',
        temperature=25.5,
        description='Clear Sky',
        humidity=60,
        pressure=1013,
        wind_speed=5.2,
        ip_address='192.168.1.1'
    )
    expected = f"São Paulo - 25.5°C at {query.timestamp}"
    assert str(query) == expected


@pytest.mark.django_db
def test_get_recent_queries():
    """Test getting recent queries"""
    for i in range(15):
        WeatherQuery.objects.create(
            city=f'City{i}',
            country='BR',
            temperature=20 + i,
            description='Test',
            humidity=50,
            pressure=1000,
            wind_speed=1.0,
            ip_address=f'127.0.0.{i}'
        )

    recent = WeatherQuery.get_recent_queries(10)

    assert len(recent) == 10
    # Deve ser ordenado por timestamp desc
    assert recent[0].city == 'City14'
    assert recent[9].city == 'City5'


@pytest.mark.django_db
def test_cleanup_old_queries():
    """Test cleanup of old queries"""
    for i in range(20):
        WeatherQuery.objects.create(
            city=f'City{i}',
            country='BR',
            temperature=20,
            description='Test',
            humidity=50,
            pressure=1000,
            wind_speed=1.0,
            ip_address=f'127.0.0.{i}'
        )

    assert WeatherQuery.objects.count() == 20

    WeatherQuery.cleanup_old_queries(keep_last=10)

    assert WeatherQuery.objects.count() == 10
