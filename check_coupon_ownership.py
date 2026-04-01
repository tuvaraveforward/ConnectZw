#!/usr/bin/env python
"""
Check which client owns which coupons
"""

import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Project1.settings')
django.setup()

from Admin.models import Transaction
from Client.models import Client

print("\n" + "="*80)
print("COUPON OWNERSHIP CHECK")
print("="*80 + "\n")

# Get all clients with coupons
clients_with_coupons = Client.objects.filter(
    transactions__coupon_code__isnull=False
).exclude(transactions__coupon_code='').distinct()

print(f"Found {clients_with_coupons.count()} clients with coupons:\n")

for client in clients_with_coupons:
    coupons = Transaction.objects.filter(
        client=client,
        coupon_code__isnull=False
    ).exclude(coupon_code='')
    
    print(f"Client: {client.username}")
    print(f"  Email: {client.email_address}")
    print(f"  Coupons:")
    for coupon in coupons:
        print(f"    - Code: {coupon.coupon_code}")
        print(f"      Serial: {coupon.serial_number}")
        print(f"      Amount: ${coupon.amount}")
        print(f"      Category: {coupon.category}")
    print()

print("="*80 + "\n")
