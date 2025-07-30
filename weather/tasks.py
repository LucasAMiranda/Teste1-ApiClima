
from celery import shared_task
import logging
from .models import WeatherQuery

logger = logging.getLogger('weather')

@shared_task
def cleanup_old_weather_queries():
    """
    Celery task to cleanup old weather queries.
    Keeps only the last 100 queries to prevent database bloat.
    """
    try:
        initial_count = WeatherQuery.objects.count() 

        keep_last = 100
        ids_to_keep = WeatherQuery.objects.order_by('-id')[:keep_last].values_list('id', flat=True)
        deleted_count, _ = WeatherQuery.objects.exclude(id__in=ids_to_keep).delete()

        final_count = WeatherQuery.objects.count()

        logger.info(
            f"Cleanup completed. "
            f"Initial: {initial_count}, Deleted: {deleted_count}, Remaining: {final_count}"
        )

        return {
            "initial": initial_count,
            "deleted": deleted_count,
            "remaining": final_count
        }

    except Exception:
        logger.exception("Error in cleanup task")
        raise