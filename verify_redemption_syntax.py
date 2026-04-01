import os
import django
import sys

# Add project root to path
sys.path.append(r'c:\Users\Forward Tuvarave\Desktop\Django\Project1')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Project1.settings')
django.setup()

from Pos.views import redeem_coupon
print("Pos.views imported successfully")
from Admin.models import Transaction
print("Admin.models imported successfully")

# Check if is_redeemed field exists
if hasattr(Transaction, 'is_redeemed'):
    print("Transaction.is_redeemed field exists")
else:
    print("Transaction.is_redeemed field MISSING")
