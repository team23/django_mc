from django.conf import settings
from django.utils.module_loading import import_module, module_has_submodule


def autodiscover():
    for app in settings.INSTALLED_APPS:
        mod = import_module(app)
        try:
            import_module('%s.%s' % (app, 'link_resolvers'))
        except:
            if module_has_submodule(mod, 'link_resolvers'):
                raise
