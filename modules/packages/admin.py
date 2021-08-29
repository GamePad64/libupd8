from django.contrib import admin

from modules.packages.models import PythonPackage, RustPackage


@admin.register(PythonPackage)
class PythonPackageAdmin(admin.ModelAdmin):
    list_display = ("slug", "name", "last_version", "last_prerelease", "last_updated", "enabled")
    search_fields = ("slug", "name")
    list_filter = ("enabled",)


@admin.register(RustPackage)
class RustPackageAdmin(admin.ModelAdmin):
    list_display = ("slug", "name", "last_version", "last_prerelease", "last_updated", "enabled")
    search_fields = ("slug", "name")
    list_filter = ("enabled",)
