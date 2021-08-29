from django.contrib import admin

from modules.tgbase.models import Chat, Message, User

admin.site.register(Message)


@admin.register(User)
class ItemAdmin(admin.ModelAdmin):
    list_display = ("username", "first_name", "last_name")


@admin.register(Chat)
class ChatAdmin(admin.ModelAdmin):
    list_display = ("tg_id", "username", "title", "type")
