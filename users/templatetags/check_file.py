from django import template
import os
from django.conf import settings

register = template.Library()

@register.filter
def file_exists(file_field):
    if not file_field:
        return False
    full_path = os.path.join(settings.MEDIA_ROOT, file_field.name)
    return os.path.isfile(full_path)
