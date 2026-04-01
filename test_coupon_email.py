#!/usr/bin/env python
"""
Test script to diagnose coupon email sending issues.
Run with: python manage.py shell < test_coupon_email.py
"""

import os
import django
import sys

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Project1.settings')
django.setup()

from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from Project1.email_utils import send_share_coupon_email
from Admin.models import Transaction
from Client.models import Client

print("=" * 60)
print("COUPON EMAIL SENDING DIAGNOSTIC TEST")
print("=" * 60)

# 1. Check email configuration
print("\n1. EMAIL CONFIGURATION CHECK")
print("-" * 60)
print(f"EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
print(f"EMAIL_HOST: {settings.EMAIL_HOST}")
print(f"EMAIL_PORT: {settings.EMAIL_PORT}")
print(f"EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}")
print(f"EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
print(f"EMAIL_HOST_PASSWORD: {'*' * len(settings.EMAIL_HOST_PASSWORD) if settings.EMAIL_HOST_PASSWORD else 'NOT SET'}")

# 2. Check if email template exists
print("\n2. EMAIL TEMPLATE CHECK")
print("-" * 60)
try:
    template_path = os.path.join(settings.BASE_DIR, 'templates', 'emails', 'share_coupon.html')
    if os.path.exists(template_path):
        print(f"✓ share_coupon.html template found at: {template_path}")
    else:
        print(f"✗ share_coupon.html template NOT found at: {template_path}")
except Exception as e:
    print(f"Error checking template: {e}")

# 3. Check if logo image exists
print("\n3. LOGO IMAGE CHECK")
print("-" * 60)
try:
    logo_path = os.path.join(settings.BASE_DIR, 'static', 'images', 'icon.png')
    if os.path.exists(logo_path):
        print(f"✓ Logo image found at: {logo_path}")
    else:
        print(f"✗ Logo image NOT found at: {logo_path}")
except Exception as e:
    print(f"Error checking logo: {e}")

# 4. Test SMTP connection
print("\n4. SMTP CONNECTION TEST")
print("-" * 60)
try:
    from django.core.mail import get_connection
    connection = get_connection()
    connection.open()
    print("✓ SMTP connection successful!")
    connection.close()
except Exception as e:
    print(f"✗ SMTP connection failed: {e}")
    print("  Common causes:")
    print("  - Incorrect EMAIL_HOST_USER")
    print("  - Incorrect EMAIL_HOST_PASSWORD (use App Password for Gmail)")
    print("  - Email credentials not configured")
    print("  - Gmail 2FA enabled without App Password")

# 5. Test basic email sending
print("\n5. BASIC EMAIL TEST")
print("-" * 60)
try:
    from django.core.mail import send_mail
    send_mail(
        'Test Email from Django',
        'This is a test email to verify your email configuration.',
        settings.EMAIL_HOST_USER,
        [settings.EMAIL_HOST_USER],
        fail_silently=False,
    )
    print("✓ Basic email sent successfully!")
except Exception as e:
    print(f"✗ Basic email failed: {e}")

# 6. Test coupon email function
print("\n6. COUPON EMAIL FUNCTION TEST")
print("-" * 60)
try:
    result = send_share_coupon_email(
        sender_name="Test User",
        recipient_email=settings.EMAIL_HOST_USER,
        coupon_id="TEST-001",
        serial_number="SN123456",
        amount=100.00,
        category="Electronics"
    )
    if result:
        print("✓ Coupon email sent successfully!")
    else:
        print("✗ Coupon email failed (check console for error details)")
except Exception as e:
    print(f"✗ Coupon email test failed: {e}")

# 7. Check for any existing test transactions with coupons
print("\n7. EXISTING COUPONS CHECK")
print("-" * 60)
try:
    coupons = Transaction.objects.filter(coupon_code__isnull=False).exclude(coupon_code='')[:5]
    if coupons.exists():
        print(f"Found {coupons.count()} transactions with coupons:")
        for coupon in coupons:
            print(f"  - ID: {coupon.id}, Code: {coupon.coupon_code}, Serial: {coupon.serial_number}")
    else:
        print("No transactions with coupons found")
except Exception as e:
    print(f"Error checking coupons: {e}")

# 8. Check client records
print("\n8. EXISTING CLIENTS CHECK")
print("-" * 60)
try:
    clients = Client.objects.all()[:3]
    if clients.exists():
        print(f"Found {clients.count()} clients:")
        for client in clients:
            print(f"  - Username: {client.username}, Email: {client.email_address}")
    else:
        print("No clients found")
except Exception as e:
    print(f"Error checking clients: {e}")

print("\n" + "=" * 60)
print("DIAGNOSTIC TEST COMPLETE")
print("=" * 60)
print("\nRECOMMENDATIONS:")
print("- If SMTP connection fails, check your Gmail App Password")
print("- Ensure EMAIL_HOST_USER and EMAIL_HOST_PASSWORD are correct")
print("- For Gmail, generate an App Password at: https://myaccount.google.com/apppasswords")
print("- Make sure the share_coupon.html template is in templates/emails/")
print("=" * 60)
