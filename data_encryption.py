from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.fernet import Fernet
import base64


def generate_key(password, salt):
    # Make byte strings out of character ones
    password_bytes = password.encode()
    salt_byte = salt.encode()

    # Create a key based on hashed password
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt_byte,
        iterations=600000,
        backend=default_backend()
    )
    key = base64.urlsafe_b64encode(kdf.derive(password_bytes))

    return key


def encrypt(plain_text, key):
    cipher_suite = Fernet(key)

    encrypted = cipher_suite.encrypt(plain_text.encode())
    return encrypted


def encrypt_many(data_list, key):
    for i in range(len(data_list)):
        data = data_list[i]
        if data is not None:
            data_list[i] = encrypt(data, key)

    return data_list


def decrypt(encrypted_text, key):
    cipher_suite = Fernet(key)

    decrypted = cipher_suite.decrypt(encrypted_text)
    return decrypted.decode()


def decrypt_many(data_list, key):
    for i in range(len(data_list)):
        data = data_list[i]
        if data is not None:
            data_list[i] = decrypt(data, key)

    return data_list
