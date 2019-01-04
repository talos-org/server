import json


class MultiChainError(Exception):
    def __init__(self, message: str):
        super().__init__(message.decode())
        self.message_parts = self.__initialize_message_parts(message.decode())
        print(self.message_parts)

    def __initialize_message_parts(self, message: str):
        return list(filter(None, message.split("\n")))

    def get_error_code(self):
        if len(self.message_parts) == 1:
            return "N/A"
        return self.message_parts[1].split(": ")[1]

    def get_error_message(self):
        if len(self.message_parts) == 1:
            return self.message_parts[0].split(": ")[1]
        return "\n".join(self.message_parts[3:])

    def get_multichain_parameters(self):
        if len(self.message_parts) == 1:
            return "N/A"
        return json.loads(self.message_parts[0])

    def get_info(self):
        error_data = {}
        error_data["error"] = {}
        error_data["error"]["code"] = self.get_error_code()
        error_data["error"]["message"] = self.get_error_message()
        error_data["error"]["MutliChainParameters"] = self.get_multichain_parameters()
        return error_data
