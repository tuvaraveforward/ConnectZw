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

def check_locations():
    print("Checking locations in database...")

    try:
        # Get all locations
        locations = Location.objects.all()
        count = locations.count()

        print(f"Total locations found: {count}")

        if count == 0:
            print("❌ No locations found in database!")
            print("This explains why locations are not displayed.")
            print("\nCreating a test location...")

            # Create a test location
            test_location = Location.objects.create(
                location_name="Test Location",
                email_address="test@example.com",
                username="testuser",
                city="Harare",
                province="Harare",
                category="Retail",
                password="testpass123"
            )
            print(f"✅ Created test location: {test_location.location_name}")

            # Verify it was created
            locations = Location.objects.all()
            print(f"✅ Now {locations.count()} locations in database:")
            for loc in locations:
                print(f"  - {loc.location_name} ({loc.city}, {loc.province})")

        else:
            print("✅ Locations found:")
            for loc in locations:
                print(f"  - {loc.location_name} ({loc.city}, {loc.province})")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_locations()
