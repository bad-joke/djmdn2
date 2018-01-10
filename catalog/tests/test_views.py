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
            
from django.contrib.auth.models import Permission
        
class RenewBookInstancesViewTest(TestCase):
    
    def setUp(self):
        # create new user
        test_user1 = User.objects.create_user(username='testuser1', password='12345')
        test_user1.save()
        
        test_user2 = User.objects.create_user(username='testuser2', password='12345')
        test_user2.save()
        
        # give permissions to only one user
        permission = Permission.objects.get(name='Renew book due date')
        test_user2.user_permissions.add(permission)
        test_user2.save()
        
        # create a book
        test_author = Author.objects.create(first_name='Test', last_name='Author')
        test_genre = Genre.objects.create(name='Fantasy')
        test_language = Language.objects.create(name='Test Language')
        test_book = Book.objects.create(title='Test Book Title', summary='A test book summary', isbn='1234567890123', 
            author=test_author, language=test_language,)
        # create genre as post step
        genre_objects_for_book = Genre.objects.all()
        test_book.genre.set(genre_objects_for_book)
        test_book.save()
        
        # create book instance for test_user1
        return_date = datetime.date.today()  + datetime.timedelta(days=5)
        self.test_bookinstance1 = BookInstance.objects.create(book=test_book, imprint='Test Imprint', borrower=test_user1, status='o')
        
        # create book instance for test_user2
        return_date = datetime.date.today() + datetime.timedelta(days=5)
        self.test_bookinstance2 = BookInstance.objects.create(book=test_book, imprint='Test Imprint', borrower=test_user2, status='o')
        
    def test_redirect_if_not_logged_in(self):
        resp = self.client.get(reverse('renew-book-librarian', kwargs={'pk':self.test_bookinstance1.pk,}))
        # manually check redirect (can't use assertRedirect, because redirect URL is unpredictable)
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(resp.url.startswith('/accounts/login/'))
        
    def test_redirect_if_logged_in_but_not_correct_permission(self):
        login = self.client.login(username='testuser1', password='12345')
        resp = self.client.get(reverse('renew-book-librarian', kwargs={'pk':self.test_bookinstance1.pk,}))
        
        # manually check redirect (can't use assertRedirect, because redirect URL is unpredictable)
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(resp.url.startswith('/accounts/login/'))
        
    def test_logged_in_with_permission_borrowed_book(self):
        login = self.client.login(username='testuser2', password='12345')
        resp = self.client.get(reverse('renew-book-librarian', kwargs={'pk':self.test_bookinstance2.pk,}))
        
        # check that it lets us login - this is our book and we have the right permissions
        self.assertEqual(resp.status_code, 200)
        
    def test_logged_in_with_permission_another_users_book(self):
        login = self.client.login(username='testuser2', password='12345')
        resp = self.client.get(reverse('renew-book-librarian', kwargs={'pk':self.test_bookinstance1.pk,}))
        
        # check that lets us view, since we're a librarian should be able to view any book
        # (if needed, change librarian group permissions using admin site)
        self.assertEqual(resp.status_code, 200)
        
    def test_HTTP404_for_invalid_book_if_logged_in(self):
        import uuid
        test_uid = uuid.uuid4() # unlikely we'll get a collision
        login = self.client.login(username='testuser2', password='12345')
        resp = self.client.get(reverse('renew-book-librarian', kwargs={'pk':test_uid,}))
        self.assertEqual(resp.status_code, 404)
        
    def test_uses_correct_template(self):
        login = self.client.login(username='testuser2', password='12345')
        resp = self.client.get(reverse('renew-book-librarian', kwargs={'pk':self.test_bookinstance1.pk,}))
        self.assertEqual(resp.status_code, 200)
        
        # check that we used the correct template
        self.assertTemplateUsed(resp, 'catalog/book_renew_librarian.html')
        
    def test_form_renewal_date_initially_has_three_weeks_in_future(self):
        login = self.client.login(username='testuser2', password='12345')
        resp = self.client.get(reverse('renew-book-librarian', kwargs={'pk':self.test_bookinstance1.pk,}))
        self.assertEqual(resp.status_code, 200)
        
        date_3_weeks_in_future = datetime.date.today() + datetime.timedelta(weeks=3)
        self.assertEqual(resp.context['form'].initial['renewal_date'], date_3_weeks_in_future)