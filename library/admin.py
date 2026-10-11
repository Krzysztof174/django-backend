from django.contrib import admin

from library.models import Author, Book, Copy, Genre, Loan


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ("last_name", "first_name", "birth_year")
    search_fields = ("first_name", "last_name")


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


class CopyInline(admin.TabularInline):
    model = Copy
    extra = 0


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "isbn", "published_year")
    list_filter = ("genres", "published_year")
    search_fields = ("title", "isbn", "author__last_name")
    list_select_related = ("author",)
    autocomplete_fields = ("author",)
    filter_horizontal = ("genres",)
    inlines = (CopyInline,)


@admin.register(Copy)
class CopyAdmin(admin.ModelAdmin):
    list_display = ("inventory_code", "book", "condition", "status")
    list_filter = ("status", "condition")
    search_fields = ("inventory_code", "book__title", "book__isbn")
    list_select_related = ("book__author",)
    autocomplete_fields = ("book",)


@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    list_display = (
        "copy",
        "borrower",
        "borrowed_at",
        "due_date",
        "returned_at",
        "overdue",
    )
    list_filter = ("due_date", "returned_at")
    search_fields = ("copy__inventory_code", "borrower__username")
    list_select_related = ("copy__book", "borrower")
    autocomplete_fields = ("copy", "borrower")
    date_hierarchy = "borrowed_at"

    @admin.display(boolean=True, description="Overdue")
    def overdue(self, loan: Loan) -> bool:
        return loan.is_overdue
