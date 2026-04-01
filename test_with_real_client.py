#!/usr/bin/env python
"""
Test share_coupon with proper Django TestClient
"""

import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Project1.settings')
django.setup()

from django.test import Client as DjangoTestClient
from Admin.models import Transaction
from Client.models import Client
from unittest.mock import patch

print("\n" + "="*80)
print("TESTING WITH PROPER DJANGO CLIENT")
print("="*80)

# Get test data
client_user = Client.objects.filter(username='Client 1').first() or Client.objects.first()
transaction = Transaction.objects.filter(client=client_user, coupon_code__isnull=False).exclude(coupon_code='').first()

if not client_user or not transaction:
    print("ERROR: No test data!")
else:
    print(f"Test Setup:")
    print(f"  - Client: {client_user.username}")
    print(f"  - Coupon Code: {transaction.coupon_code}")
    print(f"  - Email to test: testclient@example.com")
    
    # Create a test client
    test_client = DjangoTestClient()
    
    # Set up a session for the client
    session = test_client.session
    session['client_logged_in'] = True
    session['client_username'] = client_user.username
    session.save()
    
    # Now test the actual share_coupon view
    print(f"\nTest 1: Direct POST request to share_coupon")
    print("-"*80)
    
    with patch('Client.views.send_share_coupon_email') as mock_send:
        mock_send.return_value = True
        
        response = test_client.post(
            '/Client/share-coupon/',
            {
                'coupon_code': transaction.coupon_code,
                'recipient_email': 'testclient@example.com'
            },
            HTTP_X_CSRFTOKEN=session._session_key or 'test'
        )
    
    print(f"Response status: {response.status_code}")
    print(f"Response data: {response.json()}")
    
    if response.json().get('success'):
        print("✓ View succeeded!")
        if mock_send.called:
            print(f"✓ Email function was called with:")
            args, kwargs = mock_send.call_args
            print(f"  - sender_name: {kwargs.get('sender_name')}")
            print(f"  - recipient_email: {kwargs.get('recipient_email')}")
            print(f"  - coupon_id: {kwargs.get('coupon_id')}")
            print(f"  - serial_number: {kwargs.get('serial_number')}")
    else:
        print(f"✗ View failed: {response.json().get('message')}")
        print("\nTrying with alternative session setup...")
        
        # Try with different session setup
        client_with_session = DjangoTestClient()
        from django.contrib.sessions.backends.db import SessionStore
        s = SessionStore()
        s['client_logged_in'] = True
        s['client_username'] = client_user.username
        s.create()
        
        with patch('Client.views.send_share_coupon_email') as mock_send:
            mock_send.return_value = True
            
            response2 = client_with_session.post(
                '/Client/share-coupon/',
                {
                    'coupon_code': transaction.coupon_code,
                    'recipient_email': 'testclient@example.com'
                },
                HTTP_COOKIE=f'sessionid={s.session_key}'
            )
        
        print(f"Alternative Response: {response2.json()}")

print("\n" + "="*80 + "\n")
