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
    