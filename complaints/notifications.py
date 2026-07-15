from .models import Notification

from .models import Notification


def create_notification(user, title):

    if not user:
        return

    Notification.objects.create(
    user=user,
    title=title
    )
