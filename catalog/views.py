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
    num_books_english = Book.objects.filter(language__name='English').count()
    
    # Render the HTML
    return render(
        request,
        'index.html', 
        context = {'num_books':num_books, 'num_instances': num_instances, 'num_instances_available': num_instances_available, 'num_authors': num_authors, 'num_books_english': num_books_english},
    )
    
from django.views import generic

class BookListView(generic.ListView):
    model = Book
    paginate_by = 10
    
    # we could also just set the 'queryset' property but this gives us more flexibility
    # only list top 5
    def get_queryset(self):
        return Book.objects.all()[:5]
        
class BookDetailView(generic.DetailView):
    model =  Book