{% load telegram_fmt %}
{{ ":party_popper:"|emojize }} Пакет *{{ package.name |escape_markdown }}* обновлён до версии [{{ package.last_version |escape_markdown }}]({{ package.last_version_url |escape_markdown }})\.

{% for hashtag in package.hashtags %}\#{{ hashtag }} {% endfor %}