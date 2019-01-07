import nacl.secret
import nacl.utils
from nacl.public import PrivateKey, SealedBox, PublicKey

from app.models.encryption.asymmetric_key_pair import AsymmetricKeyPair
from app.models.encryption.encoded_asymmetric_key_pair import EncodedAsymmetricKeyPair
from app.models.encryption.key_data import KeyData

KEY_ENCODING = nacl.encoding.Base64Encoder


class EncrytpionController:
    def __init__(self, private_key: str = None):
        """
        If private key is None that means it is the first user (Admin)
        """
        asymmetricKeyPair = None
        if private_key == None:
            asymmetricKeyPair = self.__generate_asymetric_key_pair()
        else:
            asymmetricKeyPair = self.__get_asymmetric_key_Pair(private_key)

        self._user_private_key = asymmetricKeyPair.get_private_key()
        self._user_public_key = asymmetricKeyPair.get_public_key()

    def get_user_public_key(self):
        """
        returns the encoded public key of the current user
        """
        return self.__encode_key(self._user_public_key)

    def encrypt_data(self, data: str, public_keys: list):
        """
        Generates a random secret key that is used to encrypt the data. The randomly
        generated secret key is then encrypted using the public key of each user that
        should view the data. The encrypted data as well as a map of public to encrypted
        secret key is returned  
        """
        # Generates a random secret key and encrypts the data provided
        #
        symmetric_key = self.__generate_symmetric_key()
        enc_data = self.__encrypt_data(data, symmetric_key)

        # Encrypts the secret key for each public key and stores a map
        # of the public key to encrypted secret key
        # Stores the encrypted symmetric key for each public key provided
        #
        public_key_symmetric_key_map = self.__encrypt_symmetric_key_with_public_keys(
            symmetric_key, public_keys
        )

        key_data = KeyData(public_key_symmetric_key_map, enc_data)
        return key_data

    def decrypt_data(self, enc_data: str, enc_symmetric_key):
        """
        Using the current users private key, the encrypted symmetric key is decrypted.
        Then using the symmetric key, the encrypted data is decrypted and returned
        """
        # Decrypts the encrypted symmetric key
        #
        unseal_box = SealedBox(self._user_private_key)
        symmetric_key = unseal_box.decrypt(enc_symmetric_key)

        # Decrypts the data using the symmetric key
        #
        symmetric_box = nacl.secret.SecretBox(symmetric_key)
        plain_text = symmetric_box.decrypt(enc_data)

        return plain_text

    def generate_asymetric_key_pair(self):
        """
        Return a randomly generated public and private key pair that is encoded
        """
        asym_key_pair = self.__generate_asymetric_key_pair()
        return EncodedAsymmetricKeyPair(
            self.__encode_key(asym_key_pair.get_private_key()),
            self.__encode_key(asym_key_pair.get_public_key()),
        )

    def __encrypt_symmetric_key_with_public_keys(
        self, symmetric_key, encoded_public_keys
    ):
        """
        Encrypts the symmetric key using each public key. It then returns
        a map of public keys to their corresponding encrytped symmetric key
        """
        public_key_symmetric_key_map = {}
        encoded_public_keys.append(self.__encode_key(self._user_public_key))
        for encoded_public_key in encoded_public_keys:
            public_key_symmetric_key_map[
                encoded_public_key
            ] = self.__encrypt_symmetric_key_with_public_key(
                symmetric_key, encoded_public_key
            )
        return public_key_symmetric_key_map

    def __encode_key(self, key):
        """
        returns an encoded verison of the key passed in. The key is encoded using
        the default encoding
        """
        return key.encode(encoder=KEY_ENCODING)

    def __decode_key(self, key_type, key):
        """
        Returns an key object that represents the key provided. The key is decoded
        using the default encoding
        """
        return key_type(key, encoder=KEY_ENCODING)

    def __generate_symmetric_key(self):
        """
        Returns a randomly generated symmetric key
        """
        key = nacl.utils.random(nacl.secret.SecretBox.KEY_SIZE)
        return key

    def __get_asymmetric_key_Pair(self, encoded_private_key: str):
        """
        Returns an asymmetric key pair object given the encoded private key.
        The public and private keys inside this object are both objects
        """
        private_key = PrivateKey(encoded_private_key, encoder=KEY_ENCODING)
        public_key = private_key.public_key
        return AsymmetricKeyPair(private_key, public_key)

    def __encrypt_symmetric_key_with_public_key(
        self, symmetric_key, encoded_public_key
    ):
        """
        Returns an encrypted symmetric key that has been encrypted using the provided
        public key
        """
        public_key = self.__decode_key(PublicKey, encoded_public_key)
        user_box = SealedBox(public_key)
        enc_key = user_box.encrypt(symmetric_key)
        return enc_key

    def __generate_asymetric_key_pair(self):
        """
        Returns a randomly generated asymmetric key pair. 
        The key pair is returned in an object that stores both keys
        """
        secret_key = PrivateKey.generate()
        public_key = secret_key.public_key
        return AsymmetricKeyPair(secret_key, public_key)

    def __encrypt_data(self, data: str, secret_key):
        """
        Encrypts the data using the proivded secret key. The encrypted data
        is then returned 
        """
        box = nacl.secret.SecretBox(secret_key)
        cipher_text = box.encrypt(data.encode())
        return cipher_text
