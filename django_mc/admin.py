from django import forms
from django.utils.translation import ugettext_lazy as _
from django.contrib import admin
from .models import ComponentBaseMixin, Layout, Region


class RegionForm(forms.ModelForm):
    class Meta:
        model = Region
        fields = (
            'name',
            'slug',
            'component_extend_rule',
            'available_components',)

    def clean_available_components(self):
        components = self.cleaned_data['available_components']
        if components:
            for ct in components:
                model = ct.model_class()
                if not model or not issubclass(model, ComponentBaseMixin):
                    raise forms.ValidationError(_(
                        '{0} is not a valid component.').format(ct))
        return components


class RegionAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug',)
    filter_horizontal = ('available_components',)
    form = RegionForm


if not Layout._meta.swapped:
    admin.site.register(Layout)
    admin.site.register(Layout.RegionComponent)
admin.site.register(Region, RegionAdmin)
