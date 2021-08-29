import logging
from typing import Any

import sentry_sdk
from django.conf import settings
from django.db.models import Q
from django.template.loader import get_template
from telegram import ParseMode, Update
from telegram.ext import (
    CallbackContext,
    CommandHandler,
    ConversationHandler,
    Defaults,
    Dispatcher,
    ExtBot,
    Updater,
)
from telegram.utils.helpers import escape_markdown

from modules.packages.models import Package, PythonPackage, RustPackage
from modules.tgbase.models import Chat
from modules.tgbase.models import Chat as DbChat
from modules.tgbase.models import User
from modules.tgbot.models import TrackedPythonPackage, TrackedRustPackage

logger = logging.getLogger(__name__)


# Callbacks
def cmd_start(update: Update, context: CallbackContext) -> None:
    db_chat = DbChat.objects.from_update(update)
    db_user = User.objects.from_update(update)

    update.effective_message.reply_text(get_template("start.md").render({}), disable_web_page_preview=True)

    return ConversationHandler.END


def cmd_add(update: Update, context: CallbackContext) -> None:
    db_chat = Chat.objects.from_update(update)

    try:
        provider, package = context.args
    except ValueError:
        update.effective_message.reply_text(escape_markdown("Введите /add <Индекс> <Название>", version=2))
        raise

    try:
        if provider == "pypi":
            package_obj = PythonPackage.objects.get(Q(slug__iexact=package) | Q(name__iexact=package))

            _, track_created = TrackedPythonPackage.objects.update_or_create(chat=db_chat, package=package_obj)
        elif provider == "crates":
            package_obj = RustPackage.objects.get(Q(slug__iexact=package) | Q(name__iexact=package))

            _, track_created = TrackedRustPackage.objects.update_or_create(chat=db_chat, package=package_obj)
        else:
            update.effective_message.reply_text("Пока поддерживаются только `pypi` и `crates` :\(")
            return
    except (PythonPackage.DoesNotExist, RustPackage.DoesNotExist):
        update.effective_message.reply_text("Нет такого пакета в индексе\!")
        raise

    if track_created:
        update.effective_message.reply_text(f"Пакет {escape_markdown(package_obj.name, version=2)} добавлен")
        package_obj.enabled = True
        package_obj.save()


def cmd_remove(update: Update, context: CallbackContext) -> None:
    db_chat = Chat.objects.from_update(update)

    try:
        provider, package = context.args
    except ValueError:
        update.effective_message.reply_text(escape_markdown("Введите /remove pypi <Название>", version=2))
        raise

    try:
        if provider == "pypi":
            package_obj = TrackedPythonPackage.objects.get(
                Q(chat=db_chat) & (Q(package__slug__iexact=package) | Q(package__name__iexact=package))
            )
        elif provider == "crates":
            package_obj = TrackedRustPackage.objects.get(
                Q(chat=db_chat) & (Q(package__slug__iexact=package) | Q(package__name__iexact=package))
            )
        else:
            update.effective_message.reply_text("Пока поддерживаются только `pypi` и `crates` :\(")
            return
    except (PythonPackage.DoesNotExist, RustPackage.DoesNotExist):
        update.effective_message.reply_text("Нет такого пакета в индексе\!")
        raise

    package_obj.delete()
    update.effective_message.reply_text("Пакет удалён\!")


def cmd_list(update: Update, context: CallbackContext) -> None:
    db_chat = Chat.objects.from_update(update)
    python_packages = PythonPackage.objects.filter(trackedpythonpackage__chat=db_chat)
    rust_packages = RustPackage.objects.filter(trackedrustpackage__chat=db_chat)

    update.effective_message.reply_text(
        get_template("list.md").render({"python_packages": python_packages, "rust_packages": rust_packages}),
        disable_web_page_preview=True,
    )


def error_callback(update: Any, context: CallbackContext) -> None:
    sentry_sdk.capture_exception(error=context.error)
    raise context.error


def main():
    logger.info("Starting server")
    bot = ExtBot(token=settings.TELEGRAM_TOKEN, defaults=Defaults(parse_mode=ParseMode.MARKDOWN_V2))
    updater = Updater(bot=bot, use_context=True)

    dp: Dispatcher = updater.dispatcher

    dp.add_handler(CommandHandler("add", cmd_add))
    dp.add_handler(CommandHandler("list", cmd_list))
    dp.add_handler(CommandHandler("remove", cmd_remove))
    dp.add_handler(CommandHandler("help", cmd_start))
    dp.add_handler(CommandHandler("start", cmd_start))
    dp.add_error_handler(error_callback)

    updater.start_polling()
    updater.idle()
