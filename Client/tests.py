from django.test import TestCase, Client as TestClient
from decimal import Decimal

from Admin.models import Transaction, Product
from Client.models import Client, Basket, BasketItem
from Dealer.models import Dealer


class CheckoutFlowTestCase(TestCase):
	def setUp(self):
		# Create client and dealer
		self.client_user = Client.objects.create(
			username='test_checkout_client', firstname='Test', lastname='Checkout',
			password='pass', email_address='checkout@test.com', phone_number='000'
		)

		self.dealer = Dealer.objects.create(
			username='test_checkout_dealer', firstname='Dealer', lastname='One',
			password='pass', email_address='dealer@test.com', phone_number='111', category='Groceries'
		)

		# Create product
		self.product = Product.objects.create(
			name='Test Product', price=Decimal('12.50'), dealer=self.dealer, category='Groceries'
		)

		# Ensure basket exists and is clean
		self.basket, _ = Basket.objects.get_or_create(client=self.client_user)
		self.basket.items.all().delete()

	def tearDown(self):
		Transaction.objects.filter(client=self.client_user).delete()
		BasketItem.objects.filter(basket=self.basket).delete()
		try:
			self.product.delete()
		except Exception:
			pass
		try:
			self.dealer.delete()
		except Exception:
			pass
		try:
			self.client_user.delete()
		except Exception:
			pass

	def test_checkout_creates_purchases_and_clears_basket(self):
		# Add items to basket
		BasketItem.objects.create(basket=self.basket, product=self.product, quantity=2)
		total_cost = self.basket.get_total()

		# Deposit to cover purchase
		Transaction.objects.create(transaction_type='deposit', amount=(total_cost + Decimal('5.00')),
								   client=self.client_user, category='Topup', description='Test deposit')

		tc = TestClient()
		# Set session values expected by views
		session = tc.session
		session['client_logged_in'] = True
		session['client_username'] = self.client_user.username
		session.save()

		resp = tc.post('/Client/checkout/')
		self.assertEqual(resp.status_code, 200)
		data = resp.json()
		self.assertEqual(data.get('status'), 'success')

		purchases = Transaction.objects.filter(client=self.client_user, transaction_type='purchase')
		self.assertGreaterEqual(purchases.count(), 1)
		self.assertEqual(self.basket.items.count(), 0)
