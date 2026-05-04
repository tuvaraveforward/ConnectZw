import os
import sys

# Ensure project root is in path
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Project1.settings')
import django
django.setup()

from Admin.models import Transaction
from Project1.aes_utils import encrypt_bytes, decrypt_bytes


def to_str(val):
    try:
        return val.decode('utf-8')
    except Exception:
        return repr(val)


def main():
    tx = Transaction.objects.filter(coupon_code__isnull=False).exclude(coupon_code='').first()
    if not tx:
        print('No transactions with coupon codes found in DB.')
        return

    print('Sample transaction:')
    print('  id:', tx.id)
    print('  stored coupon_code repr:', repr(tx.coupon_code))
    print('  stored serial_number repr:', repr(tx.serial_number))

    # Try to decrypt stored coupon_code
    try:
        plain_coupon = decrypt_bytes(tx.coupon_code)
        try:
            plain_coupon = plain_coupon.decode('utf-8')
        except Exception:
            plain_coupon = repr(plain_coupon)
        print('  decrypted coupon:', plain_coupon)
    except Exception as e:
        print('  could not decrypt stored coupon_code:', repr(e))
        plain_coupon = None

    # Use candidate coupon to run the lookup logic similarly to Pos.views
    candidates = []
    if plain_coupon:
        candidates.append(plain_coupon)
    # Also try using the raw stored value string representation
    candidates.append(str(tx.coupon_code))

    for candidate in candidates:
        print('\nTesting lookup with candidate coupon value:', candidate)
        # Try encrypted lookup
        try:
            enc = encrypt_bytes(candidate.encode('utf-8'))
            q = Transaction.objects.filter(coupon_code=enc, transaction_type='purchase')
            found = q.first()
            print('  Encrypted lookup returned:', 'FOUND id '+str(found.id) if found else 'None')
        except Exception as e:
            print('  Encrypted lookup raised:', repr(e))

        # Try plaintext lookup
        q2 = Transaction.objects.filter(coupon_code=candidate, transaction_type='purchase')
        found2 = q2.first()
        print('  Plaintext lookup returned:', 'FOUND id '+str(found2.id) if found2 else 'None')


if __name__ == '__main__':
    main()
