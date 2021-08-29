import json

import httpx
from packaging.version import parse

from modules.packages.models import PythonPackage


def get_versions(package: PythonPackage) -> tuple[str, str]:
    response = httpx.get(package.package_json_url)
    response.raise_for_status()

    j = json.loads(response.text.encode(response.encoding or "UTF-8"))

    releases = [parse(release) for release in j.get("releases", [])]
    version = max([r for r in releases if not r.is_prerelease], default="")
    pre_version = max([r for r in releases if r.is_prerelease], default="")

    return str(version), str(pre_version)
