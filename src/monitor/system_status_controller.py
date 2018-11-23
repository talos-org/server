from subprocess import run, CalledProcessError
from shlex import quote
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
            print(err.stderr)
        except Exception as err:
            print(err)
