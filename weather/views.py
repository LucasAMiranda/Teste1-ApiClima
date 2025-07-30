from django.shortcuts import render
import logging
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, throttle_classes
from rest_framework.response import Response
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle
from django.views.decorators.cache import never_cache
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .services import WeatherService
from .serializers import (
    WeatherRequestSerializer, 
    WeatherResponseSerializer, 
    WeatherQuerySerializer
)
from .models import WeatherQuery

logger = logging.getLogger('weather')

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

@swagger_auto_schema(
    method='post',
    request_body=WeatherRequestSerializer,
    responses={
        200: WeatherResponseSerializer,
        400: 'Bad Request',
        404: 'City not found',
        429: 'Rate limit exceeded'
    },
    operation_description="Get current weather for a city with 10-minute caching"
)
@api_view(['POST'])
@throttle_classes([AnonRateThrottle, UserRateThrottle])
@never_cache
def get_current_weather(request):
    serializer = WeatherRequestSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    city = serializer.validated_data['city']
    country = serializer.validated_data.get('country', '')
    ip_address = get_client_ip(request)
    
    try:
        weather_service = WeatherService()
        weather_data, is_cached = weather_service.get_weather(city, country, ip_address)
        
        weather_data['cached'] = is_cached
        response_serializer = WeatherResponseSerializer(weather_data)
        
        logger.info(f"Weather request for {city}, {country} from IP {ip_address} - Cached: {is_cached}")
        return Response(response_serializer.data, status=status.HTTP_200_OK)
    except ValueError as e:
        logger.warning(f"Weather request failed for {city}, {country}: {str(e)}")
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_404_NOT_FOUND if 'not found' in str(e) else status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        logger.error(f"Unexpected error for {city}, {country}: {str(e)}")
        return Response({'error': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@swagger_auto_schema(
    method='get',
    responses={200: WeatherQuerySerializer(many=True)},
    operation_description="Get the last 10 weather queries"
)
@api_view(['GET'])
@throttle_classes([AnonRateThrottle, UserRateThrottle])
def get_weather_history(request):
    try:
        queries = WeatherQuery.get_recent_queries(10)
        serializer = WeatherQuerySerializer(queries, many=True)
        
        logger.info(f"Weather history requested from IP {get_client_ip(request)}")
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Error fetching weather history: {str(e)}")
        return Response({'error': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@swagger_auto_schema(
    method='get',
    responses={200: openapi.Response('API Health Status')},
    operation_description="Check API health status"
)
@api_view(['GET'])
def health_check(request):
    return Response({
        'status': 'healthy',
        'timestamp': timezone.now(),
        'version': '1.0.0'
    })
