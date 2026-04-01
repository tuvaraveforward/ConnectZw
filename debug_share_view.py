#!/usr/bin/env python
"""
Deep dive into why share_coupon view fails
"""

import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Project1.settings')
django.setup()

from Admin.models import Transaction
from Client.models import Client

print("\n" + "="*80)
print("INVESTIGATING SHARE_COUPON VIEW FAILURE")
print("="*80)

# Get the client that has coupons
transaction = Transaction.objects.filter(coupon_code__isnull=False).exclude(coupon_code='').first()

if transaction:
    client = transaction.client
    coupon_code = transaction.coupon_code
    
    print(f"\nTest Data:")
    print(f"  - Client ID: {client.id}")
    print(f"  - Client Username: {client.username}")
    print(f"  - Transaction ID: {transaction.id}")
    print(f"  - Coupon Code: {coupon_code}")
    print(f"  - Serial Number: {transaction.serial_number}")
    
    # Check if the query would find it
    print(f"\nQuery Test:")
    print(f"  Looking for: Transaction with client='{client.username}' AND coupon_code='{coupon_code}'")
    
    found = Transaction.objects.filter(client=client, coupon_code=coupon_code).first()
    
    if found:
        print(f"  ✓ Query FOUND: Transaction ID {found.id}")
    else:
        print(f"  ✗ Query FAILED to find transaction")
        
        # Check what coupon codes this client has
        print(f"\n  Coupons for client '{client.username}':")
        client_coupons = Transaction.objects.filter(client=client, coupon_code__isnull=False).exclude(coupon_code='')
        if client_coupons.exists():
            for t in client_coupons:
                print(f"    - {t.coupon_code}")
        else:
            print(f"    - (none found)")
    
    # Test the ACTUAL form submission
    print(f"\nSimulating Form Submission:")
    
    from django.test import RequestFactory
    from Client.views import share_coupon
    from unittest.mock import patch
    import json
    
    factory = RequestFactory()
    request = factory.post(
        '/client/share-coupon/',
        data={
            'coupon_code': coupon_code,
            'recipient_email': 'test@example.com'
        }
    )
    request.session = {'client_logged_in': True, 'client_username': client.username}
    
    # Add debugging to the view
    print(f"\n  Request Data:")
    print(f"    - coupon_code from POST: {request.POST.get('coupon_code')}")
    print(f"    - recipient_email from POST: {request.POST.get('recipient_email')}")
    print(f"    - username from session: {request.session.get('client_username')}")
    
    # Try to get the client
    try:
        db_client = Client.objects.get(username=request.session.get('client_username'))
        print(f"    - Client found: {db_client.username}")
        
        # Try to get transaction
        tx = Transaction.objects.filter(client=db_client, coupon_code=request.POST.get('coupon_code')).first()
        if tx:
            print(f"    - Transaction found: {tx.id}")
        else:
            print(f"    - Transaction NOT found")
            
            # Debug: check all transactions for this client
            all_tx = Transaction.objects.filter(client=db_client)
            print(f"\n  All transactions for {db_client.username}: {all_tx.count()}")
            for t in all_tx[:5]:
                print(f"    - ID: {t.id}, Coupon: {t.coupon_code}, Serial: {t.serial_number}")
    except Client.DoesNotExist:
        print(f"    - Client NOT found in database!")

else:
    print("No test transaction with coupon found!")

print("\n" + "="*80 + "\n")
