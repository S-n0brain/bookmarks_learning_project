from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models


class Profile(models.Model):
    user = models.OneToOneField(
        to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile"
    )
    date_of_birth = models.DateField(blank=True, null=True)
    photo = models.ImageField(upload_to="users/%Y/%m/%d", blank=True)

    def __str__(self) -> str:
        return f"Profile for {self.user.username}"


class Contact(models.Model):
    user_from = models.ForeignKey(
        to="auth.User",
        related_name="rel_from_set",
        on_delete=models.CASCADE,  # для пользователя, который создает взаимосвязь
    )
    user_to = models.ForeignKey(
        "auth.User",
        related_name="rel_to_set",
        on_delete=models.CASCADE,  # для пользователя, на которого есть подписка
    )
    created = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-created"]

    def __str__(self) -> str:
        return f"{self.user_from} follows {self.user_to}"


# Добавить следующее поле в User динамически
user_model = get_user_model()
user_model.add_to_class(
    name="following",
    value=models.ManyToManyField(
        "self", through=Contact, related_name="followers", symmetrical=False
    ),
)
