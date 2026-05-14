import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Project1.settings')
django.setup()

from Admin.models import Admin
from django.contrib.auth.hashers import make_password
from django.contrib.auth import get_user_model

def create_admin():
    username = 'forward'
    password = 'admin123'
    email = 'forward@example.com'
    
    # 1. Create custom Admin portal user
    if not Admin.objects.filter(username=username).exists():
        Admin.objects.create(
            username=username,
            firstname='Forward',
            lastname='Tuvarave',
            password=make_password(password),
            phone_number='0000000000',
            email_address=email
        )
        print(f"Success! Custom Admin '{username}' created.")
    else:
        print(f"Custom Admin '{username}' already exists.")

    # 2. Create standard Django superuser (for /admin/)
    User = get_user_model()
    if not User.objects.filter(username=username).exists():
        User.objects.create_superuser(username, email, password)
        print(f"Success! Django Superuser '{username}' created.")
    else:
        print(f"Django Superuser '{username}' already exists.")

if __name__ == '__main__':
    create_admin()
