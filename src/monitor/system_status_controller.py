from subprocess import run, CalledProcessError
from shlex import quote
from exception.multichain_error import MultiChainError
import json
import time


class SystemStatusController:

    def __init__(self, blockchain_name: str):
        self._multichain_arg = ['multichain-cli', quote(blockchain_name)]
        self._get_peer_info_arg = self._multichain_arg + ['getpeerinfo']
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
    
    def get_inactive_nodes(self, nodes_connect_permisison: list):
        """
        Returns a set of wallet address that are not connectable. 
        """
        try:
            nodes_connect_permisison = [node_connect_permission.strip() for node_connect_permission in nodes_connect_permisison if node_connect_permission.strip()]
            if not nodes_connect_permisison:
                raise ValueError('The list of nodes with connection permission is empty')

            nodes_address = set()

            for node in nodes_connect_permisison:
                nodes_address.add(node['address'])

            connectable_nodes = self.get_peer_info()
            if not connectable_nodes:
                return nodes_address
            
            connectable_nodes_address = set()

            for node in connectable_nodes:
                connectable_nodes_address.add(node['handshake']) 
            
            return nodes_address.difference(connectable_nodes_address)
        except Exception as err:
            print(err)

