import datetime

from django.contrib.contenttypes.models import ContentType
from django.utils import timezone

from actions.models import Action

DUPLICATE_ACTION_WINDOW_SECONDS = 60


def create_action(user, verb, target=None):
    now = timezone.now()
    last_minute = now - datetime.timedelta(seconds=DUPLICATE_ACTION_WINDOW_SECONDS)
    similar_actions = Action.objects.filter(
        user_id=user.id, verb=verb, created__gte=last_minute
    )
    if target:
        target_ct = ContentType.objects.get_for_model(target)
        similar_actions = similar_actions.filter(
            target_ct=target_ct, target_id=target.id
        )
    if similar_actions.exists():
        return False
    Action.objects.create(user=user, verb=verb, target=target)
    return True
