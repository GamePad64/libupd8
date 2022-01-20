import json
import re
import tempfile
import zipfile
from pathlib import Path

import httpx
import semver
from tqdm import tqdm


def download_file(url, file):
    with httpx.stream("GET", url) as response:
        with tqdm(unit_scale=True, unit_divisor=1024, unit="B") as progress:
            num_bytes_downloaded = response.num_bytes_downloaded
            for chunk in response.iter_bytes():
                file.write(chunk)
                progress.update(response.num_bytes_downloaded - num_bytes_downloaded)
                num_bytes_downloaded = response.num_bytes_downloaded
        return response.headers


def parse_metadata(metadata: bytes):
    name = ""
    versions = []
    versions_pre = []

    for line in metadata.splitlines():
        j = json.loads(line)
        name = j["name"]
        if j.get("yanked", False):
            continue
        try:
            version = semver.VersionInfo.parse(j["vers"])
        except ValueError:
            # Simplified regex for ad-hoc version gathering
            match = re.match(r"(\d)(?:\.(\d)(?:\.(\d))?)?", j["vers"])
            if match:
                version = semver.VersionInfo(
                    major=int(match.group(1)), minor=int(match.group(2)), patch=int(match.group(3))
                )
            else:
                raise RuntimeError("Version is neither semver, nor parsible")

        if not version.prerelease:
            versions += [version]
        else:
            versions_pre += [version]

    return name, str(max(versions, default="")), str(max(versions_pre, default=""))


def iter_metadata_files(ignored_slugs: set[str] = None):
    ignored_slugs = ignored_slugs if ignored_slugs is not None else set()

    CRATES_IO_INDEX_ZIP = "https://github.com/rust-lang/crates.io-index/archive/refs/heads/master.zip"
    with tempfile.TemporaryFile() as cratesindex:
        download_file(CRATES_IO_INDEX_ZIP, cratesindex)

        with zipfile.ZipFile(cratesindex) as archive:
            files = [
                x.filename
                for x in archive.infolist()
                if x.filename and not x.is_dir() and not Path(x.filename).name == "config.json" and not str(Path(x.filename)).startswith(".")
            ]

            for indexfile in tqdm(files):
                path = zipfile.Path(archive, indexfile)
                if path.name in ignored_slugs:
                    continue
                yield path.name, path.read_bytes()
