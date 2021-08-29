from django.db import models


class Package(models.Model):
    slug = models.SlugField(max_length=127, unique=True)
    name = models.CharField(max_length=127, unique=True)
    last_version = models.CharField(max_length=100, null=True, blank=True)
    last_prerelease = models.CharField(max_length=100, null=True, blank=True)
    last_updated = models.DateTimeField(null=True, db_index=True)
    enabled = models.BooleanField(default=False)

    class Meta:
        abstract = True

    def update_version(self, version: str, prerelease_version: str) -> bool:
        if (version, prerelease_version) != (self.last_version, self.last_prerelease):
            self.last_version = version
            self.last_prerelease = prerelease_version
            return True

        return False


class PythonPackage(Package):
    def __str__(self):
        return f"PyPI: {self.slug}"

    @property
    def url(self) -> str:
        return f"https://pypi.org/project/{self.name}/"

    @property
    def last_version_url(self) -> str:
        return f"{self.url}{self.last_version}/"

    @property
    def last_prerelease_url(self) -> str:
        return f"{self.url}{self.last_prerelease}/"

    @property
    def package_json_url(self) -> str:
        return f"https://pypi.org/pypi/{self.slug}/json"

    @property
    def hashtags(self) -> list[str]:
        return ["python", "pypi"]


class RustPackage(Package):
    def __str__(self):
        return f"Crates: {self.slug}"

    @property
    def url(self) -> str:
        return f"https://crates.io/crates/{self.slug}"

    @property
    def last_version_url(self) -> str:
        return f"https://crates.io/crates/{self.slug}/{self.last_version}"

    @property
    def hashtags(self) -> list[str]:
        return ["rust", "crates"]
