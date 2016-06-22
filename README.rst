django-mc
=========

|pypi-badge| |build-status|

.. |build-status| image:: https://travis-ci.org/team23/django_mc.svg
    :target: https://travis-ci.org/team23/django_mc

.. |pypi-badge| image:: https://img.shields.io/pypi/v/django-mc.svg
    :target: https://pypi.python.org/pypi/django-mc

**django-mc** let's you build a CMS system that evolves around a few key ideas:

- **Pages** are Django models where every page represents the content of one
  URL. The content of a page is mostly build up using components.
- **Components** are content fragments that can be part of a page, but usually
  don't have their own canonical URL. Examples for components might be an
  image, a pdf download, a block of text, a contact form, etc.

django-mc expects that you define different "regions" in a page that can take
components. A region might be a segment of your frontend design like "header",
"footer", "sidebar" or "content", etc. This allows you to not only fill a page
with components but also decide in which part ("region") of the page they
should be placed.

A page usually also has a **layout** assigned. A layout is also just a model
that may define multiple components in different regions. The final contents of
the rendered page will then be a combination of the components from the page
and from the page layout. The layout more or less defines the fallback
components for a region that should be displayed if one region in the page has
no components assigned.

A model that can hold components (i.e. layouts and pages) is called a
component provider (see ``django_mc.models.RegionComponentProvider``).

django_mc is unopinionated about how you display and manage the data inside the
user facing backend. This means you can use whatever administration interface
you want. A good fit though might be `django_backend`_.

.. _django_backend: https://github.com/team23/django_backend

Concepts
--------

django_mc uses a few key concepts to describe how it works.

Regions
~~~~~~~

In django_mc a region is a part of a template that gets filled up with dynamic
content. This content is defined by components (see below for more on
components).

So a region is like a placeholder in your template that is managed by your CMS.
In a "typical" website design, typical regions might be called "sidebar right",
"footer", "content area", etc.

A region is defined by the model ``django_mc.models.Region``.

Since you use the region directly in the your templates, you need to know
upfront which regions there are. So the best is not to change the regions
during runtime, but create them using migrations.

A region is also limited to specific components, so you define which component
types can go into a specific region. That is information is also stored in the
region model. So we recommend also using migrations to create this information.

Since you usually have a lot of different component types in your project, we
created the helpers
``django_mc.migration_operations.AddComponentTypeToRegions`` and
``django_mc.migration_operations.RemoveComponentTypeToRegions``. Use them like
this in your migrations::

    class Migration(migrations.Migration):
        operations = [
            AddComponentTypeToRegions(
                'my_component_app',
                'MyComponentModel',
                regions=['footer', 'sidebar_right'],
            )
        ]

Leave out the ``regions`` argument to add the component type to all regions.

Pages (e.g. a RegionComponentProvider)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

django_mc doesn't come with a pre-built page model. That's up to you to create
the page types you need. You are free to create as many different page models
as you need and structure them as needed.

In most cases your pages should inherit from
``django_mc.models.RegionComponentProvider``. This is a model mixin that
creates a many to many relation to components. The relation holds two more
information: The region a component should go in and in what position it should
be displayed.

So while rendering a page, it can decide what components (i.e. dynamic content)
shall go into a region.

Layout
~~~~~~

Usually you will create a foreign key from your page models to the layout.

A layout is also a ``RegionComponentProvider``, and experience shows that
having a layout to define a set of components that can be reused between pages
is a useful tool.

For example you could create a component based menu structure that you put in
the "footer" region in the layout. Now this content is shown in the footer
region on every page by default. Still you have the possibility to easily
override or enhance the footer content in the page itself.

django_mc comes with a default implementation for a layout model:
``django_mc.Layout``. But it's a swappable model, so feel free to change it
with your own implementation.

Components
~~~~~~~~~~

Components are the basic building blocks for managed content in django_mc.
django_mc only comes with the base class ``django_mc.models.ComponentBase``.
The components you define should subclass from that. This is using Django's
model inheritance and is required in order to make the many to many relation
provided by the ``RegionComponentProvider`` possible.

You are encouraged to create as many component types as you need.

Don't forget to add the component class to all regions as valid component type
in a migration.

Template Hints
~~~~~~~~~~~~~~

django-mc doesn't enforce any view structure to display your pages. So it's
also very flexible in the template layer as it doesn't enforce any predefined
templates that you have to use, and doesn't enforce a template name for pages.

However it tries to give you hints. For example a layout will give you it's
slug as a hint that you could in corporate into the template name. Here is an
example:

You have defined your page model (that has a layout associated) and have built
a corresponding view. Now the view uses the template name
``myapp/page.html`` to render the page. If you now decide to take the template
hint of the layout into account, you will use a list of template names to
decide which one to render. The resulting list might look like
``['myapp/page-mylayout.html', 'myapp/page.html']``. The first existing
template will then be chosen.

So the hint will suggest a variation of the template name. That gives a
powerful, but predictable way to switch out the used template without much
hassle.

In order to use this mechanism, it's easiest to make your page views subclass
from ``django_mc.views.LayoutMixin``. Have a look at it's source code to see
how it works internally. It's well commented.

Development
-----------

Create a virtual environment, then install ``django-mc`` and its dependencies
(including the test dependencies) with::

    pip install -r requirements.txt

Then you can run all tests with::

    tox
