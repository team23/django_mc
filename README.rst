django-mc
=========

|pypi-badge| |build-status|

.. |build-status| image:: https://travis-ci.org/team23/django_mc.svg
    :target: https://travis-ci.org/team23/django_mc

.. |pypi-badge| image:: https://img.shields.io/pypi/v/django-mc.svg
    :target: https://pypi.python.org/pypi/django-mc

**django-mc** let's you build a CMS system that evolves around a few key ideas:

- Pages are Django models where every page represents the content of one URL.
  The content of a page is mostly build up using components.
- Components are content fragments that can be part of a page, but usually
  don't have their own canonical URL. Examples for components might be an
  image, a pdf download, a block of text, a contact form, etc.

django-mc expects that you define different "regions" in a page that can take
components. A region might be a segment of your frontend design like "header",
"footer", "sidebar" or "content", etc. This allows you to not only fill a page
with components but also decide in which part ("region") of the page they
should be placed.

A page usually also has a layout assigned. A layout is also just a model that
may define multiple components in different regions. The final contents of the
rendered page will then be a combination of the components from the page and
from the page layout. The layout more or less defines the fallback components
for a region that should be displayed if one region in the page has no
components assigned.

A model that can hold components (i.e. layouts and pages) is called a
component provider (see ``django_mc.models.RegionComponentProvider``).

django_mc is unopinionated about how you display and manage the data inside the
user facing backend. This means you can use whatever administration interface
you want. A good fit though might be ``django_backend``.

Development
-----------

Create a virtual environment, then install ``django-mc`` and its dependencies with::

Install the dependencies (including the test dependencies) with::

    pip install -r requirements.txt

Then you can run all tests with::

    tox
