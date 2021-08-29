import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.settings")
django.setup()


if __name__ == "__main__":
    from modules.tgbot.menu import main

    main()
