from UserList import UserList
from django.views.generic import View
from django.views.generic.detail import BaseDetailView
from django_mc.mixins import TemplateHintProvider
from django_mc.models import Region, Layout as _Layout
from django.db.models.loading import get_model
from .settings import MC_LAYOUT_MODEL


class RegionComponentList(TemplateHintProvider, UserList):
    '''
    Wrapper for a region including a list of provided component that will be
    used in the template.
    '''

    def __init__(self, region, data=None):
        self._region = region
        if data is not None:
            self.data = list(
                component
                for component in data
                if component is not None)

    def suggest_template_names(self, *args, **kwargs):
        return self._region.suggest_template_names(*args, **kwargs)


class LayoutMixin(object):
    '''
    This mixin provides methods to easily write a detail view that changes its
    appearance based on a layout.

    Subclasses usually want to override the following methods:

    * ``get_layout``
    * ``get_component_providers``
    * ``get_hint_providers``

    See the docstrings on those methods for their purpose.
    '''

    layout_slug = None

    def get_layout(self):
        '''
        Determine which layout should be used in this view. It defaults to the
        default layout. You propably want to replace this in the subclass with
        something like::

            def get_layout(self):
                return self.object.layout
        '''
        Layout = get_model(*MC_LAYOUT_MODEL.split('.'))
        layout_slug = self.layout_slug
        if layout_slug is None:
            layout_slug = Layout.DEFAULT_LAYOUT_SLUG
        return Layout.objects.get(slug=layout_slug)

    def dispatch(self, request, *args, **kwargs):
        '''
        Set the object and layout objects here to make the available as early
        as possible to avoid fetching them more than once.
        '''
        if isinstance(self, BaseDetailView) or hasattr(self, 'get_object'):
            # support self.object for all request methods, BaseDetailView only sets
            # self.object for GET requests
            self.object = self.get_object()
        else:
            self.object = None
        self.layout = self.get_layout()
        return super(LayoutMixin, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        '''
        This method is specified here to prevent the fetching of
        ``self.object`` since we already did that in the ``dispatch`` method.
        '''
        if isinstance(self, BaseDetailView):
            context = self.get_context_data(object=self.object)
            return self.render_to_response(context)
        else:
            return super(LayoutMixin, self).get(request, *args, **kwargs)

    def get_component_providers(self):
        '''
        The view may provide multiple component providers, normally this will be like
        `return [self.layout, self.object]`. Note, that you need to add the
        content object yourself, this base method will only contain the layout.
        '''
        return self.layout.get_component_providers()

    def order_component_list(self, component_list):
        '''
        Implement the logic for ordering the component items that where
        collected from the component providers.
        '''
        return sorted(component_list, key=lambda c: c.position)

    def get_components_for_regions(self):
        '''
        Return a dict of the format::

            {
                region_slug: RegionComponentList([component_obj, component_obj, ...]),
                region_slug: RegionComponentList([component_obj, component_obj, ...]),
                ...
            }

        The component objects are retrieved from the component providers specified
        in ``get_component_providers`` and the chosen layout object.
        '''
        regions_by_id = Region.objects.regions_by_pk()
        regions_mapping = Region.objects.region_pk_to_slug()

        components_by_region = {}
        for component_provider in self.get_component_providers():
            for region_id, region_components in component_provider.get_components_by_region().iteritems():
                components_by_region[region_id] = regions_by_id[region_id].extend_components(
                    components_by_region.get(region_id, []),
                    region_components,
                )

        return dict([  # convert components by region id to components by region slug
            (
                regions_mapping[region_id],
                RegionComponentList(regions_by_id[region_id], [
                    c.resolve_component() for c in self.order_component_list(components)
                ]),
            )
            for region_id, components
            in components_by_region.iteritems()
        ])

    def get_context_data(self, **kwargs):
        kwargs['layout'] = self.layout
        kwargs['region'] = self.get_components_for_regions()
        return super(LayoutMixin, self).get_context_data(**kwargs)

    def get_hint_providers(self):
        '''
        Return a list of ``TemplateHintProvider``s that shall be used to
        determine the template name.
        '''
        return [self.layout]

    def get_template_names(self):
        '''
        This method requires the return value of ``get_object`` to be a
        ``Renderable`` object. Otherwise it wouldn't be possible to use
        template hints.
        '''
        template_names = []
        if self.object and hasattr(self.object, 'suggest_template_names'):
            hint_providers = self.get_hint_providers()
            hint_providers = [self.object] + hint_providers
            template_names = self.object.get_template_names(hint_providers, type='detail')
        if getattr(self, 'get_template_names', None) is not None:
            template_names = template_names + super(LayoutMixin, self).get_template_names()
        return template_names
