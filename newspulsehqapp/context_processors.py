from django.conf import settings

from .models import Category


def site_categories(request):
    return {
        "categories": Category.objects.all(),
    }


def adsense_settings(request):
    return {
        "adsense_client_id": settings.ADSENSE_CLIENT_ID,
        "adsense_slot_home": settings.ADSENSE_SLOT_HOME,
        "adsense_slot_article": settings.ADSENSE_SLOT_ARTICLE,
        "adsense_slot_category": settings.ADSENSE_SLOT_CATEGORY,
    }
