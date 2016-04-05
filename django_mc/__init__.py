from django.apps import apps as django_apps
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from .mixins import *  # noqa


__version__ = '0.1.0'


default_app_config = 'django_mc.apps.DjangoMCAppConfig'


def get_layout_model():
    """
    Returns the Layout model that is active in this project.
    """
    try:
        return django_apps.get_model(settings.MC_LAYOUT_MODEL)
    except ValueError:
        raise ImproperlyConfigured("MC_LAYOUT_MODEL must be of the form 'app_label.model_name'")
    except LookupError:
        raise ImproperlyConfigured(
            "MC_LAYOUT_MODEL refers to model '%s' that has not been installed" % settings.MC_LAYOUT_MODEL
        )
