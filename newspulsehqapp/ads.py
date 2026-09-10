import random

from django.db.models import F, Q
from django.utils import timezone

from .models import SponsoredAd


def get_active_ad(placement, track_impression=True):
    """
    Return one live SponsoredAd for the given placement, or None.

    When several ads share the top priority for a placement, one is
    picked at random so direct-sold campaigns rotate impressions
    instead of one advertiser always winning the slot.
    """
    now = timezone.now()

    candidates = list(
        SponsoredAd.objects.filter(placement=placement, is_active=True)
        .filter(Q(starts_at__isnull=True) | Q(starts_at__lte=now))
        .filter(Q(ends_at__isnull=True) | Q(ends_at__gte=now))
    )

    if not candidates:
        return None

    top_priority = max(ad.priority for ad in candidates)
    top_candidates = [ad for ad in candidates if ad.priority == top_priority]

    ad = random.choice(top_candidates)

    if track_impression:
        SponsoredAd.objects.filter(pk=ad.pk).update(
            impression_count=F("impression_count") + 1
        )

    return ad
