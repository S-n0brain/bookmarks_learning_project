from django.conf import settings
from django.db import models
from django.utils.text import slugify


class Image(models.Model):
    user = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="images_created",
    )
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, blank=True)
    url = models.URLField(max_length=2000)
    image = models.ImageField(upload_to="images/%Y/%m/%d")
    description = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True, db_index=True)
    users_like = models.ManyToManyField(
        to=settings.AUTH_USER_MODEL, related_name="images_liked", blank=True
    )

    class Meta:
        ordering = ("-created",)
        indexes = [models.Index(fields=["-created"])]

    def __str__(self) -> str:
        return self.title

    def save(self, *args, **kwargs) -> None:
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)