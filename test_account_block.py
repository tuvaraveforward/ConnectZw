import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Project1.settings')
django.setup()

from django.test import Client
from Admin.models import LoginAttempt, Admin
from django.contrib.auth.hashers import make_password

def setup():
    Admin.objects.all().delete()
    LoginAttempt.objects.all().delete()
    admin = Admin.objects.create(username='testadmin', password=make_password('correctpass'), email_address='test@test.com')
    return admin

def test_blocking():
    setup()
    client = Client()
    url = '/'

    print("Test 1: 3 failed logins should block")
    for i in range(3):
        response = client.post(url, {'username': 'testadmin', 'password': 'wrongpassword'})
        att = LoginAttempt.objects.get(username='testadmin')
        print(f"Attempt {i+1}: Blocked={att.is_blocked}, FailedCount={att.failed_attempts}")

    print("Test 2: 4th login should be rejected even with correct password")
    response = client.post(url, {'username': 'testadmin', 'password': 'correctpass'})
    att = LoginAttempt.objects.get(username='testadmin')
    print(f"Attempt 4 (correct pass): Blocked={att.is_blocked}, FailedCount={att.failed_attempts}")
    
    # Should stay blocked
    messages = list(response.wsgi_request._messages)
    for msg in messages:
        print("Message:", msg)

    print("\nTest 3: Correct login resets counter")
    LoginAttempt.objects.all().delete()
    client.post(url, {'username': 'testadmin', 'password': 'wrongpassword'})
    att = LoginAttempt.objects.get(username='testadmin')
    print(f"After 1 wrong attempt: FailedCount={att.failed_attempts}")
    
    client.post(url, {'username': 'testadmin', 'password': 'correctpass'})
    att = LoginAttempt.objects.get(username='testadmin')
    print(f"After correct attempt: FailedCount={att.failed_attempts}, Blocked={att.is_blocked}")

if __name__ == '__main__':
    test_blocking()
