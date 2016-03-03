import re


_BASE_OBJECT_REFERENCE_REGEX_STRING = (
    r'(?:(?P<object_type>{allowed_types})/(?P<object_id>.+))')


OBJECT_REFERENCE_REGEX_STRING = _BASE_OBJECT_REFERENCE_REGEX_STRING.format(
    allowed_types=r'[-a-z]+')

OBJECT_REFERENCE_REGEX = re.compile(OBJECT_REFERENCE_REGEX_STRING)


# Matches all valid input for the LinkField.
LINK_REFERENCE_REGEX = re.compile(
    r'^' +
    r'(?P<url>\w+://.+)|' +
    r'(?P<path>/.*)|' +
    OBJECT_REFERENCE_REGEX_STRING +
    r'$')


def get_object_reference_regex():
    from .registry import registry

    types = [
        re.escape(type_name)
        for type_name in registry._registry.keys()
    ]
    return re.compile(
        _BASE_OBJECT_REFERENCE_REGEX_STRING.format(
            allowed_types=r'|'.join(types)))
