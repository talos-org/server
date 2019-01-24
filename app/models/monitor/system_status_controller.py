from subprocess import run, CalledProcessError
from app.models.exception.multichain_error import MultiChainError
import json
import time


class SystemStatusController:
    MULTICHAIN_ARG = "multichain-cli"
    GET_PEER_INFO_ARG = "getpeerinfo"
    GET_WALLET_ADDRESSES_ARG = "getaddresses"
    TARGET_DATE_TIME_FORMAT = "%m-%d-%Y %H:%M:%S"

    @staticmethod
    def get_peer_info(blockchain_name: str):
        """
        Returns information about the other nodes to which this node is connected. The main information that is returned is:
        "lastsend":                (numeric) The date and time of the last send
        "lastrecv":                (numeric) The data and time of the last receive
        "bytessent":               (numeric) The total bytes sent
        "bytesrecv":               (numeric) The total bytes received
        "conntime":                (numeric) The connection date and time
        "timeoffset":              (numeric) The time offset in seconds
        "pingtime":                (numeric) ping time (if available)
        """
        try:
            blockchain_name = blockchain_name.strip()
            if not blockchain_name:
                raise ValueError("Blockchain name can't be empty")

            args = [
                SystemStatusController.MULTICHAIN_ARG,
                blockchain_name,
                SystemStatusController.GET_PEER_INFO_ARG,
            ]
            output = run(args, check=True, capture_output=True)

            json_peer_info = json.loads(output.stdout)

            # Iterate over each peer and convert the time in seconds since epoch (Jan 1 1970 GMT)
            # to a human readable date and time
            for peer in json_peer_info:
                peer["lastsend"] = time.strftime(
                    SystemStatusController.TARGET_DATE_TIME_FORMAT,
                    time.localtime(int(peer["lastsend"])),
                )
                peer["lastrecv"] = time.strftime(
                    SystemStatusController.TARGET_DATE_TIME_FORMAT,
                    time.localtime(int(peer["lastrecv"])),
                )
                peer["conntime"] = time.strftime(
                    SystemStatusController.TARGET_DATE_TIME_FORMAT,
                    time.localtime(int(peer["conntime"])),
                )

            return json_peer_info
        except CalledProcessError as err:
            raise MultiChainError(err.stderr)
        except Exception as err:
            raise err

    @staticmethod
    def get_wallet_address(blockchain_name: str):
        """
        Returns the wallet address for the node that is running this server.
        """
        try:
            blockchain_name = blockchain_name.strip()
            if not blockchain_name:
                raise ValueError("Blockchain name can't be empty")

            args = [
                SystemStatusController.MULTICHAIN_ARG,
                blockchain_name,
                SystemStatusController.GET_WALLET_ADDRESSES_ARG,
            ]
            output = run(args, check=True, capture_output=True)

            wallet_addresses = json.loads(output.stdout)
            wallet_address = wallet_addresses[0]

            if not wallet_address:
                raise ValueError("The wallet address is empty")

            return wallet_address
        except CalledProcessError as err:
            raise MultiChainError(err.stderr)
        except Exception as err:
            raise err

    @staticmethod
    def get_inactive_nodes(blockchain_name: str, nodes_connect_permisison: list):
        """
        Returns a set of wallet address that the node that is running the server is not able to connect to. 
        """
        try:
            blockchain_name = blockchain_name.strip()
            if not blockchain_name:
                raise ValueError("Blockchain name can't be empty")

            if not nodes_connect_permisison:
                raise ValueError(
                    "The list of nodes with connection permission is empty"
                )

            nodes_address = set()

            # Stores all the nodes that have permissions to connect to the current blockchain
            #
            for node in nodes_connect_permisison:
                nodes_address.add(node["address"])

            connectable_nodes = SystemStatusController.get_peer_info(blockchain_name)
            if not connectable_nodes:
                return nodes_address

            connectable_nodes_address = set()

            # Stores all the nodes that are currently connected to the node that is running this server.
            # In other words, all the nodes that are connected to blockchain EXCEPT the node that is running this server.
            #
            for node in connectable_nodes:
                connectable_nodes_address.add(node["handshake"])

            # Adds the wallet address for the node that is running this server as get peer info doesn't return this address.
            #
            connectable_nodes_address.add(
                SystemStatusController.get_wallet_address(blockchain_name)
            )

            # Returns all the nodes that should be able to connect to the blockchain but are not currently connected.
            #
            return nodes_address.difference(connectable_nodes_address)
        except Exception as err:
            raise err
