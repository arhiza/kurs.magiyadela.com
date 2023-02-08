from django.contrib import admin

from .models import SiteSettings, Profile


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ["key", "value"]


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ["user", "name_hint", "name_note", "is_verified"]
    fields = ["name_hint", "name_note"]
    
