# -*- coding: utf-8 -*-
'''
Implements a ``LinkField`` which takes care of converting the string that is
stored in the database (e.g. a link id like ``page/123``) into a URL
when converted to a string.
'''

from django.core.validators import RegexValidator
from django.db import models
from django.utils.translation import ugettext_lazy as _

from .registry import ResolveError
from .pattern import LINK_REFERENCE_REGEX


class Link(object):
    '''
    It takes one of the three types of link references, described in
    ``LinkField`` docstring.

    You use the ``url`` attribute to get the URL this link links to.
    '''

    def __init__(self, reference):
        self.reference = reference

        match = LINK_REFERENCE_REGEX.match(reference)
        if not match:
            raise ValueError(
                'Given reference is not a valid link id: {}'
                .format(repr(reference)))

        bits = match.groupdict()
        if bits['url'] is not None:
            self._url = bits['url']
        elif bits['path'] is not None:
            self._url = bits['path']
        else:
            self.object_type = bits['object_type']
            self.object_id = bits['object_id']

    def __repr__(self):
        return '<{0}: {1}>'.format(
            self.__class__.__name__,
            repr(self.reference))

    def __unicode__(self):
        return self.reference

    def __len__(self):
        return len(self.reference)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return other.reference == self.reference
        return False

    def resolve(self):
        from .registry import registry
        self._url = registry.resolve(self.object_type, self.object_id)
        return self._url

    def exists(self):
        if hasattr(self, '_url'):
            return True
        try:
            self.resolve()
            return True
        except ResolveError:
            return False

    @property
    def url(self):
        if not hasattr(self, '_url'):
            try:
                self.resolve()
            except ResolveError:
                return ''
        return self._url


class LinkReferenceValidator(RegexValidator):
    regex = LINK_REFERENCE_REGEX
    message = _(
        'Please enter a valid link. This is either a URL (starting with '
        'http:// or https://), a absolute path (starting with a slash) '
        'or a link id which looks like "page/123".')


class LinkField(models.CharField):
    '''
    ``LinkField`` allows three different formats for URLs.

    1. A full URL, starting with ``<protocol>://``
    2. An absolute path, starting with ``/``
    3. A link id which is in the form of ``<link-type>/<object-id>``,
       e.g. ``news/7``

    It deserializes to a python class which evaluates to the printable
    absolute url.
    '''

    __metaclass__ = models.SubfieldBase

    default_error_messages = models.CharField.default_error_messages.copy()
    default_error_messages['invalid'] = _(
        'Please enter a valid link id. This is either a URL (starting with '
        'http:// or https://), a absolute path (starting with a slash) '
        'or a link id which looks like "page/123".')

    default_help_text = _(
        'You can enter full URLs, absolute paths (starting with a slash) or '
        'a link it that represents a content in the CMS. These '
        'usually look like "page/123".')

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('max_length', 250)
        kwargs.setdefault('help_text', self.default_help_text)
        super(LinkField, self).__init__(*args, **kwargs)

    def clean(self, value, model_instance):
        cleaned_value = super(LinkField, self).clean(value, model_instance)
        if value:
            validator = LinkReferenceValidator()
            validator(value)
        return cleaned_value

    def to_python(self, value):
        if not value:
            return super(LinkField, self).to_python(value)
        if isinstance(value, Link):
            return value
        try:
            return Link(value)
        except ValueError:
            return value

    def get_prep_value(self, value):
        if isinstance(value, Link):
            value = value.reference
        if not value:
            return value
        return unicode(value)
