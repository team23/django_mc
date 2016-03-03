"""
Support for django_textfomat.
"""

import re
from bs4 import BeautifulSoup
from django_textformat.registry import registry

from .registry import ResolveError
from .pattern import get_object_reference_regex


@registry.register
def convert_link(value):
    """
    Replaces ``page/123`` object links in ``<a href="page/123">`` with the
    actual ID resolved by the link registry.
    """
    from .registry import registry as link_registry

    reference = get_object_reference_regex()
    reference = re.compile('^{}$'.format(reference.pattern))

    soup = BeautifulSoup(value, 'lxml')

    for link in soup.find_all('a'):
        href = link.get('href')
        if href:
            try:
                href = reference.sub(
                    lambda m: link_registry.resolve(
                        m.group('object_type'),
                        m.group('object_id')),
                    href
                )
                link['href'] = href
            except ResolveError:
                if link.string:
                    link.replace_with(link.string)  # remove link completely, but preserve link content (/text)
                else:
                    link.replace_with('')  # remove the link completely, it has no reusable content

    return re.sub('^(<html>)?<body>', '', re.sub('</body>(</html>)?$', '', unicode(soup)))
