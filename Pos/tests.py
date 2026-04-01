from django.test import TestCase, Client as TestClient
from django.urls import reverse
from Pos.models import Pos
from Client.models import Client
from Admin.models import Transaction
from Location.models import Location

class PosCheckValidityTest(TestCase):
    def setUp(self):
        self.client = TestClient()
        self.location = Location.objects.create(
            location_name='TestLocation',
            email_address='test@location.com',
            username='loc_test',
            city='TestCity',
            province='TestProvince',
            category='TestCategory',
            password='password'
        )
        self.pos = Pos.objects.create(
            pos_name='TestPos',
            pos_code='12345',
            location=self.location 
        )
        self.user_client = Client.objects.create(
            username='testclient',
            firstname='Test',
            lastname='Client',
            password='password'
        )
        self.transaction_unused = Transaction.objects.create(
            transaction_type='purchase',
            amount=100.00,
            client=self.user_client,
            coupon_code='VALID123',
            serial_number='SERIAL123',
            is_redeemed=False
        )
        self.transaction_used = Transaction.objects.create(
            transaction_type='purchase',
            amount=50.00,
            client=self.user_client,
            coupon_code='USED123',
            serial_number='SERIAL456',
            is_redeemed=True
        )
        
        # Simulate POS login
        session = self.client.session
        session['pos_logged_in'] = True
        session['pos_id'] = self.pos.id
        session.save()

    def test_pos_check_validity_view_access(self):
        response = self.client.get(reverse('pos_check_validity'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'Pos/pos_check_validity.html')

    def test_pos_check_validity_valid_unused(self):
        response = self.client.post(reverse('pos_check_validity'), {
            'coupon_number': 'VALID123',
            'serial_number': 'SERIAL123'
        })
        self.assertEqual(response.status_code, 200)
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertIn('VALID and ready for use', str(messages[0]))
        self.assertEqual(messages[0].tags, 'success')

    def test_pos_check_validity_valid_used(self):
        response = self.client.post(reverse('pos_check_validity'), {
            'coupon_number': 'USED123',
            'serial_number': 'SERIAL456'
        })
        self.assertEqual(response.status_code, 200)
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertIn('ALREADY been used', str(messages[0]))
        self.assertEqual(messages[0].tags, 'warning')

    def test_pos_check_validity_invalid_coupon(self):
        response = self.client.post(reverse('pos_check_validity'), {
            'coupon_number': 'INVALID',
            'serial_number': 'SERIAL123'
        })
        self.assertEqual(response.status_code, 200)
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertIn('Invalid Coupon', str(messages[0]))
        self.assertEqual(messages[0].tags, 'error')

    def test_pos_check_validity_invalid_serial(self):
        response = self.client.post(reverse('pos_check_validity'), {
            'coupon_number': 'VALID123',
            'serial_number': 'WRONGSERIAL'
        })
        self.assertEqual(response.status_code, 200)
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertIn('Invalid Coupon', str(messages[0]))
        self.assertEqual(messages[0].tags, 'error')
