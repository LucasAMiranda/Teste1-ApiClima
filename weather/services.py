import requests
import logging
from typing import Dict, Tuple
from django.conf import settings
from django.core.cache import cache
from .models import WeatherQuery

logger = logging.getLogger('weather')

class WeatherService:
    def __init__(self):
        self.api_key = settings.OPENWEATHER_API_KEY
        self.base_url = settings.OPENWEATHER_BASE_URL
        self.cache_timeout = settings.WEATHER_CACHE_TIMEOUT

    def get_weather(self, city: str, country: str = '', ip_address: str = None) -> Tuple[Dict, bool]:
        """Get weather data for a city with caching"""
        cache_key = self._get_cache_key(city, country)
        
        cached_data = cache.get(cache_key)
        if cached_data:
            logger.info(f"Cache hit for {city}, {country}")
            return cached_data, True

        try:
            weather_data = self._fetch_from_api(city, country)

            weather_query = WeatherQuery.objects.create(
                city=weather_data['city'],
                country=weather_data['country'],
                temperature=weather_data['temperature'],
                description=weather_data['description'],
                humidity=weather_data['humidity'],
                pressure=weather_data['pressure'],
                wind_speed=weather_data['wind_speed'],
                ip_address=ip_address
            )
            
            weather_data['timestamp'] = weather_query.timestamp
            cache.set(cache_key, weather_data, self.cache_timeout)
            
            logger.info(f"API call successful for {city}, {country}")
            return weather_data, False

        except Exception as e:
            logger.error(f"Error fetching weather for {city}, {country}: {str(e)}")
            raise  # Re-raise para que a view possa tratar

    def _fetch_from_api(self, city: str, country: str = '') -> Dict:
        """Fetch weather data from OpenWeatherMap API"""
        if not self.api_key:
            raise ValueError("OpenWeatherMap API key not configured")

        query = city.strip()
        if country:
            query += f",{country.strip()}"

        params = {
            'q': query,
            'appid': self.api_key,
            'units': 'metric'
        }

        response = requests.get(f"{self.base_url}/weather", params=params, timeout=10)

        if response.status_code == 404:
            raise ValueError(f"City '{query}' not found")
        elif response.status_code == 401:
            raise ValueError("Invalid API key")
        elif response.status_code != 200:
            raise ValueError(f"API error: {response.status_code}")

        data = response.json()

        return {
            'city': data['name'],
            'country': data['sys']['country'],
            'temperature': round(data['main']['temp'], 1),
            'description': data['weather'][0]['description'].title(),
            'humidity': data['main']['humidity'],
            'pressure': data['main']['pressure'],
            'wind_speed': round(data.get('wind', {}).get('speed', 0), 1),
        }

    def _get_cache_key(self, city: str, country: str = '') -> str:
        """Generate cache key for city/country combination"""
        key = f"weather:{city.strip().lower()}"
        if country:
            key += f":{country.strip().lower()}"
        return key

    @staticmethod
    def get_query_history(limit: int = 10) -> list:
        """Get recent weather queries"""
        return WeatherQuery.get_recent_queries(limit)
