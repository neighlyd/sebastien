from django.contrib import admin
from .models import Role, Profile

# Register your models here.
class ProfileAdmin(admin.ModelAdmin):
    filter_horizontal = ('roles',)

admin.site.register(Role)
admin.site.register(Profile, ProfileAdmin)