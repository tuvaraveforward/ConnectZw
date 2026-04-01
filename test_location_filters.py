import os
import django
from django.test import Client
from django.urls import reverse
from datetime import timedelta
from django.utils import timezone

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Project1.settings')
django.setup()

from Location.models import Location
from Admin.models import Admin
from django.contrib.auth.hashers import make_password

def setup_test_data():
    # Create Admin User
    if not Admin.objects.filter(username='testadmin').exists():
        Admin.objects.create(
            username='testadmin',
            firstname='Test',
            lastname='Admin',
            phone_number='1234567890',
            password=make_password('testpass'),
            email_address='admin@test.com'
        )

    # Clear existing locations for clean test
    Location.objects.all().delete()

    # Create Test Locations
    # 1. New Active Location
    Location.objects.create(
        location_name="New Active Loc",
        username="new_active",
        email_address="new_active@test.com",
        city="City1",
        province="Prov1",
        category="Retail",
        password="pass",
        is_active=True
    )
    
    # 2. Old Active Location (created > 30 days ago)
    old_active = Location.objects.create(
        location_name="Old Active Loc",
        username="old_active",
        email_address="old_active@test.com",
        city="City2",
        province="Prov2",
        category="Retail",
        password="pass",
        is_active=True
    )
    # Hack to update created_at since auto_now_add=True
    old_active.created_at = timezone.now() - timedelta(days=40)
    old_active.save()

    # 3. New Blocked Location
    Location.objects.create(
        location_name="New Blocked Loc",
        username="new_blocked",
        email_address="new_blocked@test.com",
        city="City3",
        province="Prov3",
        category="Retail",
        password="pass",
        is_active=False
    )

def test_filters():
    c = Client()
    
    # Login
    login_response = c.post(reverse('admin_login'), {'username': 'testadmin', 'password': 'testpass'})
    assert login_response.status_code == 302, "Login failed"
    session = c.session
    session['admin_logged_in'] = True
    session.save()

    print("\nStarting Filter Tests...")

    # Test 1: No Filters (Should show all)
    print("Test 1: No Filters (Default: Show All)")
    response = c.get(reverse('locations'))
    content = response.content.decode()
    assert "New Active Loc" in content
    assert "Old Active Loc" in content
    assert "New Blocked Loc" in content
    # Note: Logic was updated to "Default to show all if no filters selected"
    print("PASS")

    # Test 2: Filter New Locations
    print("Test 2: Filter New Locations")
    response = c.get(reverse('locations'), {'new_locations': 'on'})
    content = response.content.decode()
    assert "New Active Loc" in content
    assert "New Blocked Loc" in content
    assert "Old Active Loc" not in content
    print("PASS")

    # Test 3: Filter Active Locations
    print("Test 3: Filter Active Locations")
    response = c.get(reverse('locations'), {'active_locations': 'on'})
    content = response.content.decode()
    assert "New Active Loc" in content
    assert "Old Active Loc" in content
    assert "New Blocked Loc" not in content
    print("PASS")

    # Test 4: Filter Blocked Locations
    print("Test 4: Filter Blocked Locations")
    response = c.get(reverse('locations'), {'blocked_locations': 'on'})
    content = response.content.decode()
    assert "New Blocked Loc" in content
    assert "New Active Loc" not in content
    assert "Old Active Loc" not in content
    print("PASS")

    # Test 5: Filter New AND Active
    print("Test 5: Filter New AND Active")
    response = c.get(reverse('locations'), {'new_locations': 'on', 'active_locations': 'on'})
    content = response.content.decode()
    # Logic is OR for filters usually? Wait, let's check code. 
    # Logic in code:
    # if show_new: filter_conditions |= Q(created_at__gte=thirty_days_ago)
    # if show_active: filter_conditions |= Q(is_active=True)
    # locations_list = locations_list.filter(filter_conditions)
    # It uses |= (OR) logic. So "New OR Active".
    
    assert "New Active Loc" in content # New and Active
    assert "Old Active Loc" in content # Active (Old)
    assert "New Blocked Loc" in content # New (Blocked)
    
    # Wait, if logic is OR:
    # New Active Loc (New=True, Active=True) -> Match
    # Old Active Loc (New=False, Active=True) -> Match
    # New Blocked Loc (New=True, Active=False) -> Match
    # So all three should be present?
    # Actually, verify_locations logic:
    # filter_conditions starts empty.
    # if new: add Q(new)
    # if active: add Q(active)
    # if blocked: add Q(blocked)
    # filter(Q(new) | Q(active))
    
    # So yes, it's OR logic. 
    # But usually filters like "New" AND "Active" implies Intersection?
    # The Prompt asked to "improve functionality". 
    # My implementation plan used `accounts.html` as reference.
    # checking accounts view logic:
    #     if show_new: filter_conditions |= Q(created_at__gte=thirty_days_ago) (OR)
    # So I matched the existing pattern in Accounts.
    
    # Let's verify standard OR behavior:
    # Should include New Blocked Loc (because it is New)
    # Should include Old Active Loc (because it is Active)
    
    assert "New Blocked Loc" in content
    assert "Old Active Loc" in content
    print("PASS")

    print("\nAll Tests Passed!")

if __name__ == "__main__":
    try:
        setup_test_data()
        test_filters()
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"FAILED: {e}")
