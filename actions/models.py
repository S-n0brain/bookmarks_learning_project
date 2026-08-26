from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models


class Action(models.Model):
    user = models.ForeignKey(
        to="auth.User", related_name="actions", on_delete=models.CASCADE
    )
    verb = models.CharField(max_length=255) # move
    created = models.DateTimeField(auto_now_add=True, db_index=True)
    target_ct = models.ForeignKey(
        to=ContentType,
        blank=True,
        null=True,
        related_name="target_obj",
        on_delete=models.CASCADE,
        limit_choices_to={"model__in": ("user", "image")},
    )
    target_id = models.PositiveIntegerField(null=True, blank=True, db_index=True)
    target = GenericForeignKey("target_ct", "target_id")

    class Meta:
        ordering = ["-created"]
        indexes = [
            models.Index(fields=["target_ct", "target_id"]),
        ]


    def __str__(self) -> str:
        return f"{self.user} {self.verb}"
