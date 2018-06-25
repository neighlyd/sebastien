from django.contrib import admin
from .models import Payroll
from profiles.models import Profile

# Register your models here.
class PayrollAdmin(admin.ModelAdmin):
    def get_form(self, request, obj=None, **kwargs):
        form = super(PayrollAdmin, self).get_form(request, obj, **kwargs)
        form.base_fields['employee'].queryset = Profile.objects.filter(wage__isnull=False)
        return form

admin.site.register(Payroll, PayrollAdmin)