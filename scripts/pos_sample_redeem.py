import os
import sys
import requests

# Ensure project root is in path
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Project1.settings')
import django
django.setup()

from Pos.models import Pos

BASE = 'http://127.0.0.1:8000'

def main():
    pos = Pos.objects.first()
    if not pos:
        print('No POS entries found in DB.')
        return
    username = pos.pos_name
    password = pos.pos_code
    print(f'Using POS: {username} / {password}')

    session = requests.Session()
    # disable environment proxy usage so localhost requests go direct
    session.trust_env = False
    login_url = BASE + '/Pos/login/'
    redeem_url = BASE + '/Pos/redeem_coupon/'

    # Fetch login page to get CSRF cookie
    session.get(login_url)
    csrf = session.cookies.get('csrftoken', '')
    headers = {'X-CSRFToken': csrf, 'Referer': login_url}

    # Login
    r = session.post(login_url, data={'username': username, 'password': password}, headers=headers)
    print('Login status:', r.status_code)

    # Use a sample coupon known to exist
    coupon_id = '517110620260420'
    serial = '51111711067533U'

    # First, verification step (default action)
    # Need CSRF token for POST
    csrf = session.cookies.get('csrftoken', '')
    headers = {'X-CSRFToken': csrf, 'Referer': redeem_url}
    r2 = session.post(redeem_url, data={'coupon_id': coupon_id, 'serial_number': serial}, headers=headers)
    print('Verification POST status:', r2.status_code)
    print('Verification response length:', len(r2.text))

    # Now, attempt confirm redemption
    r3 = session.post(redeem_url, data={'action': 'redeem_confirm', 'coupon_id': coupon_id}, headers=headers)
    print('Redeem confirm POST status:', r3.status_code)
    print('Redeem response length:', len(r3.text))

if __name__ == '__main__':
    main()
