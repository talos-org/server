from subprocess import run, CalledProcessError
import re
from app.models.exception.multichain_error import MultiChainError


class NodeController:
    def __init__(self, blockchain_name: str):
        self._blockchain_name = blockchain_name
        self._multichain_cli_arg = ["multichain-cli", blockchain_name]
        self._multichain_d_arg = ["multichaind"]
        self._connect_arg = ["connect"]
        self._grant_arg = ["grant"]

    def connect_to_admin_node(self, admin_node_address: str):
        """
        Initializes the connection between the current node and the admin
        :param admin_node_address: Node address of the admin node
        If successful, it returns a wallet address, which must used on the admin node to verify
        """
        cmd = self._multichain_d_arg + [admin_node_address]
        try:
            output = run(cmd, capture_output=True)
            return (
                re.findall(
                    r"(?<=grant )(.*)(?= connect\\n)", str(output.stdout.strip())
                )
            )[0]
        except CalledProcessError as err:
            raise MultiChainError(err.stderr)
        except Exception as err:
            raise err

    def add_node(self, new_node_wallet_address: str):
        """
        Adds a node to the blockchain network with the provided wallet address of the node
        that was generated in the connection process.
        :param new_node_wallet_address:
        :return:
        """
        cmd = (
            self._multichain_cli_arg
            + self._grant_arg
            + [new_node_wallet_address]
            + self._connect_arg
        )
        try:
            output = run(cmd, capture_output=True)
            return output.stdout.strip()
        except CalledProcessError as err:
            raise MultiChainError(err.stderr)
        except Exception as err:
            raise err

    def remove_node(self):  # Have not implemented this yet
        """
        Removes node from current chain....
        :return:
        """
        print("N/A")
