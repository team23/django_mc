from django.shortcuts import _get_queryset


__all__ = ('LinkResolver', 'ModelLinkResolver',)


class LinkResolver(object):
    def resolve(self, object_id):
        return RuntimeError('You have to implement this, use ModelLinkResolver for simple models')

    def handles(self, obj):
        return False

    def get_object_id(self, obj):
        raise NotImplementedError('get_object_id needs to be implemented by subclasses.')


class ModelLinkResolver(LinkResolver):
    def __init__(self, model_or_qs):
        self.queryset = _get_queryset(model_or_qs)
        self.model = self.queryset.model

    def resolve(self, object_id):
        return self.queryset.get(pk=object_id).get_absolute_url()

    def handles(self, obj):
        return isinstance(obj, self.model)

    def get_object_id(self, obj):
        return obj.pk
