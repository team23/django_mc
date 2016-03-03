from django.db import migrations


ALL_REGIONS = object()


class _ManageComponentTypeInRegions(migrations.RunPython):
    """
    Requires all migrations of ``django.contrib.contenttypes`` to be applied.
    """

    def __init__(self, component_app_label, component_model,
                 regions=ALL_REGIONS):
        self.component_app_label = component_app_label
        self.component_model = component_model
        self.regions = regions
        super(_ManageComponentTypeInRegions, self).__init__(
            self.run_forwards,
            self.run_backwards)

    def get_content_type_model(self, apps):
        return apps.get_model('contenttypes', 'ContentType')

    def get_region_model(self, apps):
        return apps.get_model('django_mc', 'Region')

    def get_component_content_type(self, apps):
        ContentType = self.get_content_type_model(apps)
        content_type, created = ContentType.objects.get_or_create(
            app_label=self.component_app_label,
            model=self.component_model)
        return content_type

    def get_regions(self, apps):
        Region = self.get_region_model(apps)
        if self.regions is ALL_REGIONS:
            return Region.objects.all()
        else:
            return Region.objects.filter(slug__in=self.regions)

    def add_to_regions(self, apps):
        content_type = self.get_component_content_type(apps)
        for region in self.get_regions(apps):
            region.available_components.add(content_type)

    def remove_from_regions(self, apps):
        content_type = self.get_component_content_type(apps)
        for region in self.get_regions(apps):
            region.available_components.remove(content_type)

    def run_forwards(self):
        raise NotImplementedError()

    def run_backwards(self):
        raise NotImplementedError()


class AddComponentTypeToRegions(_ManageComponentTypeInRegions):
    def run_forwards(self, apps, schema_editor):
        self.add_to_regions(apps)

    def run_backwards(self, apps, schema_editor):
        self.remove_from_regions(apps)


class RemoveComponentTypeFromRegions(_ManageComponentTypeInRegions):
    def run_forwards(self, apps, schema_editor):
        self.remove_from_regions(apps)

    def run_backwards(self, apps, schema_editor):
        self.add_to_regions(apps)
