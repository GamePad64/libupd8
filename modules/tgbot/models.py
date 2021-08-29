from django.db import models

from modules.packages.models import PythonPackage, RustPackage
from modules.tgbase.models import Chat


class TrackedPythonPackage(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE)
    package = models.ForeignKey(PythonPackage, on_delete=models.CASCADE)


class TrackedRustPackage(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE)
    package = models.ForeignKey(RustPackage, on_delete=models.CASCADE)
