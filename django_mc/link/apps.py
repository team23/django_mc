from django.apps import AppConfig
from .autodiscover import autodiscover


class LinkAppConfig(AppConfig):
    label = 'django_mc_link'
    name = 'django_mc.link'
    verbose_name = 'Link'

    def ready(self):
        autodiscover()
