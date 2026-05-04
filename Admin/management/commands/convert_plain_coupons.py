from django.core.management.base import BaseCommand
from Admin.models import Transaction
from Project1.aes_utils import decrypt_bytes


class Command(BaseCommand):
    help = 'Convert plaintext coupon_code and serial_number DB values to encrypted storage via EncryptedCharField.'

    def add_arguments(self, parser):
        parser.add_argument('--dry-run', action='store_true', help='Show what would be converted without saving')
        parser.add_argument('--limit', type=int, default=0, help='Limit number of rows to convert (0 = no limit)')

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        limit = options['limit']

        table = Transaction._meta.db_table
        from django.db import connection

        with connection.cursor() as cursor:
            cursor.execute(f"SELECT COUNT(1) FROM {table}")
            total = cursor.fetchone()[0]

        self.stdout.write(f'Inspecting {total} transaction rows (reading raw columns)...')

        converted = 0
        skipped = 0
        inspected = 0

        # iterate raw rows to access underlying DB column values
        with connection.cursor() as cursor:
            cursor.execute(f"SELECT id, coupon_code_encrypted, serial_number_encrypted FROM {table}")
            rows = cursor.fetchall()

        for row in rows:
            if limit and converted >= limit:
                break
            inspected += 1
            tx_id = row[0]
            raw_coupon = row[1]
            raw_serial = row[2]

            def is_encrypted(raw):
                if raw is None or raw == b'' or raw == '':
                    return False
                # If stored as bytes, try decrypting
                try:
                    if isinstance(raw, (bytes, bytearray)):
                        _ = decrypt_bytes(bytes(raw))
                        return True
                    # If stored as str, it's plaintext (not encrypted)
                    if isinstance(raw, str):
                        return False
                    # Other types: attempt decode then decrypt
                    try:
                        payload = bytes(raw)
                        _ = decrypt_bytes(payload)
                        return True
                    except Exception:
                        return False
                except Exception:
                    return False

            coupon_encrypted = is_encrypted(raw_coupon)
            serial_encrypted = is_encrypted(raw_serial)

            if coupon_encrypted and (serial_encrypted or raw_serial in (None, b'', '')):
                skipped += 1
                continue

            self.stdout.write(f'Converting Transaction id={tx_id} (coupon_encrypted={coupon_encrypted}, serial_encrypted={serial_encrypted})')

            if not dry_run:
                tx = Transaction.objects.get(id=tx_id)
                # If coupon stored as bytes but not decryptable, treat as plaintext bytes
                if not coupon_encrypted and raw_coupon not in (None, b'', ''):
                    if isinstance(raw_coupon, (bytes, bytearray)):
                        try:
                            plain = raw_coupon.decode('utf-8')
                        except Exception:
                            plain = str(raw_coupon)
                    else:
                        plain = str(raw_coupon)
                    tx.coupon_code = plain

                if not serial_encrypted and raw_serial not in (None, b'', ''):
                    if isinstance(raw_serial, (bytes, bytearray)):
                        try:
                            plain_s = raw_serial.decode('utf-8')
                        except Exception:
                            plain_s = str(raw_serial)
                    else:
                        plain_s = str(raw_serial)
                    tx.serial_number = plain_s

                tx.save(update_fields=[f for f in ['coupon_code', 'serial_number'] if getattr(tx, f) is not None])
                converted += 1

        self.stdout.write(f'Done. Converted: {converted}, Skipped: {skipped}, Inspected: {inspected}')
