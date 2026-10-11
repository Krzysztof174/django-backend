from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase
from django.utils import timezone

from library.models import LOAN_PERIOD_DAYS, Author, Book, Copy, Genre, Loan

User = get_user_model()


class LibraryModelTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = Author.objects.create(
            first_name="Stanislaw", last_name="Lem", birth_year=1921
        )
        cls.genre = Genre.objects.create(name="Science fiction")
        cls.book = Book.objects.create(
            title="Solaris",
            isbn="9780156027601",
            published_year=1961,
            author=cls.author,
        )
        cls.book.genres.add(cls.genre)
        cls.copy = Copy.objects.create(book=cls.book, inventory_code="SOL-1")
        cls.member = User.objects.create_user(username="anna", password="pw")


class StrRepresentationTests(LibraryModelTestCase):
    def test_str_methods(self):
        loan = Loan.objects.create(copy=self.copy, borrower=self.member)

        self.assertEqual(str(self.author), "Stanislaw Lem")
        self.assertEqual(str(self.genre), "Science fiction")
        self.assertEqual(str(self.book), "Solaris (Stanislaw Lem)")
        self.assertEqual(str(self.copy), "SOL-1 – Solaris")
        self.assertEqual(str(loan), "SOL-1 → anna")


class BookValidationTests(LibraryModelTestCase):
    def test_isbn_must_have_thirteen_digits(self):
        self.book.isbn = "12345"

        with self.assertRaises(ValidationError):
            self.book.full_clean()

    def test_published_year_cannot_be_in_future(self):
        self.book.published_year = timezone.localdate().year + 1

        with self.assertRaises(ValidationError):
            self.book.full_clean()


class LoanTests(LibraryModelTestCase):
    def test_default_due_date_is_loan_period_ahead(self):
        loan = Loan.objects.create(copy=self.copy, borrower=self.member)

        expected = timezone.localdate() + timedelta(days=LOAN_PERIOD_DAYS)
        self.assertEqual(loan.due_date, expected)
        self.assertTrue(loan.is_active)
        self.assertFalse(loan.is_overdue)

    def test_copy_cannot_have_two_active_loans(self):
        Loan.objects.create(copy=self.copy, borrower=self.member)

        with self.assertRaises(IntegrityError), transaction.atomic():
            Loan.objects.create(copy=self.copy, borrower=self.member)

    def test_returned_copy_can_be_borrowed_again(self):
        first = Loan.objects.create(copy=self.copy, borrower=self.member)
        first.returned_at = timezone.now()
        first.save()

        Loan.objects.create(copy=self.copy, borrower=self.member)

        self.assertEqual(self.copy.loans.count(), 2)

    def test_loan_is_overdue_after_due_date(self):
        loan = Loan.objects.create(
            copy=self.copy,
            borrower=self.member,
            due_date=timezone.localdate() - timedelta(days=1),
        )

        self.assertTrue(loan.is_overdue)

    def test_due_date_before_borrow_date_is_invalid(self):
        loan = Loan(
            copy=self.copy,
            borrower=self.member,
            due_date=timezone.localdate() - timedelta(days=1),
        )

        with self.assertRaises(ValidationError):
            loan.full_clean()
