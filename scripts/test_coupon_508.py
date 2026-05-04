import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Project1.settings')
import django
django.setup()

from Admin.models import Transaction
from Project1.aes_utils import decrypt_bytes

tx = Transaction.objects.get(id=28)
print('Transaction id=28:')
print(f'  coupon_code: {tx.coupon_code}')
print(f'  serial_number: {tx.serial_number}')
print(f'  is_redeemed: {tx.is_redeemed}')

# Now test the POS lookup with these exact values
import requests

session = requests.Session()
session.trust_env = False

login_url = 'http://127.0.0.1:8000/Pos/login/'
check_url = 'http://127.0.0.1:8000/Pos/check_validity/'

# Get CSRF
session.get(login_url)
csrf = session.cookies.get('csrftoken', '')

# Login
session.post(
    login_url,
    data={'username': 'OK_Counter', 'password': 'LOC009-001'},
    headers={'X-CSRFToken': csrf, 'Referer': login_url}
)

# Test check_validity with correct coupon and serial
headers = {'X-CSRFToken': csrf, 'Referer': check_url}
r = session.post(
    check_url,
    data={'coupon_number': tx.coupon_code, 'serial_number': tx.serial_number},
    headers=headers
)

print(f'\nPOS check_validity result:')
print(f'  Status: {r.status_code}')
if 'VALID' in r.text:
    print('  ✓ Coupon validated successfully')
elif 'ALREADY' in r.text:
    print('  ✗ Coupon already redeemed')
elif 'Invalid' in r.text:
    print('  ✗ Invalid coupon error (lookup failed)')
else:
    print('  ? Unknown response')
