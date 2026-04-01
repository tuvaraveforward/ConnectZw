#!/usr/bin/env python
import os
import sys
import django

# Add the project directory to the Python path
sys.path.append('c:/Users/NOOR AL MUSABAH/Desktop/Django/Project1')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Project1.settings')

# Setup Django
django.setup()

from Location.models import Location
from django.contrib.auth.hashers import make_password

def create_sample_locations():
    print("Creating sample locations...")

    # Sample location data
    sample_locations = [
        {
            'location_name': 'Downtown Mall',
            'email_address': 'downtown@example.com',
            'username': 'downtown_mall',
            'city': 'Harare',
            'province': 'Harare',
            'category': 'Retail',
            'password': 'Zimconnect'
        },
        {
            'location_name': 'City Hospital',
            'email_address': 'hospital@example.com',
            'username': 'city_hospital',
            'city': 'Harare',
            'province': 'Harare',
            'category': 'Healthcare',
            'password': 'Zimconnect'
        },
        {
            'location_name': 'Tech Hub',
            'email_address': 'techhub@example.com',
            'username': 'tech_hub',
            'city': 'Bulawayo',
            'province': 'Bulawayo',
            'category': 'Service',
            'password': 'Zimconnect'
        },
        {
            'location_name': 'Garden Restaurant',
            'email_address': 'garden@example.com',
            'username': 'garden_restaurant',
            'city': 'Mutare',
            'province': 'Manicaland',
            'category': 'Restaurant',
            'password': 'Zimconnect'
        },
        {
            'location_name': 'Bookstore Plus',
            'email_address': 'bookstore@example.com',
            'username': 'bookstore_plus',
            'city': 'Gweru',
            'province': 'Midlands',
            'category': 'Retail',
            'password': 'Zimconnect'
        }
    ]

    created_count = 0
    for location_data in sample_locations:
        try:
            # Check if location already exists
            if not Location.objects.filter(username=location_data['username']).exists():
                location = Location.objects.create(**location_data)
                print(f"✅ Created: {location.location_name} - {location.city}, {location.province}")
                created_count += 1
            else:
                print(f"⚠️  Skipped: {location_data['location_name']} (already exists)")
        except Exception as e:
            print(f"❌ Error creating {location_data['location_name']}: {e}")

    # Show final count
    total_locations = Location.objects.count()
    print(f"\n📊 Total locations in database: {total_locations}")
    print(f"✅ Successfully created {created_count} new locations")

    if total_locations > 0:
        print("\n📋 All locations:")
        for loc in Location.objects.all():
            print(f"  - {loc.location_name} ({loc.city}, {loc.province}) - {loc.category}")

if __name__ == "__main__":
    create_sample_locations()
