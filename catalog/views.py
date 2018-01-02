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
    
    # Number of visits to this view, counted in sessions variable
    num_visits = request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits + 1
    
    # Render the HTML
    return render(
        request,
        'index.html', 
        context = {'num_books':num_books, 'num_instances': num_instances, 'num_instances_available': num_instances_available, 'num_authors': num_authors, 'num_books_english': num_books_english,
            'num_visits': num_visits,
        },
    )
    
from django.views import generic

class BookListView(generic.ListView):
    model = Book
    paginate_by = 10
    
    # we could also just set the 'queryset' property but this gives us more flexibility
    # only list top 5
    # (removing because we can paginate now)
    #def get_queryset(self):
    #    return Book.objects.all()[:5]
        
class BookDetailView(generic.DetailView):
    model = Book # shorthand for queryset = Book.objects.all()
    paginate_by = 10
    
class AuthorListView(generic.ListView):
    model = Author # shorthand for queryset = Author.objects.all()
    paginate_by = 10
    
class AuthorDetailView(generic.DetailView):
    model = Author # shorthand for queryset = Author.objects.all()
    paginate_by = 10
    
from django.contrib.auth.mixins import LoginRequiredMixin

class LoanedBooksByUserListView(LoginRequiredMixin, generic.ListView):
    """
    Generic class-based view listing books on loan to logged-in user.
    """
    model = BookInstance
    template_name = 'catalog/bookinstance_list_borrowed_user.html'
    paginate_by = 10
    
    def get_queryset(self):
        return BookInstance.objects.filter(borrower = self.request.user).filter(status__exact='o').order_by('due_back')
