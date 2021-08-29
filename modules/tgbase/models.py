import telegram
from django.db import models
from model_utils.models import TimeStampedModel


class UserManager(models.Manager):
    def from_tg(self, user: telegram.User):
        o, _ = self.update_or_create(
            tg_id=user.id,
            defaults={
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name,
            },
        )
        return o

    def from_update(self, update: telegram.Update):
        assert update.effective_user
        return self.from_tg(update.effective_user)


class User(TimeStampedModel):
    tg_id = models.BigIntegerField(db_index=True, unique=True)
    username = models.CharField(max_length=32)
    first_name = models.CharField(max_length=255, blank=True)
    last_name = models.CharField(max_length=255, blank=True, null=True)

    objects = UserManager()


class ChatManager(models.Manager):
    def from_tg(self, chat: telegram.Chat):
        o, _ = self.update_or_create(
            tg_id=chat.id,
            defaults={
                "type": chat.type,
                "title": chat.title,
                "username": chat.username,
            },
        )
        return o

    def from_update(self, update: telegram.Update):
        assert update.effective_chat
        return self.from_tg(update.effective_chat)


class Chat(TimeStampedModel):
    tg_id = models.BigIntegerField(db_index=True, unique=True)
    type = models.CharField(max_length=32)
    title = models.CharField(max_length=255, blank=True, null=True)
    username = models.CharField(max_length=255, blank=True, null=True)

    objects = ChatManager()


class MessageManager(models.Manager):
    def from_tg(self, message: telegram.Message):
        o, _ = self.update_or_create(
            tg_id=message.message_id,
            defaults={
                "chat": Chat.objects.from_tg(message.chat),
            },
        )
        return o


class Message(TimeStampedModel):
    tg_id = models.BigIntegerField(db_index=True)
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, null=True, related_name="messages")

    objects = MessageManager()

    class Meta:
        unique_together = [("tg_id", "chat")]
