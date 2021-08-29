import datetime
from time import sleep

import httpx
from celery import shared_task
from django.conf import settings
from django.db import transaction
from django.db.models import Q
from django.template.loader import get_template
from django.utils import timezone
from lxml import html
from telegram import ParseMode
from telegram.ext import Defaults, ExtBot
from tqdm import tqdm

from modules.packages.backends.cargo import iter_metadata_files, parse_metadata
from modules.packages.backends.pypi import get_versions
from modules.packages.models import Package, PythonPackage, RustPackage
from modules.tgbot.models import TrackedPythonPackage, TrackedRustPackage

bot = ExtBot(token=settings.TELEGRAM_TOKEN, defaults=Defaults(parse_mode=ParseMode.MARKDOWN_V2))


@shared_task
def update_python_index():
    response = httpx.get("https://pypi.org/simple/")
    tree = html.fromstring(response.content)

    index_packages = {package.attrib["href"][8:-1]: package.text for package in tree.xpath("//a")}
    existing_slugs = set(PythonPackage.objects.values_list("slug", flat=True))

    new_slugs = set(index_packages.keys()) - existing_slugs

    for new_slug in tqdm(new_slugs, total=len(new_slugs)):
        PythonPackage.objects.create(slug=new_slug, name=index_packages[new_slug])


def broadcast_notification(package: Package, chat_ids: list[int]):
    for chat_id in chat_ids:
        bot.send_message(chat_id=chat_id, text=get_template("update_post.md").render({"package": package}))
        sleep(0.1)


@shared_task
@transaction.atomic
def update_crates_index():
    packages = {package.slug: package for package in RustPackage.objects.filter(enabled=True)}
    disabled_packages = set(RustPackage.objects.filter(enabled=False).values_list("slug", flat=True))

    for slug, metadata in iter_metadata_files(disabled_packages):
        if slug in disabled_packages:
            continue

        name, version, version_pre = parse_metadata(metadata)
        # print(f"{slug=} {name=} {version=} {version_pre=}")

        if slug in packages:
            package = packages[slug]
            package.name = name
        else:
            package = RustPackage(slug=slug, name=name, last_version=version, last_prerelease=version_pre)

        newversion = package.update_version(version, version_pre)
        notify = package.last_updated is not None and newversion
        package.last_updated = timezone.now()
        package.save()

        if notify:
            broadcast_notification(
                package=package,
                chat_ids=TrackedRustPackage.objects.filter(package=package).values_list("chat__tg_id", flat=True),
            )


@shared_task
@transaction.atomic
def update_python_versions():
    for package in PythonPackage.objects.filter(
        Q(enabled=True)
        & (Q(last_updated__lte=timezone.now() - datetime.timedelta(hours=1)) | Q(last_updated__isnull=True))
    ):
        version, version_pre = get_versions(package)

        newversion = package.update_version(version, version_pre)
        notify = package.last_updated is not None and newversion
        package.last_updated = timezone.now()
        package.save()

        if notify:
            broadcast_notification(
                package=package,
                chat_ids=TrackedPythonPackage.objects.filter(package=package).values_list("chat__tg_id", flat=True),
            )
