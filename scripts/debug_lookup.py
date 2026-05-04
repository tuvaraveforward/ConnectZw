import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Project1.settings')
import django
django.setup()

from Admin.models import Transaction
from Project1.aes_utils import encrypt_bytes, decrypt_bytes
from django.db import connection

coupon_id = '508024320260422'
serial_number = '540802437862X'

print(f'Testing lookup for coupon={coupon_id}, serial={serial_number}\n')

# Test 1: Encrypted lookup
print('1. Encrypted ORM lookup:')
try:
    enc_coupon = encrypt_bytes(coupon_id.encode('utf-8'))
    enc_serial = encrypt_bytes(serial_number.encode('utf-8'))
    q = Transaction.objects.filter(coupon_code=enc_coupon, serial_number=enc_serial, transaction_type='purchase')
    found = q.first()
    print(f'   Result: {found}')
except Exception as e:
    print(f'   Error: {e}')

# Test 2: Plaintext ORM lookup
print('\n2. Plaintext ORM lookup:')
try:
    q = Transaction.objects.filter(coupon_code=coupon_id, serial_number=serial_number, transaction_type='purchase')
    found = q.first()
    print(f'   Result: {found}')
except Exception as e:
    print(f'   Error: {e}')

# Test 3: Raw DB byte lookup
print('\n3. Raw DB byte equality lookup:')
try:
    table = Transaction._meta.db_table
    with connection.cursor() as cursor:
        params = []
        sql = f"SELECT id FROM {table} WHERE transaction_type = 'purchase' AND "
        sql += "(coupon_code_encrypted = %s OR coupon_code_encrypted = %s)"
        params.append(coupon_id.encode('utf-8'))
        params.append(encrypt_bytes(coupon_id.encode('utf-8')))
        if serial_number:
            sql += " AND (serial_number_encrypted = %s OR serial_number_encrypted = %s)"
            params.append(serial_number.encode('utf-8'))
            params.append(encrypt_bytes(serial_number.encode('utf-8')))
        
        print(f'   SQL: {sql[:100]}...')
        print(f'   Params: [plaintext_coupon, encrypted_coupon, plaintext_serial, encrypted_serial]')
        cursor.execute(sql, params)
        row = cursor.fetchone()
        print(f'   Result: {"Found id=" + str(row[0]) if row else "Not found"}')
except Exception as e:
    print(f'   Error: {e}')

# Test 4: Check what's actually in DB for id=28
print('\n4. Checking DB storage for actual id=28:')
try:
    table = Transaction._meta.db_table
    with connection.cursor() as cursor:
        cursor.execute(f"SELECT id, coupon_code_encrypted, serial_number_encrypted FROM {table} WHERE id=28")
        row = cursor.fetchone()
        if row:
            tx_id, raw_coupon, raw_serial = row
            print(f'   id={tx_id}')
            print(f'   coupon_code_encrypted type: {type(raw_coupon).__name__}, len={len(raw_coupon) if raw_coupon else 0}')
            print(f'   serial_number_encrypted type: {type(raw_serial).__name__}, len={len(raw_serial) if raw_serial else 0}')
            # Try decrypting
            try:
                dec_coupon = decrypt_bytes(raw_coupon).decode('utf-8')
                print(f'   decrypted coupon: {dec_coupon}')
            except Exception as e:
                print(f'   decrypt coupon failed: {e}')
            try:
                dec_serial = decrypt_bytes(raw_serial).decode('utf-8')
                print(f'   decrypted serial: {dec_serial}')
            except Exception as e:
                print(f'   decrypt serial failed: {e}')
except Exception as e:
    print(f'   Error: {e}')
