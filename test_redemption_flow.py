import os
import django
import sys
from django.conf import settings

# Add project root to path
sys.path.append(r'c:\Users\Forward Tuvarave\Desktop\Django\Project1')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Project1.settings')
django.setup()

from Admin.models import Transaction, Client, Dealer, Product, Location, Pos

def test_redemption_logic():
    # 1. Setup Data
    print("Setting up test data...")
    try:
        # Create Dummy Client/Dealer if needed (using get_or_create to avoid dupes)
        client, _ = Client.objects.get_or_create(username='test_redeem_client', defaults={
            'firstname': 'Test', 'lastname': 'Client', 'password': 'pass', 'email_address': 'test@test.com', 'phone_number': '123'
        })
        
        # Create a Transaction that is NOT redeemed
        coupon_code = 'TEST_COUPON_123'
        serial_number = 'TEST_SERIAL_123'
        
        # Clear old test data
        Transaction.objects.filter(coupon_code=coupon_code).delete()
        
        t1 = Transaction.objects.create(
            transaction_type='purchase',
            amount=100,
            client=client,
            coupon_code=coupon_code,
            serial_number=serial_number,
            description="Test Item 1",
            is_redeemed=False
        )
        t2 = Transaction.objects.create(
            transaction_type='purchase',
            amount=50,
            client=client,
            coupon_code=coupon_code,
            serial_number='OTHER_SERIAL', # Same basket/coupon, different serial
            description="Test Item 2",
            is_redeemed=False
        )
        
        print(f"Created 2 transactions with coupon {coupon_code}. is_redeemed={t1.is_redeemed}")
        
        # 2. Simulate "Redeem Confirm" Logic
        print("\nSimulating Redeem Confirm...")
        # Logic from view:
        transactions = Transaction.objects.filter(coupon_code=coupon_code, transaction_type='purchase')
        updated_count = transactions.update(is_redeemed=True)
        
        print(f"Updated count: {updated_count}")
        
        # 3. Verify
        t1.refresh_from_db()
        t2.refresh_from_db()
        
        if t1.is_redeemed and t2.is_redeemed:
            print("SUCCESS: Transactions marked as redeemed.")
        else:
            print(f"FAILURE: t1.is_redeemed={t1.is_redeemed}, t2.is_redeemed={t2.is_redeemed}")

        # Cleanup
        print("\nCleaning up...")
        Transaction.objects.filter(coupon_code=coupon_code).delete()
        client.delete()
        
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == '__main__':
    test_redemption_logic()
