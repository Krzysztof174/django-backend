from django.conf import settings
from django.core.validators import (
    MaxValueValidator,
    MinValueValidator,
    RegexValidator,
)
from django.db import models

DEFAULT_MAX_LOANS = 3

phone_validator = RegexValidator(
    regex=r"^\+?\d{9,15}$",
    message="Enter 9 to 15 digits.",
)


class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    phone = models.CharField(
        max_length=16,
        blank=True,
        default="",
        validators=[phone_validator],
    )
    max_loans = models.PositiveSmallIntegerField(
        default=DEFAULT_MAX_LOANS,
        validators=[MinValueValidator(1), MaxValueValidator(10)],
    )

    class Meta:
        ordering = ["user__username"]
        verbose_name = "profile"
        verbose_name_plural = "profiles"

    def __str__(self) -> str:
        return f"Profile of {self.user.get_username()}"
