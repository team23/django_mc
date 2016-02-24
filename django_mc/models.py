# -*- coding: utf-8 -*-
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django_deferred_polymorph.models import SubDeferredPolymorphBaseModel
from .mixins import Renderable
from .mixins import TemplateHintProvider
from .settings import MC_COMPONENT_BASE_MODEL


class RegionManager(models.Manager):
    def get_by_natural_key(self, slug):
        return self.get(slug=slug)

    def regions_by_slug(self):
        try:
            return self._regions_by_slug
        except AttributeError:
            self.fill_cache()
            return self._regions_by_slug

    def regions_by_pk(self):
        try:
            return self._regions_by_pk
        except AttributeError:
            self.fill_cache()
            return self._regions_by_pk

    def region_pk_to_slug(self):
        try:
            return self._region_pk_to_slug
        except AttributeError:
            self.fill_cache()
            return self._region_pk_to_slug

    def fill_cache(self):
        regions = list(self.all())
        self._regions_by_slug = dict((r.slug, r) for r in regions)
        self._regions_by_pk = dict((r.pk, r) for r in regions)
        self._region_pk_to_slug = dict((r.pk, r.slug) for r in regions)

    def clear_cache(self):
        try:
            del self._regions_by_slug
            del self._regions_by_pk
            del self._region_pk_to_slug
        except AttributeError:
            pass


class Region(TemplateHintProvider, models.Model):
    COMBINE = 'combine'
    OVERWRITE = 'overwrite'
    EXTEND_CHOICES = (
        (COMBINE, _('Add to existing layout components')),
        (OVERWRITE, _('Replace existing layout components')),
    )

    name = models.CharField(max_length=50)
    slug = models.SlugField(unique=True)
    component_extend_rule = models.CharField(
        max_length=16, choices=EXTEND_CHOICES,
        help_text=_(
            'Define how page components that is added to this region change '
            'the layout components.'))
    position = models.IntegerField(default=0)
    available_components = models.ManyToManyField('contenttypes.ContentType')

    objects = RegionManager()

    class Meta:
        verbose_name = _('Region')
        verbose_name_plural = _('Regions')
        ordering = ('position',)

    def natural_key(self):
        return [self.slug]

    def __unicode__(self):
        return self.name

    def get_template_hints(self, name_provider, hint_providers):
        return ['region-{0}'.format(self.slug)]

    def extend_components(self, first, second):
        '''
        Apply the ``component_extend_rule`` to two given lists. The first
        argument shall be the one that is extended, the second argument the one
        that shall overwrite or be combined with the original first one.
        '''
        if self.component_extend_rule == self.OVERWRITE:
            if second:
                return list(second)
            else:
                return list(first)
        elif self.component_extend_rule == self.COMBINE:
            combined = []
            if first:
                combined.extend(first)
            if second:
                combined.extend(second)
            return combined

    def get_valid_component_models(self):
        return [
            content_type.model_class
            for content_type in self.available_components.all()
        ]


class RegionComponentBaseManager(models.Manager):
    def visible(self):
        '''
        This allows django_mc to provide a common place for injecting additional filters
        to the component<->page/layout relation. Only "visible" components will then be used.
        As django_mc does not need any visible-filtering by default we just return self.all(),
        you still may overwrite this to fit your needs.
        '''
        return self.all()


