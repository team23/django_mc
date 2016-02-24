class FixedTemplateFakeComponent(object):
    def __init__(self, template_name, position=0):
        self.template_name = template_name
        self.position = position

    def resolve_component(self):
        return self

    def get_template_names(self, hint_providers, **kwargs):
        return [self.template_name]

    def get_context_data(self):
        return {}
