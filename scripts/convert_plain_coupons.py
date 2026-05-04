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
from Project1.aes_utils import decrypt_bytes


def looks_encrypted(value) -> bool:
    """Return True if value appears to be AES-GCM payload (decryptable).

    We attempt to call decrypt_bytes. If it raises or returns invalid data,
    we treat the stored value as plaintext and return False.
    """
    if value in (None, ''):
        return False
    try:
        # decrypt_bytes accepts bytes; if value is str encode it
        payload = value if isinstance(value, (bytes, bytearray)) else str(value).encode('utf-8')
        dec = decrypt_bytes(payload)
        # If decrypt_bytes returns bytes without error, consider it encrypted
        return isinstance(dec, (bytes, bytearray))
    except Exception:
        return False


def main():
    qs = Transaction.objects.filter(coupon_code__isnull=False).exclude(coupon_code='')
    total = qs.count()
    if total == 0:
        print('No coupon entries found to inspect.')
        return

    print(f'Found {total} transactions with coupon codes. Inspecting...')

    converted = 0
    skipped = 0
    for tx in qs.iterator():
        # Check coupon_code
        if looks_encrypted(tx.coupon_code):
            coupon_encrypted = True
        else:
            coupon_encrypted = False

        if tx.serial_number in (None, ''):
            serial_encrypted = True
        else:
            if looks_encrypted(tx.serial_number):
                serial_encrypted = True
            else:
                serial_encrypted = False

        if coupon_encrypted and serial_encrypted:
            skipped += 1
            continue

        # Convert plaintext fields to encrypted by assigning and saving.
        changed = []
        if not coupon_encrypted:
            print(f'Encrypting coupon for Transaction id={tx.id}: "{tx.coupon_code}"')
            tx.coupon_code = tx.coupon_code
            changed.append('coupon_code')

        if not serial_encrypted and tx.serial_number not in (None, ''):
            print(f'Encrypting serial for Transaction id={tx.id}: "{tx.serial_number}"')
            tx.serial_number = tx.serial_number
            changed.append('serial_number')

        if changed:
            tx.save(update_fields=changed)
            converted += 1

    print(f'Done. Converted: {converted}, Skipped (already encrypted): {skipped}, Total inspected: {total}')


if __name__ == '__main__':
    main()
