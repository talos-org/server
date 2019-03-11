from subprocess import run, CalledProcessError
import re
from app.models.exception.multichain_error import MultiChainError


class NodeController:
    MULTICHAIN_CLI_ARG = ["multichain-cli"]
    MULTICHAIN_D_ARG = ["multichaind"]
    CONNECT_ARG = ["connect"]
    GRANT_ARG = ["grant"]

    @staticmethod
    def connect_to_admin_node(admin_node_address: str):
        """
        Initializes the connection between the current node and the admin
        :param admin_node_address: Node address of the admin node
        If successful, it returns a wallet address, which must used on the admin node to verify
        """
        cmd = NodeController.MULTICHAIN_D_ARG + [admin_node_address]
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

    @staticmethod
    def add_node(blockchain_name: str,new_node_wallet_address: str):
        """
        Adds a node to the blockchain network with the provided wallet address of the node
        that was generated in the connection process.
        :param new_node_wallet_address:
        :return:
        """
        cmd = (
            NodeController.MULTICHAIN_CLI_ARG
            +[blockchain_name]
            + NodeController.GRANT_ARG
            + [new_node_wallet_address]
            + NodeController.CONNECT_ARG
        )
        try:
            output = run(cmd, capture_output=True)
            return output.stdout.strip()
        except CalledProcessError as err:
            raise MultiChainError(err.stderr)
        except Exception as err:
            raise err
