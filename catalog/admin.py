from django.contrib import admin

from .models import Author, Genre, Book, BookInstance, Language


#admin.site.register(BookInstance)
@admin.register(BookInstance)
class BookInstanceAdmin(admin.ModelAdmin):
    list_display = ('book', 'status', 'borrower', 'due_back')
    list_filter = ('status', 'due_back')
    fieldsets = (
        (None, {
            'fields' : ('book', 'imprint', 'id'),
        }),
        ('Availability', {
            'fields' : ('status', 'due_back', 'borrower')
        })
    )

class BookInstanceInline(admin.TabularInline):
    model = BookInstance
    extra = 0

#admin.site.register(Book)
@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    # author is foreign key, so displays __str__ output
    list_display = ('title', 'author', 'display_genre')
    inlines = [BookInstanceInline]

class BookInline(admin.TabularInline):
    model = Book
    extra = 0

#admin.site.register(Author)
@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name', 'date_of_birth', 'date_of_death')
    fields = ['last_name', 'first_name', ('date_of_birth', 'date_of_death')]
    inlines = [BookInline]

admin.site.register(Genre)

admin.site.register(Language)