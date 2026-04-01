import os
import django
import sys

# Set up Django environment
sys.path.append(r'c:\Users\Forward Tuvarave\Desktop\Django\Project1')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Project1.settings')
django.setup()

from Client.models import Client
from django.contrib.auth.hashers import make_password, check_password

def verify_password_reset_logic():
    print("Testing Password Reset Logic...")
    
    # Create or get a test client
    test_username = 'test_reset_user'
    test_email = 'test_reset_unique@example.com'
    old_pw = 'old_password_123'
    new_pw = 'new_password_456'
    
    # Cleanup existing
    Client.objects.filter(username=test_username).delete()
    Client.objects.filter(email_address=test_email).delete()
    
    client = Client.objects.create(
        username=test_username,
        firstname='Test',
        lastname='User',
        phone_number='123456789',
        email_address=test_email,
        password=make_password(old_pw)
    )
    print(f"Created test user '{test_username}' with password '{old_pw}'")

    # Step 1: Verify old password
    print(f"Verifying old password: {check_password(old_pw, client.password)}")
    assert check_password(old_pw, client.password) == True
    
    # Step 2: Simulate password change
    client.password = make_password(new_pw)
    client.save()
    print("Updated password to 'new_password_456'")
    
    # Step 3: Verify new password
    print(f"Verifying new password: {check_password(new_pw, client.password)}")
    assert check_password(new_pw, client.password) == True
    
    # Step 4: Verify old password fails
    print(f"Verifying old password now fails: {not check_password(old_pw, client.password)}")
    assert check_password(old_pw, client.password) == False
    
    print("Password Reset Logic Verified Successfully!")

if __name__ == "__main__":
    try:
        verify_password_reset_logic()
    except Exception:
        import traceback
        traceback.print_exc()
        sys.exit(1)
