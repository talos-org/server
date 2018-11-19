class KeyData:
    def __init__(self, public_key_symmetric_key_map, enc_data):
        self._public_key_symmetric_key_map = public_key_symmetric_key_map
        self._enc_data = enc_data
    
    def get_public_key_symmetric_key_map(self):
        return self._public_key_symmetric_key_map
    
    def get_encypted_data(self):
        return self._enc_data