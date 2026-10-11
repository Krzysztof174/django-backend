from django.apps import AppConfig
from django.conf import settings
from django.db.models.signals import post_save


class AccountsConfig(AppConfig):
    name = "accounts"

    def ready(self) -> None:
        from accounts.signals import create_profile_for_new_user

        post_save.connect(
            create_profile_for_new_user,
            sender=settings.AUTH_USER_MODEL,
            dispatch_uid="accounts.create_profile_for_new_user",
        )
