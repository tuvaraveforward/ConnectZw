#!/usr/bin/env python
"""
Test the actual share_coupon view to identify the issue.
"""

import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Project1.settings')
django.setup()

from django.test import Client as TestClient, RequestFactory
from Client.views import share_coupon, share_coupon_via_email
from Admin.models import Transaction
from Client.models import Client
import json
from unittest.mock import patch

print("\n" + "="*80)
print("TESTING COUPON EMAIL SHARE VIEW")
print("="*80)

# Get test data
client_user = Client.objects.first()
transaction = Transaction.objects.filter(coupon_code__isnull=False).exclude(coupon_code='').first()

if not client_user or not transaction:
    print("ERROR: No test data available!")
    print(f"  - Clients: {Client.objects.count()}")
    print(f"  - Transactions with coupons: {Transaction.objects.filter(coupon_code__isnull=False).count()}")
else:
    print(f"Using test data:")
    print(f"  - Client: {client_user.username}")
    print(f"  - Transaction ID: {transaction.id}")
    print(f"  - Coupon Code: {transaction.coupon_code}")
    
    # Test 1: Test share_coupon view
    print("\n1. TESTING share_coupon VIEW")
    print("-"*80)
    
    factory = RequestFactory()
    request = factory.post(
        '/client/share-coupon/',
        data={
            'coupon_code': transaction.coupon_code,
            'recipient_email': 'test@example.com'
        }
    )
    request.session = {'client_logged_in': True, 'client_username': client_user.username}
    
    with patch('Client.views.send_share_coupon_email') as mock_send:
        mock_send.return_value = True
        response = share_coupon(request)
        
    response_data = json.loads(response.content)
    print(f"Response: {response_data}")
    
    if response_data.get('success'):
        print("✓ share_coupon view would succeed")
        if mock_send.called:
            print(f"✓ Email function was called with:")
            call_args = mock_send.call_args
            print(f"  - sender_name: {call_args.kwargs.get('sender_name')}")
            print(f"  - recipient_email: {call_args.kwargs.get('recipient_email')}")
            print(f"  - coupon_id: {call_args.kwargs.get('coupon_id')}")
            print(f"  - serial_number: {call_args.kwargs.get('serial_number')}")
    else:
        print(f"✗ share_coupon view failed: {response_data.get('message')}")
    
    # Test 2: Test share_coupon_via_email view
    print("\n2. TESTING share_coupon_via_email VIEW (JSON)")
    print("-"*80)
    
    json_data = {
        'coupon_id': str(transaction.id),
        'serial_number': transaction.serial_number,
        'recipient_email': 'test@example.com',
        'amount': float(transaction.amount),
        'category': transaction.category
    }
    
    request = factory.post(
        '/client/share-coupon-email/',
        data=json.dumps(json_data),
        content_type='application/json'
    )
    request.session = {'client_logged_in': True, 'client_username': client_user.username}
    
    with patch('Client.views.send_share_coupon_email') as mock_send:
        mock_send.return_value = True
        response = share_coupon_via_email(request)
    
    response_data = json.loads(response.content)
    print(f"Response: {response_data}")
    
    if response_data.get('status') == 'success':
        print("✓ share_coupon_via_email view would succeed")
        if mock_send.called:
            print(f"✓ Email function was called")
    else:
        print(f"✗ share_coupon_via_email view failed: {response_data.get('message')}")

    # Test 3: Check the actual email function with real parameters
    print("\n3. TESTING ACTUAL EMAIL SENDING")
    print("-"*80)
    
    from Project1.email_utils import send_share_coupon_email
    
    result = send_share_coupon_email(
        sender_name=client_user.username,
        recipient_email='test@example.com',
        coupon_id=str(transaction.id),
        serial_number=transaction.serial_number,
        amount=float(transaction.amount),
        category=transaction.category
    )
    
    if result:
        print("✓ Email sent successfully!")
    else:
        print("✗ Email failed to send")

print("\n" + "="*80)
print("END OF VIEW TEST")
print("="*80 + "\n")
