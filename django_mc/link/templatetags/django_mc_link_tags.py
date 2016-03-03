# -*- coding: utf-8 -*-
from django import template

from ..pattern import LINK_REFERENCE_REGEX
from ..registry import registry, ResolveError


register = template.Library()


@register.assignment_tag
def resolve_link(reference):
    match = LINK_REFERENCE_REGEX.match(reference)
    if not match:
        return ''
    bits = match.groupdict()
    if bits['url'] is not None:
        return bits['url']
    elif bits['path'] is not None:
        return bits['path']
    else:
        try:
            return registry.resolve(bits['object_type'], bits['object_id'])
        except ResolveError:
            return ''
