from subprocess import run, CalledProcessError
from exception.multichain_error import MultiChainError
import json
import time


class SystemStatusController:

    def __init__(self, blockchain_name: str):
        blockchain_name = blockchain_name.strip()

        if not blockchain_name:
            raise ValueError("Blockchain name can't be empty")

        self._multichain_arg = ['multichain-cli', blockchain_name]
        self._get_peer_info_arg = self._multichain_arg + ['getpeerinfo']
        self._get_wallet_addresses = self._multichain_arg + ['getaddresses']
        self._TARGET_DATE_TIME_FORMAT = '%m-%d-%Y %H:%M:%S'

    def get_peer_info(self):
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
            output = run(self._get_peer_info_arg,
                         check=True, capture_output=True)

            json_peer_info = json.loads(output.stdout)

            # Iterate over each peer and convert the time in seconds since epoch (Jan 1 1970 GMT)
            # to a human readable date and time
            for peer in json_peer_info:
                peer['lastsend'] = time.strftime(
                    self._TARGET_DATE_TIME_FORMAT, time.localtime(int(peer['lastsend'])))
                peer['lastrecv'] = time.strftime(
                    self._TARGET_DATE_TIME_FORMAT, time.localtime(int(peer['lastrecv'])))
                peer['conntime'] = time.strftime(
                    self._TARGET_DATE_TIME_FORMAT, time.localtime(int(peer['conntime'])))

            return json_peer_info
        except CalledProcessError as err:
            raise MultiChainError(err.stderr)
        except Exception as err:
            print(err)

    def __get_wallet_address(self):
        """
        Returns the wallet address for the node that is running this server.
        """
        try:
            output = run(self._get_wallet_addresses,
                         check=True, capture_output=True)

            wallet_addresses = json.loads(output.stdout)
            wallet_address = wallet_addresses[0]

            if not wallet_address:
                raise ValueError('The wallet address is empty')

            return wallet_address
        except CalledProcessError as err:
            raise MultiChainError(err.stderr)
        except Exception as err:
            print(err)

    def get_inactive_nodes(self, nodes_connect_permisison: list):
        """
        Returns a set of wallet address that the node that is running the server is not able to connect to. 
        """
        try:
            nodes_connect_permisison = [node_connect_permission.strip(
            ) for node_connect_permission in nodes_connect_permisison if node_connect_permission.strip()]
            if not nodes_connect_permisison:
                raise ValueError(
                    'The list of nodes with connection permission is empty')

            nodes_address = set()

            # Stores all the nodes that have permissions to connect to the current blockchain
            #
            for node in nodes_connect_permisison:
                nodes_address.add(node['address'])

            connectable_nodes = self.get_peer_info()
            if not connectable_nodes:
                return nodes_address

            connectable_nodes_address = set()

            # Stores all the nodes that are currently connected to the node that is running this server.
            # In other words, all the nodes that are connected to blockchain EXCEPT the node that is running this server.
            #
            for node in connectable_nodes:
                connectable_nodes_address.add(node['handshake'])

            # Adds the wallet address for the node that is running this server as get peer info doesn't return this address.
            #
            connectable_nodes_address.add(self.__get_wallet_address())

            # Returns all the nodes that should be able to connect to the blockchain but are not currently connected.
            #
            return nodes_address.difference(connectable_nodes_address)
        except Exception as err:
            print(err)
