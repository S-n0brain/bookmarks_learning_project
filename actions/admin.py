from django.contrib import admin

from actions.models import Action


@admin.register(Action)
class ActionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "verb",
        "created",
        "target_ct",
        "target_id",
    )
    list_filter = ("user", "created", "target_ct")
    search_fields = ("user__username", "verb")
