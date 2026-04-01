from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.hashers import make_password
from .models import Admin
from Location.models import Location
from Dealer.models import Dealer
from Pos.models import Pos, User

class EditLocationViewTest(TestCase):
    def setUp(self):
        # Create test admin user
        self.admin = Admin.objects.create(
            username='testadmin',
            password=make_password('password'),
            email='admin@test.com'
        )
        # Create test location
        self.location = Location.objects.create(
            location_name='Test Location',
            username='testlocation',
            email_address='location@test.com',
            category='Retail',
            city='Test City',
            province='Test Province',
            is_active=True
        )
        # Create test dealer
        self.dealer = Dealer.objects.create(
            username='testdealer',
            firstname='Test',
            lastname='Dealer',
            phone_number='1234567890',
            email_address='dealer@test.com',
            password=make_password('password'),
            is_active=True
        )
        # Create test POS device
        self.pos = Pos.objects.create(
            pos_name='Test POS',
            pos_code='TP001',
            dealer=self.dealer,
            location=self.location,
            is_active=True
        )
        self.client = Client()

    def test_edit_location_view_requires_login(self):
        # Test that the view requires admin login
        response = self.client.get(reverse('edit_location', args=[self.location.id]))
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_edit_location_view_with_login(self):
        # Simulate admin login
        session = self.client.session
        session['admin_logged_in'] = True
        session['admin_username'] = self.admin.username
        session.save()

        response = self.client.get(reverse('edit_location', args=[self.location.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin/edit_location.html')
        # Check that context contains dealers and pos_devices
        self.assertIn('dealers', response.context)
        self.assertIn('pos_devices', response.context)
        self.assertIn(self.dealer, response.context['dealers'])
        self.assertIn(self.pos, response.context['pos_devices'])

    def test_edit_location_post_valid_data(self):
        # Simulate admin login
        session = self.client.session
        session['admin_logged_in'] = True
        session['admin_username'] = self.admin.username
        session.save()

        data = {
            'location_name': 'Updated Location',
            'username': 'updatedlocation',
            'email_address': 'updated@test.com',
            'category': 'Service',
            'city': 'Updated City',
            'province': 'Updated Province',
            'is_active': True,
            'password': '',
            'confirm_password': ''
        }
        response = self.client.post(reverse('edit_location', args=[self.location.id]), data)
        self.assertEqual(response.status_code, 302)  # Redirect after success
        self.location.refresh_from_db()
        self.assertEqual(self.location.location_name, 'Updated Location')

    def test_edit_location_post_invalid_data(self):
        # Simulate admin login
        session = self.client.session
        session['admin_logged_in'] = True
        session['admin_username'] = self.admin.username
        session.save()

        data = {
            'location_name': '',  # Invalid: required field empty
            'username': 'updatedlocation',
            'email_address': 'updated@test.com',
            'category': 'Service',
            'city': 'Updated City',
            'province': 'Updated Province',
            'is_active': True,
            'password': '',
            'confirm_password': ''
        }
        response = self.client.post(reverse('edit_location', args=[self.location.id]), data)
        self.assertEqual(response.status_code, 200)  # Stay on page with errors
        self.assertFormError(response, 'form', 'location_name', 'This field is required.')

class AddPosViewTest(TestCase):
    def setUp(self):
        # Create a test admin
        self.admin = Admin.objects.create(
            username='testadmin',
            password=make_password('password')
        )
        # Create a test location
        self.location = Location.objects.create(
            location_name='Test Location',
            username='testlocation',
            email_address='location@test.com',
            category='Retail',
            city='Test City',
            province='Test Province'
        )
        # Create a test user to assign to the POS
        self.user = User.objects.create(
            username='testuser',
            password='password'
        )
        self.client = Client()
        self.add_pos_url = reverse('add_pos', args=[self.location.id])

    def test_add_pos_view_requires_login(self):
        # This test assumes you have a login check in your view.
        # If not, it will fail, indicating a potential security issue.
        response = self.client.get(self.add_pos_url)
        # Expecting a redirect to a login page
        self.assertIn(response.status_code, [301, 302])

    def test_add_pos_get_request(self):
        # Simulate admin login
        session = self.client.session
        session['admin_logged_in'] = True
        session['admin_username'] = self.admin.username
        session.save()

        response = self.client.get(self.add_pos_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin/add_user_pos.html')
        self.assertIn('form', response.context)

    def test_add_pos_post_valid_data(self):
        # Simulate admin login
        session = self.client.session
        session['admin_logged_in'] = True
        session['admin_username'] = self.admin.username
        session.save()

        pos_data = {
            'pos_name': 'New POS 1',
            'user': self.user.id,
            'is_active': True
        }
        response = self.client.post(self.add_pos_url, pos_data)

        # Check for redirect to the edit location page
        self.assertRedirects(response, reverse('edit_location', args=[self.location.id]))
        # Verify the POS device was created
        self.assertTrue(Pos.objects.filter(pos_name='New POS 1', location=self.location).exists())
