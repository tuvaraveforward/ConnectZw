#!/usr/bin/env python
"""
Detailed debugging script for coupon email sharing.
Checks the form submission flow and data.
"""

import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Project1.settings')
django.setup()

from Admin.models import Transaction
from Client.models import Client
import json

print("\n" + "="*80)
print("DETAILED COUPON EMAIL DEBUGGING")
print("="*80)

# 1. Check a sample coupon
print("\n1. SAMPLE COUPON DATA")
print("-"*80)
transaction = Transaction.objects.filter(coupon_code__isnull=False).exclude(coupon_code='').first()

if transaction:
    print(f"Transaction ID: {transaction.id}")
    print(f"Coupon Code: {transaction.coupon_code}")
    print(f"Serial Number: {transaction.serial_number}")
    print(f"Category: {transaction.category}")
    print(f"Amount: {transaction.amount}")
    print(f"Client: {transaction.client.username if transaction.client else 'None'}")
else:
    print("No transactions with coupons found!")

# 2. Check form submission flow
print("\n2. FORM SUBMISSION FLOW CHECK")
print("-"*80)

# Simulate what the form sends to share_coupon view
if transaction and transaction.client:
    coupon_code = transaction.coupon_code
    
    # Try to find it the way share_coupon view does
    found_transaction = Transaction.objects.filter(
        client=transaction.client, 
        coupon_code=coupon_code
    ).first()
    
    if found_transaction:
        print(f"✓ Form submission would find transaction: ID={found_transaction.id}")
        print(f"  - Coupon Code: {found_transaction.coupon_code}")
        print(f"  - Serial Number: {found_transaction.serial_number}")
    else:
        print(f"✗ Form submission would NOT find transaction with code: {coupon_code}")
        print("  This would cause the share to fail!")

# 3. Check if there are any transactions without serial_number
print("\n3. CHECK FOR MISSING SERIAL NUMBERS")
print("-"*80)
missing_serial = Transaction.objects.filter(
    coupon_code__isnull=False
).exclude(coupon_code='').filter(serial_number__isnull=True)

if missing_serial.exists():
    print(f"⚠ Found {missing_serial.count()} transactions with coupon codes but NO serial numbers!")
    for t in missing_serial[:3]:
        print(f"  - ID: {t.id}, Code: {t.coupon_code}, Serial: {t.serial_number}")
else:
    print("✓ All transactions with coupon codes have serial numbers")

# 4. Check if there are duplicate coupon codes
print("\n4. CHECK FOR DUPLICATE COUPON CODES")
print("-"*80)
from django.db.models import Count
duplicates = Transaction.objects.filter(
    coupon_code__isnull=False
).exclude(coupon_code='').values('coupon_code').annotate(
    count=Count('id')
).filter(count__gt=1)

if duplicates.exists():
    print(f"⚠ Found {duplicates.count()} duplicate coupon codes:")
    for dup in duplicates[:5]:
        code = dup['coupon_code']
        count = dup['count']
        print(f"  - Code: {code} (used {count} times)")
        txns = Transaction.objects.filter(coupon_code=code)
        for txn in txns:
            print(f"    • ID: {txn.id}, Client: {txn.client}, Serial: {txn.serial_number}")
else:
    print("✓ No duplicate coupon codes found")

print("\n" + "="*80)
print("END OF DEBUG REPORT")
print("="*80 + "\n")
