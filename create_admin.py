import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Project1.settings')
django.setup()

from Admin.models import Admin
from django.contrib.auth.hashers import make_password

def create_admin():
    username = 'superadmin'
    password = 'superadmin123'
    
    if not Admin.objects.filter(username=username).exists():
        Admin.objects.create(
            username=username,
            firstname='System',
            lastname='Administrator',
            password=make_password(password),
            phone_number='0000000000',
            email_address='admin@system.local'
        )
        print(f"Success! Admin user created:\nUsername: {username}\nPassword: {password}")
    else:
        print(f"Admin user '{username}' already exists. Please use those credentials or change the script to a new username.")

if __name__ == '__main__':
    create_admin()
