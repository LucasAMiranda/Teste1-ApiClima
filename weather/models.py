from django.db import models

class WeatherQuery(models.Model):
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=2, blank=True, null=True)
    temperature = models.FloatField()
    description = models.CharField(max_length=100)
    humidity = models.IntegerField()
    pressure = models.IntegerField()
    wind_speed = models.FloatField()
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    @classmethod
    def get_recent_queries(cls, limit=10):
        return cls.objects.order_by('-timestamp', '-id')[:limit]

    @classmethod
    def cleanup_old_queries(cls, keep_last=10):
        """Mantém apenas os últimos X registros com desempate por ID"""
        ids_to_keep = cls.objects.order_by('-timestamp', '-id').values_list('id', flat=True)[:keep_last]
        cls.objects.exclude(id__in=ids_to_keep).delete()

    def __str__(self):
        return f"{self.city} - {self.temperature}°C at {self.timestamp}"
