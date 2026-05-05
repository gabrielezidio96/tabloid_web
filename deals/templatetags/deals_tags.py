from django import template
from django.utils import timezone

register = template.Library()


@register.filter
def short_timesince(value):
    if not value:
        return ""
    now = timezone.now()
    diff = now - value
    seconds = int(diff.total_seconds())
    if seconds < 3600:
        return f"{seconds // 60} min"
    if seconds < 86400:
        return f"{seconds // 3600} h"
    return f"{seconds // 86400} d"
