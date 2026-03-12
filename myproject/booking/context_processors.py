from django.utils import timezone

from .models import Advertisement


def active_ads(request):
    """Inject active advertisements into template context.

    Ads are considered active when:
    - is_active is True
    - current date is between start_date and end_date (inclusive)

    Templates can use the returned dict to render ads based on the configured position.
    """
    today = timezone.now().date()
    active_ads_qs = Advertisement.objects.filter(is_active=True, start_date__lte=today, end_date__gte=today)

    # Group by position for easier template usage:
    ads_by_position = {choice[0]: [] for choice in Advertisement.POSITION_CHOICES}
    for ad in active_ads_qs:
        ads_by_position.setdefault(ad.position, []).append(ad)

    return {
        'active_ads': ads_by_position,
    }
