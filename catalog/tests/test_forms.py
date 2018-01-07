from django.test import TestCase

import datetime
from django.utils import timezone
from catalog.forms import RenewalBookForm

class RenewBookFormTest(TestCase):
    
    def test_renew_form_date_in_past(self):
        date = datetime.date.today() - datetime.timedelta(days=1)
        form_data = { 'renewal_date': date, }
        form = RenewalBookForm(data=form_data)
        self.assertFalse(form.is_valid())
        
    def test_renew_form_date_too_far_in_future(self):
        date = datetime.date.today() + datetime.timedelta(weeks=4,days=1)
        form_data = { 'renewal_date': date, }
        form = RenewalBookForm(data=form_data)
        self.assertFalse(form.is_valid())
        
    def test_renew_form_date_today(self):
        date = datetime.date.today()
        form_data = { 'renewal_date': date, }
        form = RenewalBookForm(data=form_data)
        self.assertTrue(form.is_valid())
        
    def test_renew_form_date_max(self):
        date = datetime.date.today() + datetime.timedelta(weeks=4)
        form_data = { 'renewal_date': date, }
        form = RenewalBookForm(data=form_data)
        self.assertTrue(form.is_valid())