class RegionComponentProvider(models.Model):
    '''
    Drop this mixin into a model that can link component objects to regions. The
    mixin will take care of creating the intermediary model.
    '''

    class Meta:
        abstract = True

    def get_components_by_region(self):
        '''
        Return a dictionary in the form of::

            {
                region.pk: [region_component_obj, region_component_obj, ...]
            }
        '''

        # see RegionComponentBaseManager for details on visible()
        queryset = self.region_components.visible()
        regions = {}
        for region_component in queryset:
            regions.setdefault(region_component.region_id, []).append(region_component)
        return regions

    class RegionComponentBase(models.Model):
        region = models.ForeignKey('django_mc.Region', related_name='+')
        component = models.ForeignKey(MC_COMPONENT_BASE_MODEL, related_name='+')
        position = models.IntegerField(default=0)

        # The field ``provider`` will be dynamically defined in the created
        # intermediary table.

        objects = RegionComponentBaseManager()

        class Meta:
            abstract = True

        def __unicode__(self):
            return unicode(
                '%s @ %s in %s' % (
                    self.component.get_real_instance(),
                    self.provider,
                    self.region))

        def resolve_component(self):
            return self.component.resolve_component()

    @classmethod
    def _create_region_component_model(cls, sender, **kwargs):
        '''
        Generate intermediary model automatically that looks like this:

            class <ModelName>RegionComponent(ComponentProvider.RegionComponentBase):
                region = models.ForeignKey(Region, related_name='+')
                provider = models.ForeignKey(<Model>,
                    related_name='region_components')
                component = models.ForeignKey(ComponentBase, related_name='+')
                position = models.IntegerField(default=0)

        Note that the intermediary model inherits from the
        ``RegionComponentBase`` attribute on the ``ComponentProvider``. You can use
        this behaviour to subclass ``ComponentProvider`` and override
        ``RegionComponentBase`` to alter the behaviour and fields of the
        intermediary model.
        '''

        # Ignore calls from models that are not inherited from
        # RegionComponentProvider.
        if not issubclass(sender, cls):
            return

        # Ignore calls from models that are not concrete models
        # RegionComponentProvider.
        if sender._meta.abstract:
            return

        # Ignore calls from models that are swapped
        if sender._meta.swapped:
            return

        # The sender of the signal is the model that we want to attach the
        # branch model to.
        if hasattr(sender, 'RegionComponent'):
            return  # seems like some base class already has a region component relation
        # assert not hasattr(sender, 'RegionComponent'), \
        #     'There is already a RegionComponent specified for %s' % sender

        db_table = '%s_%s' % (
            sender._meta.db_table,
            'regioncomponent')

        meta = type('Meta', (object,), {
            'db_table': db_table,
            'app_label': sender._meta.app_label,
            'db_tablespace': sender._meta.db_tablespace,
            # We sadly cannot use translations here, as using translations ("%" does resolve the
            # translation) triggers an import off all installed apps
            # (see django/utils/translation/trans_real.py:158). This may lead
            # to circular imports and thus break your project badly! I'm sorry.
            # 'verbose_name': _('%s region component') % sender._meta.verbose_name,
            # 'verbose_name_plural': _('%s region component') % sender._meta.verbose_name_plural,
        })

        model_name = '%sRegionComponent' % sender._meta.object_name

        bases = (sender.RegionComponentBase,)

        # Construct and return the new class.
        model = type(str(model_name), bases, {
            'Meta': meta,
            '__module__': sender.__module__,
            'provider': models.ForeignKey(
                sender,
                related_name='region_components'),
        })

        sender.RegionComponent = model


models.signals.class_prepared.connect(
    RegionComponentProvider._create_region_component_model)


class LayoutManager(models.Manager):
    def get_by_natural_key(self, slug):
        return self.get(slug=slug)


class LayoutMixin(TemplateHintProvider, RegionComponentProvider, models.Model):
    DEFAULT_LAYOUT_SLUG = 'default'

    name = models.CharField(max_length=50)
    slug = models.SlugField(unique=True)
    parent = models.ForeignKey('self', null=True, blank=True,
        help_text=_(
            'Select a layout which shall be extended by this layout according to region '
            'extend rules.'))

    objects = LayoutManager()

    class Meta:
        abstract = True
        verbose_name = _('Layout')
        verbose_name_plural = _('Layouts')

    def __unicode__(self):
        return self.name

    def natural_key(self):
        return (self.slug,)

    def get_template_hints(self, name_provider, hint_providers):
        if self.parent:
            parent_hints = self.parent.get_template_hints(name_provider, hint_providers)
        else:
            parent_hints = []
        return ['layout-{0}'.format(self.slug)] + parent_hints

    def get_component_providers(self):
        if self.parent_id:
            return self.parent.get_component_providers() + [self]
        else:
            return [self]

#     @classmethod
#     def _create_default_layout(cls, sender, **kwargs):
#         # Only create default layout when the synced app is the django_mc.
#         if sender.__name__ == __name__:
#             default_layout = cls.objects.filter(slug=Layout.DEFAULT_LAYOUT_SLUG)
#             if not default_layout.exists():
#                 cls.objects.create(
#                     slug=Layout.DEFAULT_LAYOUT_SLUG,
#                     name='Default')
#
#
# models.signals.post_syncdb.connect(Layout._create_default_layout)


class Layout(LayoutMixin):
    class Meta(LayoutMixin.Meta):
        swappable = 'MC_LAYOUT_MODEL'


class ComponentBaseMixin(Renderable, SubDeferredPolymorphBaseModel):
    class Meta:
        abstract = True
        verbose_name = _('Component Base')
        verbose_name_plural = _('Component Bases')

    def resolve_component(self):
        # Make sure we get the real component model instance.
        #
        # May be used to implement more complex component resolve strategies
        # (e.g. versionable components, that need to switch to the current version)
        return self.get_real_instance()

    def get_template_basename(self):
        return '%s.html' % self.get_real_instance()._meta.object_name.lower()


class ComponentBase(ComponentBaseMixin):
    class Meta(ComponentBaseMixin.Meta):
        swappable = 'MC_COMPONENT_BASE_MODEL'
