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

from django.contrib.auth.mixins import PermissionRequiredMixin

class AllBooksLoanedListView(PermissionRequiredMixin, LoginRequiredMixin, generic.ListView):
    """
    Generic class-based view listing ALL books on loan (for librarian eyes only).
    """
    permission_required = ('catalog.can_mark_returned', )
    model = BookInstance
    template_name = 'catalog/bookinstance_list_borrowed_all.html'
    paginate_by = 10
    
    def get_queryset(self):
        return BookInstance.objects.filter(status__exact='o').order_by('due_back')
        
from django.contrib.auth.decorators import permission_required

from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
import datetime

from .forms import RenewalBookForm

@permission_required('catalog.can_renew')
def renew_book_librarian(request, pk):
    """
    View function for renewing a specific BookInstance by librarian
    """
    book_inst = get_object_or_404(BookInstance, pk=pk)
    
    # If this is a POST request then process the form data
    if request.method == 'POST':
        
        # create a new form instance and bind to data from request
        form = RenewalBookForm(request.POST)
        
        # check if the form is valid
        if form.is_valid():
            # process the CLEANED data (form errors will generate errors to render)
            # if no errors update object
            book_inst.due_back = form.cleaned_data['renewal_date']
            book_inst.save()
            
            # redirect to new url
            return HttpResponseRedirect(reverse('all-borrowed-books'))
            
    # if this is a GET request (or any other method), create the default form
    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        form = RenewalBookForm(initial={'renewal_date': proposed_renewal_date,})
    
    # done
    return render(request, 'catalog/book_renew_librarian.html', {'form': form, 'bookinst': book_inst})
