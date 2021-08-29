{% load telegram_fmt %}
{% if not python_packages and not rust_packages %}Список пакетов пуст\! Добавьте пакет командой /add{% else %}
{% if python_packages %}Пакеты PyPI \(Python\):
{% for package in python_packages %}\- [{{ package.name|escape_markdown }}]({{ package.url|escape_markdown }})
{% endfor %}{% endif %}
{% if rust_packages %}Пакеты crates\.io \(Rust\):
{% for package in rust_packages %}\- [{{ package.name|escape_markdown }}]({{ package.url|escape_markdown }})
{% endfor %}{% endif %}
{% endif %}