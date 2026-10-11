from accounts.models import Profile


def create_profile_for_new_user(sender, instance, created, **kwargs) -> None:
    if created:
        Profile.objects.create(user=instance)
