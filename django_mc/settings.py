from django.conf import settings


MC_LAYOUT_MODEL = getattr(settings, 'MC_LAYOUT_MODEL', 'django_mc.layout')
MC_COMPONENT_BASE_MODEL = getattr(settings, 'MC_COMPONENT_BASE_MODEL', 'django_mc.componentbase')
