from django.contrib import admin

from .models import Image


@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "title",
        "slug",
        "url",
        "image",
        "description",
        "created",
    )
    list_filter = ("user", "created")
    raw_id_fields = ("users_like",)
    search_fields = ("slug",)
