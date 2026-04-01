#!/usr/bin/env python
"""
Test script to verify coupon email sharing works end-to-end.
Run with: python manage.py shell < test_coupon_sharing_flow.py
"""

import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Project1.settings')
django.setup()

from Admin.models import Transaction
from Client.models import Client
from Project1.email_utils import send_share_coupon_email

print("\n" + "="*80)
print("COUPON EMAIL SHARING END-TO-END TEST")
print("="*80)

# Get test data
client = Client.objects.first()
transaction = Transaction.objects.filter(coupon_code__isnull=False).exclude(coupon_code='').first()

if not client or not transaction:
    print("ERROR: No test data available")
else:
    print(f"\n✓ Test Data Found:")
    print(f"  - Client: {client.username} ({client.email_address})")
    print(f"  - Coupon Code: {transaction.coupon_code}")
    print(f"  - Serial Number: {transaction.serial_number}")
    print(f"  - Amount: ${transaction.amount}")
    print(f"  - Category: {transaction.category}")
    
    # Test 1: Send to test email
    print(f"\n1. SENDING TEST EMAIL")
    print("-"*80)
    
    test_email = "test@example.com"
    
    result = send_share_coupon_email(
        sender_name=client.username,
        recipient_email=test_email,
        coupon_id=str(transaction.id),
        serial_number=transaction.serial_number,
        amount=float(transaction.amount),
        category=transaction.category
    )
    
    if result:
        print(f"✓ Email sent successfully to {test_email}")
    else:
        print(f"✗ Email failed to send to {test_email}")
        print("  Check Django console logs for [ERROR] messages")
    
    # Test 2: Verify form submission would work
    print(f"\n2. FORM SUBMISSION SIMULATION")
    print("-"*80)
    
    from django.test import RequestFactory
    from Client.views import share_coupon
    from unittest.mock import patch
    import json
    
    factory = RequestFactory()
    request = factory.post(
        '/client/share-coupon/',
        data={
            'coupon_code': transaction.coupon_code,
            'recipient_email': 'form_test@example.com'
        }
    )
    request.session = {
        'client_logged_in': True,
        'client_username': client.username
    }
    
    with patch('Client.views.send_share_coupon_email') as mock_send:
        mock_send.return_value = True
        response = share_coupon(request)
    
    response_data = json.loads(response.content)
    
    if response_data.get('success'):
        print(f"✓ Form submission successful")
        print(f"  Response: {response_data.get('message')}")
    else:
        print(f"✗ Form submission failed")
        print(f"  Error: {response_data.get('message')}")

print("\n" + "="*80)
print("TESTING COMPLETE")
print("="*80)
print("\nNEXT STEPS:")
print("1. Open browser and go to http://127.0.0.1:8000/Client/login/")
print("2. Log in with your test account")
print("3. Go to Purchases page")
print("4. Click 'Share Coupon' > 'Email'")
print("5. Select a coupon and enter recipient email")
print("6. Click 'Send Coupon'")
print("7. Check browser console (F12) for logs")
print("8. Check Django console for [INFO]/[ERROR] messages")
print("="*80 + "\n")
