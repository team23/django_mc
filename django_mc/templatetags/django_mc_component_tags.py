from django import template
from django.template import Variable, TemplateSyntaxError
from django.template.loader import render_to_string
from ..mixins import CompositeTemplateHintProvider


register = template.Library()


class RenderComponentNode(template.Node):
    '''
    {% render_component %} template tag. It takes a ``Renderable`` object as
    first argument and then a list of hint providers after the keyword
    ``for``. So the usage might look like::

        {% render_component image for layout %}

    This will render the template with the name returned by
    ``image.get_template_names(hint_providers=[layout])``.

    The template tag also adds the variable ``PARENT_HINT_PROVIDER`` to the
    context of the rendered item. It contains a composite template hint
    provider that can be used for nested component items. Like this:

        # in the page template
        {% render_component page.gallery for layout %}

        # in the gallery template
        {% render_component gallery.image.0 for gallery PARENT_HINT_PROVIDER %}

    This will render ``gallery.image.0`` with the hint providers ``[gallery,
    layout]``.
    '''

    parent_hint_providers_variable_name = 'PARENT_HINT_PROVIDER'

    # TODO: It might be useful to change the template_type via the template
    # tag. A suggested syntax would use the 'as' keyword:
    #     {% render_component obj for layout as "partial" %}
    template_type = 'partial'

    def __init__(self, component_var, template_hint_providers):
        self.component_var = component_var
        self.template_hint_providers = template_hint_providers

    def render(self, context):
        component = self.component_var.resolve(context)
        hint_providers = [
            hint_provider.resolve(context)
            for hint_provider in self.template_hint_providers]
        hint_providers = [
            hint_provider
            for hint_provider in hint_providers
            if hint_provider]

        composite_hint_providers = CompositeTemplateHintProvider(hint_providers)
        template_names = component.get_template_names(
            type=self.template_type,
            hint_providers=hint_providers)

        component_context = {}
        component_context.update(
            composite_hint_providers.suggest_context_data(component))
        component_context[self.parent_hint_providers_variable_name] = composite_hint_providers

        component_context.update(component.get_context_data())
        context.update(component_context)
        try:
            return render_to_string(template_names, context)
        finally:
            context.pop()

    @classmethod
    def parse(cls, parser, token):
        tokens = token.split_contents()
        tagname = tokens.pop(0)
        component_variable = parser.compile_filter(tokens.pop(0))
        if len(tokens):
            if tokens[0] != 'for':
                raise TemplateSyntaxError('Second argument for %s must be `for`' % tagname)
            tokens.pop(0)
            template_hint_providers = [
                parser.compile_filter(token)
                for token in tokens]
        else:
            template_hint_providers = []
        return cls(component_variable, template_hint_providers)


register.tag('render_component', RenderComponentNode.parse)
