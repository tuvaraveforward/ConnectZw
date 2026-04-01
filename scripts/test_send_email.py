import os
import django
import sys
import traceback

sys.path.append(r'c:\Users\Forward Tuvarave\Desktop\Django\Project1')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Project1.settings')
django.setup()

from Project1.email_utils import send_share_coupon_email

def run_test():
    try:
        print('Calling send_share_coupon_email...')
        ok = send_share_coupon_email(
            sender_name='Test Sender',
            recipient_email='forward.tuvarave@students.uz.ac.zw',
            coupon_id='TEST_COUPON_123',
            serial_number='TEST_SERIAL_123',
            amount=50,
            category='Test'
        )
        print('send_share_coupon_email returned:', ok)
    except Exception as e:
        print('Exception during send:', e)
        traceback.print_exc()

if __name__ == '__main__':
    run_test()
