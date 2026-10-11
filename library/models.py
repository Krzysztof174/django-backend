from datetime import date, timedelta

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import (
    MaxValueValidator,
    MinValueValidator,
    RegexValidator,
)
from django.db import models
from django.db.models import F, Q
from django.utils import timezone

LOAN_PERIOD_DAYS = 14
FIRST_PRINTED_BOOK_YEAR = 1450

isbn_validator = RegexValidator(
    regex=r"^\d{13}$",
    message="ISBN must have 13 digits.",
)


def current_year() -> int:
    return timezone.localdate().year


def default_due_date() -> date:
    return timezone.localdate() + timedelta(days=LOAN_PERIOD_DAYS)


class Author(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    birth_year = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(current_year)],
    )

    class Meta:
        ordering = ["last_name", "first_name"]
        verbose_name = "author"
        verbose_name_plural = "authors"

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}"


class Genre(models.Model):
    name = models.CharField(max_length=50, unique=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "genre"
        verbose_name_plural = "genres"

    def __str__(self) -> str:
        return self.name


class Book(models.Model):
    title = models.CharField(max_length=200)
    isbn = models.CharField(
        "ISBN",
        max_length=13,
        unique=True,
        validators=[isbn_validator],
    )
    published_year = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(FIRST_PRINTED_BOOK_YEAR),
            MaxValueValidator(current_year),
        ],
    )
    author = models.ForeignKey(
        Author,
        on_delete=models.PROTECT,
        related_name="books",
    )
    genres = models.ManyToManyField(Genre, related_name="books", blank=True)

    class Meta:
        ordering = ["title"]
        verbose_name = "book"
        verbose_name_plural = "books"

    def __str__(self) -> str:
        return f"{self.title} ({self.author})"


class Copy(models.Model):
    class Condition(models.TextChoices):
        NEW = "new", "New"
        GOOD = "good", "Good"
        WORN = "worn", "Worn"
        DAMAGED = "damaged", "Damaged"

    class Status(models.TextChoices):
        AVAILABLE = "available", "Available"
        BORROWED = "borrowed", "Borrowed"
        WITHDRAWN = "withdrawn", "Withdrawn"

    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name="copies",
    )
    inventory_code = models.CharField(max_length=20, unique=True)
    condition = models.CharField(
        max_length=10,
        choices=Condition,
        default=Condition.GOOD,
    )
    status = models.CharField(
        max_length=10,
        choices=Status,
        default=Status.AVAILABLE,
    )

    class Meta:
        ordering = ["inventory_code"]
        verbose_name = "copy"
        verbose_name_plural = "copies"

    def __str__(self) -> str:
        return f"{self.inventory_code} – {self.book.title}"


class Loan(models.Model):
    copy = models.ForeignKey(
        Copy,
        on_delete=models.PROTECT,
        related_name="loans",
    )
    borrower = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="loans",
    )
    borrowed_at = models.DateTimeField(auto_now_add=True)
    due_date = models.DateField(default=default_due_date)
    returned_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-borrowed_at"]
        verbose_name = "loan"
        verbose_name_plural = "loans"
        constraints = [
            models.UniqueConstraint(
                fields=["copy"],
                condition=Q(returned_at__isnull=True),
                name="unique_active_loan_per_copy",
                violation_error_message="Copy is already on loan.",
            ),
            models.CheckConstraint(
                condition=Q(returned_at__isnull=True)
                | Q(returned_at__gte=F("borrowed_at")),
                name="returned_after_borrowed",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.copy.inventory_code} → {self.borrower.get_username()}"

    @property
    def is_active(self) -> bool:
        return self.returned_at is None

    @property
    def is_overdue(self) -> bool:
        return self.is_active and self.due_date < timezone.localdate()

    def clean(self) -> None:
        borrowed_on = (
            timezone.localdate(self.borrowed_at)
            if self.borrowed_at
            else timezone.localdate()
        )
        if self.due_date and self.due_date < borrowed_on:
            raise ValidationError(
                {"due_date": "Due date cannot be before the borrow date."}
            )
