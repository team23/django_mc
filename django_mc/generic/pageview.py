from django.http import Http404
from django.utils.translation import ugettext as _
from django.views.generic.detail import DetailView
from django_mc.models import Region
from django_mc.views import LayoutMixin


class PageView(LayoutMixin, DetailView):
    """
    Base implementation for a page object. A page might be something like a
    component provider. It also usually holds a ForeignKey to the ``Layout``
    model.

    Subclasses usually want to set the ``queryset`` attribute or override the
    ``get_queryset`` method.

    If the page object defines its own layout, then override the ``get_layout``
    method and return it accordingly.
    """

    context_object_name = 'page'

    def add_extra_component(self, region, component):
        if not hasattr(self, 'extra_components'):
            self.extra_components = {}
        if isinstance(region, basestring):
            region = Region.objects.regions_by_slug()[region]
        self.extra_components.setdefault(region.pk, []).append(component)

    def get_components_by_region(self):
        try:
            return self.extra_components
        except:
            return {}

    def get_component_providers(self):
        return super(PageView, self).get_component_providers() + [
            self.object,
            self
        ]

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)
