from django.shortcuts import render


from .models import Book, Author, BookInstance, Genre

def index(request):
    """
    A barebones home page
    """
    # Generate counts of some of the main objects
    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()
    # Available books
    num_instances_available = BookInstance.objects.filter(status__exact='a').count()
    num_authors = Author.objects.all().count()
    
    # Render the HTML
    return render(
        request,
        'base_generic.html', 
        context = {'num_books':num_books, 'num_instances': num_instances, 'num_instances_available': num_instances_available, 'num_authors': num_authors},
    )