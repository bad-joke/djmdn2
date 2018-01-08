from django.test import TestCase

from catalog.models import Author
from django.core.urlresolvers import reverse

class AuthorListViewTest(TestCase):
    
    @classmethod
    def setUpTestData(cls):
        # create 13 authors for pagination test
        number_of_authors = 13
        for author_num in range(number_of_authors):
            Author.objects.create(first_name='Test Author %s' % author_num, last_name='Surname %s' % author_num,)
            
    def test_view_url_exists_at_desired_location(self):
        resp = self.client.get('/catalog/authors/')
        self.assertEqual(resp.status_code, 200)
        
    def test_view_url_accessible_by_name(self):
        resp = self.client.get(reverse('authors'))
        self.assertEqual(resp.status_code, 200)
        
    def test_view_uses_correct_template(self):
        resp = self.client.get(reverse('authors'))
        self.assertEqual(resp.status_code, 200)
        
        self.assertTemplateUsed(resp, 'catalog/author_list.html')
        
    def test_pagination_is_ten(self):
        resp = self.client.get(reverse('authors'))
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('is_paginated' in resp.context)
        self.assertTrue(resp.context['is_paginated'] == True)
        self.assertTrue(len(resp.context['author_list'])==10)
        
    def test_lists_all_authors(self):
        # get second page and confirm it has exactly 3 authors (we created 13 above)
        resp = self.client.get(reverse('authors') + '?page=2')
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('is_paginated' in resp.context)
        self.assertTrue(resp.context['is_paginated'] == True)
        self.assertTrue(len(resp.context['author_list'])==3)
    
from django.utils import timezone

from catalog.models import BookInstance, Book, Genre, Language
from django.contrib.auth.models import User # required to assign User as borrower
import datetime

class LoanedBookInstancesByUserListViewTest(TestCase):
    
    def setUp(self):
        # create two users
        testuser1 = User.objects.create_user(username='testuser1', password='12345')
        testuser1.save()
        testuser2 = User.objects.create_user(username='testuser2', password='12345')
        testuser2.save()
        
        # create a book
        test_author = Author.objects.create(first_name='FirstName', last_name='LastName')
        test_genre = Genre.objects.create(name='Fantasy')
        test_language = Language.objects.create(name='English')
        test_book = Book.models.create(title='Test Book Title', summary='A test book summary', isbn='1234567890123',
            author=test_author, language=test_language)
        # create genre as post step
        genre_objects_for_book = Genre.objects.all()
        test_book.genre.set(genre_objects_for_book) # direct assignment for many-to-many... we would have to filter if more than one
        test_book.save()
        
        # create 30 book instance copies
        number_of_book_copies = 30
        for book_copy in range(number_of_book_copies):
            return_date = timezone.now() + datetime.timedelta(days=book_copy%5)
            if book_copy % 2:
                the_borrower = testuser1
            else:
                the_borrower = testuser2
            status = 'm'
            BookInstance.objects.create(book=test_book, imprint='Test Imprint', due_back=return_date, borrower=the_borrower, status=status)
        
        def test_redirect_if_not_logged_in(self):
            resp = self.client.get(reverse('borrowed-books'))
            self.assertRedirects(resp, '/accounts/login/?next=/catalog/mybooks/')
            
        def test_logged_in_uses_correct_template(self):
            login = self.client.login(username='testuser1', password='12345')
            resp = self.client.get(reverse('borrowed-books'))
            
            # check if our user is logged in
            self.assertEqual(str(resp.context['user']), 'testuser1')
            # check that we got a success response
            self.assertEqual(resp.status_code, 200)
            
            # check that we used the correct template
            self.assertTemplateUsed(resp, 'catalog/bookinstance_list_borrowed_user.html')
        
        def test_only_self_borrowed_books_in_list(self):
            login = self.client.login(username='testuser1', password='12345')
            resp = self.client.get(reverse('borrowed-books'))
            
            # check our user is logged in
            self.assertEqual(str(resp.context['user']), 'testuser1')
            # check that we got a success response
            self.assertEqual(resp.status_code, 200)
            
            # check that we initially don't have any books in list (on loan)
            self.assertTrue('bookinstance_list' in resp.context)
            self.assertEqual(len(resp.context['bookinstance_list']), 0)
            
            # now change all books to be on loan
            get_ten_books = BookInstance.objects.all()[:10]
            
            for copy in get_ten_books:
                copy.status = 'o'
                copy.save()
                
            # check that we have now borrowed 10 books
            resp.self.client.get(reverse('borrowed-books'))
            # check our user is logged in
            self.assertEqual(str(resp.context['user']), 'testuser1')
            # check that we got a success response
            self.assertEqual(resp.status_code, 200)
            
            # confirm that we got the book instances
            self.assertTrue('bookinstance_list' in resp.context)
            
            # confirm that all these books were borrowed by testuser1 and are on loan
            for bookitem in resp.context['bookinstance_list']:
                self.assertEqual(resp.context['user'], bookitem.borrower)
                self.assertEqual('o', bookitem.status)
                
        def test_pages_ordered_by_due_date(self):
            
            #change all books to be on loan
            for copy in BookInstance.objects.all():
                copy.status = 'o'
                copy.save()
                
            login = self.client.login(username='testuser1', password='12345')
            resp = self.client.get(reverse('borrowed-books'))
            
            # check our user is logged in
            self.assertEqual(str(resp.context['user']), 'testuser1')
            # check that we got a status response
            self.assertEqual(resp.status_code, 200)
            
            # confirm that only 10 items are displayed due to pagination
            self.assertEqual(len(resp.context['bookinstance_list']), 10)
            
            last_date = 0
            for copy in resp.context['bookinstance_list']:
                if last_date == 0:
                    last_date = copy.due_back
                else:
                    self.assertTrue(last_date <= copy.due_back)
            
        
        