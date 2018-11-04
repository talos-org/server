import binascii
import os

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.serialization import (load_pem_private_key,
                                                          load_pem_public_key)

from .asymmetric_key_pair import AsymmetricKeyPair
from .symmetric_key_pair import SymmetricKeyPair
from .key_data import KeyData


class EncrytpionController:
    def __init__(self, private_key_pem):
        self._backend = default_backend()
        self._generated_secret_keys = []
        self._user_private_key = self.__get_private_key_object(private_key_pem)
        self._user_public_key = self._user_private_key.public_key()
        self._user_public_key_pem = self.__asymmetric_key_to_pem(
            self._user_private_key.public_key())

    def __get_private_key_object(self, private_key_pem):
        private_key = load_pem_private_key(
            private_key_pem, None, self._backend)
        return private_key

    def __get_public_key_object(self, public_key_pem):
        public_key = load_pem_public_key(public_key_pem, backend=self._backend)
        return public_key

    def get_user_public_key(self):
        return self._user_public_key_pem

    def encrypt_data(self, data, public_keys_pem):
        symmetric_key_pair = self.__generate_symmetric_key_pair()
        self._generated_secret_keys.append(symmetric_key_pair)

        enc_data = self.__encrypt_data(
            data, symmetric_key_pair.get_key, symmetric_key_pair.get_iv)

        # Stores the encrypted symmetric key for each public key provided
        #
        public_key_symmetric_key_map = self.__encrypt_symmetric_key_with_public_keys(
            SymmetricKeyPair.get_key(), public_keys_pem)

        key_data = KeyData(public_key_symmetric_key_map,
                           symmetric_key_pair.get_iv(), enc_data)
        return key_data

    def __encrypt_symmetric_key_with_public_keys(self, symmetric_key, public_keys_pem):
        public_key_symmetric_key_map = {}
        public_keys_pem.append(self._user_public_key_pem)
        for public_key in public_keys_pem:
            public_key_symmetric_key_map[public_key] = self.__encrypt_symmetric_key_with_public_key(
                symmetric_key, public_key)
        return public_key_symmetric_key_map

    def __generate_symmetric_key_pair(self):
        key = os.urandom(32)
        iv = os.urandom(16)
        return SymmetricKeyPair(key, iv)

    def __encrypt_symmetric_key_with_public_key(self, symmetric_key, public_key_pem):
        public_key = self.__get_public_key_object(public_key_pem)
        enc_key = public_key.encrypt(
            symmetric_key.encode(),
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return enc_key

    def __asymmetric_key_to_pem(self, key):
        key_pem = key.prviate_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption())
        return key_pem

    def __generate_asymetric_key_pair(self):
        private_key = rsa.generate_private_key(public_exponent=65537,
                                               key_size=4096,
                                               backend=self._backend())
        private_key_pem = self.__asymmetric_key_to_pem(private_key)
        public_key = private_key.public_key()
        public_key_pem = self.__asymmetric_key_to_pem(public_key)
        return AsymmetricKeyPair(private_key_pem, public_key_pem)

    def __encrypt_data(self, data, secret_key, iv):
        cipher = Cipher(algorithms.AES(secret_key),
                        modes.CBC(iv), backend=self._backend)
        encryptor = cipher.encryptor()
        cipher_text = encryptor.update(data.encode()) + encryptor.finalize()
        hex_cipher_text = binascii.hexlify(cipher_text)
        return hex_cipher_text

    def __decrypt_data(self, enc_data):
        cipher = Cipher(algorithms.AES(secret_key),
                        modes.CBC(secret_key), backend=self._backend)
        encryptor = cipher.encryptor()
        cipher_text = encryptor.update(data.encode()) + encryptor.finalize()
        hex_cipher_text = binascii.hexlify(cipher_text)
        return hex_cipher_text
