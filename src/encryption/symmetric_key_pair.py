class SymmetricKeyPair:
    def __init__(self, key, iv):
        self._key = key
        self._iv = iv
    
    def get_key(self):
        return self._key
    
    def get_iv(self):
        return self._iv
