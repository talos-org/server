import json


class MultiChainError(Exception):

    def __init__(self, message: str):
        super().__init__(message.decode())
        self.message_parts = self.__initialize_message_parts(message.decode())

    def __initialize_message_parts(self, message: str):
        return list(filter(None, message.split("\n")))

    def get_error_code(self):
        return self.message_parts[1].split(": ")[1]

    def get_error_message(self):
        return '\n'.join(self.message_parts[3:])

    def get_multichain_parameters(self):
        return json.loads(self.message_parts[0])
