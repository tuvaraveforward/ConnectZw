import os
import django
import sys
from decimal import Decimal

# Ensure project root on path and Django configured
sys.path.append(r'c:\Users\Forward Tuvarave\Desktop\Django\Project1')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Project1.settings')
django.setup()

from django.test import Client as TestClient
from Admin.models import Transaction, Product
from Client.models import Client, Basket, BasketItem
from Dealer.models import Dealer


def test_checkout_flow():
    print("Setting up test data...")
    # Create client and dealer
    client_user, _ = Client.objects.get_or_create(username='test_checkout_client', defaults={
        'firstname': 'Test', 'lastname': 'Checkout', 'password': 'pass', 'email_address': 'checkout@test.com', 'phone_number': '000'
    })

    dealer, _ = Dealer.objects.get_or_create(username='test_checkout_dealer', defaults={
        'firstname': 'Dealer', 'lastname': 'One', 'password': 'pass', 'email_address': 'dealer@test.com', 'phone_number': '111', 'category': 'Groceries'
    })

    # Create product
    product, _ = Product.objects.get_or_create(name='Test Product', dealer=dealer, defaults={
        'price': Decimal('12.50'), 'category': 'Groceries'
    })

    # Ensure clean basket
    basket, _ = Basket.objects.get_or_create(client=client_user)
    basket.items.all().delete()

    # Add one item to basket
    item = BasketItem.objects.create(basket=basket, product=product, quantity=2)
    total_cost = basket.get_total()
    print(f"Basket total: {total_cost}")

    # Create deposit to cover purchase
    Transaction.objects.create(transaction_type='deposit', amount=(total_cost + Decimal('5.00')),
                               client=client_user, category='Topup', description='Test deposit')

    # Use Django test client and set session values expected by views
    tc = TestClient()
    session = tc.session
    session['client_logged_in'] = True
    session['client_username'] = client_user.username
    session.save()

    print("Posting to checkout endpoint...")
    resp = tc.post('/Client/checkout/')
    try:
        data = resp.json()
    except Exception:
        data = {'status': 'error', 'content': resp.content.decode('utf-8')}

    print('Response:', data)

    # Verify that purchase transactions were created
    purchases = Transaction.objects.filter(client=client_user, transaction_type='purchase')
    print(f"Purchase transactions count: {purchases.count()}")

    # Verify basket cleared
    remaining_items = basket.items.count()
    print(f"Remaining basket items: {remaining_items}")

    # Basic assertions (print-based for script use)
    if purchases.count() >= 1 and remaining_items == 0 and data.get('status') == 'success':
        print('SUCCESS: Checkout created purchases and cleared the basket.')
    else:
        print('FAILURE: Checkout did not behave as expected.')

    # Cleanup
    print('Cleaning up test data...')
    Transaction.objects.filter(client=client_user, transaction_type__in=['purchase', 'deposit']).delete()
    basket.items.all().delete()
    try:
        product.delete()
    except Exception:
        pass
    try:
        dealer.delete()
    except Exception:
        pass
    try:
        client_user.delete()
    except Exception:
        pass


if __name__ == '__main__':
    test_checkout_flow()
