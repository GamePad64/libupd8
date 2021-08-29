from django.contrib import admin

from modules.tgbot.models import TrackedPythonPackage, TrackedRustPackage


@admin.register(TrackedPythonPackage)
class TrackedPythonPackageAdmin(admin.ModelAdmin):
    list_display = (
        "chat",
        "package",
    )
    raw_id_fields = ("package",)


@admin.register(TrackedRustPackage)
class TrackedRustPackageAdmin(admin.ModelAdmin):
    list_display = (
        "chat",
        "package",
    )
    raw_id_fields = ("package",)
