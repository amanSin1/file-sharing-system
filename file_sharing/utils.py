from cryptography.fernet import Fernet
from django.conf import settings
import base64
import os

def get_or_create_key():
    """Get or create encryption key"""
    key_file = os.path.join(settings.BASE_DIR, 'encryption.key')
    
    if os.path.exists(key_file):
        with open(key_file, 'rb') as f:
            key = f.read()
    else:
        key = Fernet.generate_key()
        with open(key_file, 'wb') as f:
            f.write(key)
    
    return key

def encrypt_url(data):
    """Encrypt URL data"""
    key = get_or_create_key()
    f = Fernet(key)
    encrypted_data = f.encrypt(data.encode())
    return base64.urlsafe_b64encode(encrypted_data).decode()

def decrypt_url(encrypted_data):
    """Decrypt URL data"""
    try:
        key = get_or_create_key()
        f = Fernet(key)
        decoded_data = base64.urlsafe_b64decode(encrypted_data.encode())
        decrypted_data = f.decrypt(decoded_data)
        return decrypted_data.decode()
    except Exception:
        return None