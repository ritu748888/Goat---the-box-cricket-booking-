from django.conf import settings


def admin_email(request):
    """Add ADMIN_EMAIL setting to every template context."""
    return {'ADMIN_EMAIL': settings.ADMIN_EMAIL}
