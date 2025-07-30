from rest_framework import serializers
from .models import WeatherQuery

class WeatherQuerySerializer(serializers.ModelSerializer):
    class Meta:
        model = WeatherQuery
        fields = [
            'id', 'city', 'country', 'temperature', 'description',
            'humidity', 'pressure', 'wind_speed', 'timestamp'
        ]
        read_only_fields = ['id', 'timestamp']

class WeatherRequestSerializer(serializers.Serializer):
    city = serializers.CharField(max_length=100)
    country = serializers.CharField(max_length=2, required=False, allow_blank=True)

    def validate_city(self, value):
        if not value.strip():
            raise serializers.ValidationError("City name cannot be empty")
        return value.strip()

class WeatherResponseSerializer(serializers.Serializer):
    city = serializers.CharField()
    country = serializers.CharField()
    temperature = serializers.FloatField()
    description = serializers.CharField()
    humidity = serializers.IntegerField()
    pressure = serializers.IntegerField()
    wind_speed = serializers.FloatField()
    cached = serializers.BooleanField()
    timestamp = serializers.DateTimeField()