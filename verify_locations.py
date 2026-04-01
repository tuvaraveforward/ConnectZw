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

def verify_locations():
    print("🔍 Verifying locations in database...")

    try:
        locations = Location.objects.all()
        count = locations.count()

        print(f"📊 Found {count} locations in database")

        if count > 0:
            print("\n✅ SUCCESS! Locations are now in the database:")
            print("-" * 50)
            for i, loc in enumerate(locations, 1):
                print(f"{i}. {loc.location_name}")
                print(f"   📍 {loc.city}, {loc.province}")
                print(f"   📧 {loc.email_address}")
                print(f"   🏷️  {loc.category}")
                print(f"   👤 {loc.username}")
                print()

            print("🎉 The locations should now be visible on the locations page!")
            print("\n📱 To test:")
            print("1. Open your browser")
            print("2. Go to: http://127.0.0.1:8000/Admin/locations/")
            print("3. Log in as admin")
            print("4. You should see the locations in the table")
        else:
            print("❌ No locations found. There might be an issue with database creation.")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    verify_locations()
