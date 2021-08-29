import emoji
from django import template
from django.template.defaultfilters import stringfilter
from telegram.utils.helpers import escape_markdown as telegram_escape

register = template.Library()


@register.filter
@stringfilter
def escape_markdown(value: str):
    return telegram_escape(value, version=2)


@register.filter
@stringfilter
def emojize(value: str):
    return emoji.emojize(value)
