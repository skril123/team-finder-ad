from urllib.parse import urlparse

from django.core.exceptions import ValidationError

from core.constants import GITHUB_HOSTS


def validate_github_url(value):
    if not value:
        return value
    hostname = urlparse(value).hostname or ""
    if hostname.lower() not in GITHUB_HOSTS:
        raise ValidationError("Ссылка должна вести на GitHub.")
    return value
