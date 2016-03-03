"""
This app makes it easy to link to specific pages or other objects in the site
by using simple identifiers like ``page/123``.

To use the full set of features, add ``'django_mc.link'`` to your
``INSTALLED_APPS`` setting.
"""
from .fields import Link  # noqa
from .fields import LinkField  # noqa
from .registry import registry  # noqa
from .registry import ResolveError  # noqa
from .registry import ReverseResolveError  # noqa
from .resolvers import *  # noqa


default_app_config = 'django_mc.link.apps.LinkAppConfig'


register = registry.register
resolve = registry.resolve
reverse = registry.reverse
