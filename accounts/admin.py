from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

from accounts.models import Profile

User = get_user_model()


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "phone", "max_loans")
    list_filter = ("max_loans",)
    search_fields = ("user__username", "user__email", "phone")
    list_select_related = ("user",)


admin.site.unregister(User)


@admin.register(User)
class UserWithProfileAdmin(UserAdmin):
    inlines = (ProfileInline,)

    def get_inlines(self, request, obj):
        return self.inlines if obj else ()
