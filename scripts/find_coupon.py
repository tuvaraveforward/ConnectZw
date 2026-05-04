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
from django.db import connection

target = '508024320260422'
print('Searching for coupon:', target)

table = Transaction._meta.db_table

found = False

with connection.cursor() as cursor:
    cursor.execute(f"SELECT id, coupon_code_encrypted, serial_number_encrypted, is_redeemed FROM {table} WHERE coupon_code_encrypted IS NOT NULL")
    rows = cursor.fetchall()

for row in rows:
    tx_id, raw_coupon, raw_serial, is_redeemed = row
    # try decrypt
    try:
        dec = decrypt_bytes(raw_coupon)
        try:
            dec_s = dec.decode('utf-8')
        except Exception:
            dec_s = repr(dec)
        if dec_s == target:
            print(f'Found by decrypt: id={tx_id}, serial={raw_serial}, is_redeemed={is_redeemed}')
            found = True
            break
    except Exception:
        pass

    # try raw decode (plaintext stored as bytes)
    try:
        if isinstance(raw_coupon, (bytes, bytearray)) and raw_coupon.decode('utf-8') == target:
            print(f'Found by raw decode: id={tx_id}, serial={raw_serial}, is_redeemed={is_redeemed}')
            found = True
            break
    except Exception:
        pass

# Also try ORM-level lookup (may return decrypted strings)
orm_matches = Transaction.objects.filter(coupon_code=target)
for tx in orm_matches:
    print(f'ORM match: id={tx.id}, serial={tx.serial_number}, is_redeemed={tx.is_redeemed}')
    found = True

if not found:
    print('No matches found for coupon', target)
