from django.db import models
from django.core.urlresolvers import reverse

class Genre(models.Model):
    """
    Models representing a book genre (e.g. military history, pole dancing)
    """
    name = models.CharField(max_length=200, help_text="Enter a book genre (e.g. Chemistry, Romance)")
    
    def __str__(self):
        """
        How the model shows up in, for instance, the Admin site
        """
        return self.name
        
class Book(models.Model):
    """
    Model representing a book (but not a specific copy of a book)
    """
    title = models.CharField(max_length=200)
    # Foreign Key because author can have many books, but our limited view allows one author per book
    # Author as string rather than object because we haven't defined the Author model yet :\
    author = models.ForeignKey('Author', on_delete=models.SET_NULL, null=True)
    summary = models.TextField(max_length=1000, help_text="Please enter a BRIEF description of the book")
    # Declaring the ISBN label here because we don't want it to show up as Isbn
    isbn = models.CharField('ISBN', max_length=13, help_text='13-character <a href="https://www.isbn-international.org/content/what-isbn">ISBN number</a>')
    # Many to Many because many book can have many genres
    # Note we declared Genre above so this is okay to declare now
    genre = models.ManyToManyField(Genre, help_text="Select a genre for this book")
    
    def __str__(self):
        """
        String representing the model object
        """
        
        return self.title
        
    def get_absolute_url(self):
        """
        Returns the URL to access a particular book instance
        """
        return reverse('book-detail', args=[str(self.id)])
    
import uuid # for uniqueness

class BookInstance(models.Model):
    """
    Specific copy of a book that can be borrowed
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, help_text="Unique ID for this book across the whole library")
    # a copy cannot be two books at once
    book = models.ForeignKey(Book, on_delete=models.SET_NULL, null=True)
    imprint = models.CharField(max_length=200)
    due_back = models.DateField(null=True, blank=True)
    LOAN_STATUS = (
        ('m', 'Maintenance'),
        ('o', 'On Loan'),
        ('a', 'Available'),
        ('r', 'Reserved'),
        ('p', 'Between Matter Phases'),
        ('x', 'Trapped in Dimension X'),
        ('k', 'Not Yet Provided By The Free Market')
    )
    
    status = models.CharField(max_length=1, choices=LOAN_STATUS, blank=True, default='m', help_text='Book availability')
    
    class Meta:
        ordering = ['due_back']
        
    def __str__(self):
        """
        String for representing the model object
        """
        return '%s (%s)' % (self.id, self.book.title)
        
class Author(models.Model):
    """
    An author of a book
    """
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField(null=True, blank=True)
    date_of_death = models.DateField('Died', null=True, blank=True)
    
    def get_absolute_url(self):
        """
        Returns the url to access a partiular instance of the author
        """
        return reverse('author-detail', args=[str(self.id)])
        
    def __str__(self):
        """
        String representing the model object
        """
        return '%s, %s' % (self.last_name, self.first_name) 