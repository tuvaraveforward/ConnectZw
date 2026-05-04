from django.db import models
from django.core import exceptions
from Project1.aes_utils import encrypt_bytes, decrypt_bytes


class EncryptedCharField(models.BinaryField):
    description = "Encrypted text stored as binary using AES-GCM"

    def __init__(self, *args, max_length=None, **kwargs):
        # stored as binary, but keep max_length for compatibility
        self.max_length = max_length
        super().__init__(*args, **kwargs)

    def get_prep_value(self, value):
        # Prepare value for DB: accept None, str, or bytes
        if value is None:
            return None
        if isinstance(value, str):
            return encrypt_bytes(value.encode('utf-8'))
        if isinstance(value, (bytes, bytearray)):
            # assume already encrypted
            return bytes(value)
        # fallback convert to str then encrypt
        return encrypt_bytes(str(value).encode('utf-8'))

    def from_db_value(self, value, expression, connection):
        # Convert DB value (bytes) to Python string
        if value is None:
            return None
        try:
            plain = decrypt_bytes(bytes(value))
            return plain.decode('utf-8')
        except Exception:
            return ''

    def to_python(self, value):
        # Called during deserialization and assignment
        if value is None:
            return None
        if isinstance(value, str):
            return value
        if isinstance(value, (bytes, bytearray)):
            try:
                plain = decrypt_bytes(bytes(value))
                return plain.decode('utf-8')
            except Exception:
                return ''
        return str(value)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        # keep max_length in arguments for migrations/tools
        if self.max_length is not None:
            kwargs['max_length'] = self.max_length
        return name, path, args, kwargs
