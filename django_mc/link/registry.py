TYPE_ID_SEPARATOR = '/'


class ResolveError(Exception):
    pass


class ReverseResolveError(Exception):
    pass


class Registry(object):
    def __init__(self):
        self._registry = {}

    def register(self, object_type, object_resolver):
        self._registry[object_type] = object_resolver

    def resolve(self, object_type, object_id):
        if object_type not in self._registry:
            raise ResolveError('module not registered (%s)' % object_type)
        try:
            return self._registry[object_type].resolve(object_id)
        except:
            raise ResolveError('module could not handle resolve, type {0}, id {1}'.format(object_type, object_id))

    def reverse(self, obj):
        for object_type, object_resolver in self._registry.items():
            if object_resolver.handles(obj):
                return TYPE_ID_SEPARATOR.join((
                    unicode(object_type),
                    unicode(object_resolver.get_object_id(obj))))
        raise ReverseResolveError(
            'no object resolver found for object: {0}'.format(repr(obj)))


registry = Registry()
