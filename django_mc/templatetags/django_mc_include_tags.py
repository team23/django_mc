from itertools import dropwhile
from itertools import takewhile
from django import template
from django.template.loader import select_template

from django_mc.utils.functional import flatten


register = template.Library()


class HintedIncludeNode(template.Node):
    """
    Syntax::

        {% hinted_include <template-name>+ using <template-hint-provider>+ %}

    Example::

        {% hinted_include "_theme_{hint}.html" using SITE.group %}

    Will include the first template
    """

    def __init__(self, template_name_variables, hint_provider_variables):
        self.template_name_variables = template_name_variables
        self.hint_provider_variables = hint_provider_variables

    def render(self, context):
        hint_providers = [
            var.resolve(context)
            for var in self.hint_provider_variables]

        hints = flatten(
            hint_provider.get_template_hints(
                name_provider=None,
                hint_providers=hint_providers)
            for hint_provider in hint_providers)

        template_names = [
            var.resolve(context)
            for var in self.template_name_variables]

        template_names = flatten(
            [template_name.format(hint=hint) for hint in hints]
            for template_name in template_names)

        tpl = select_template(template_names)
        return tpl.render(context)

    @classmethod
    def parse(cls, parser, token):
        tokens = token.split_contents()
        tokens.pop(0)  # Pop the tag name.

        def make_variable(name):
            return template.Variable(name)

        def not_using(bit):
            return bit != "using"

        template_name_variables = map(make_variable, filter(
            not_using,
            takewhile(not_using, tokens)))
        hint_provider_variables = map(make_variable, filter(
            not_using,
            dropwhile(not_using, tokens)))

        return cls(template_name_variables, hint_provider_variables)


register.tag('hinted_include', HintedIncludeNode.parse)
