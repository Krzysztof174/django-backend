from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import TestCase

from accounts.models import DEFAULT_MAX_LOANS, Profile
from accounts.roles import ALL_ROLES

User = get_user_model()


class ProfileTests(TestCase):
    def test_profile_is_created_for_new_user(self):
        user = User.objects.create_user(username="anna", password="pass")

        self.assertEqual(user.profile.max_loans, DEFAULT_MAX_LOANS)

    def test_profile_is_not_duplicated_on_user_update(self):
        user = User.objects.create_user(username="anna", password="pass")
        user.first_name = "Anna"
        user.save()

        self.assertEqual(Profile.objects.filter(user=user).count(), 1)

    def test_str_contains_username(self):
        user = User.objects.create_user(username="anna", password="pass")

        self.assertEqual(str(user.profile), "Profile of anna")


class RoleTests(TestCase):
    def test_role_groups_exist(self):
        existing = set(Group.objects.values_list("name", flat=True))

        self.assertTrue(set(ALL_ROLES).issubset(existing))
