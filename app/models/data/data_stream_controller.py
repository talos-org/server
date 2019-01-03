from subprocess import run, CalledProcessError
from exception.multichain_error import MultiChainError
import json


class DataStreamController:
    MAX_DATA_COUNT = 10

    def __init__(self, blockchain_name: str):
        blockchain_name = blockchain_name.strip()

        if not blockchain_name:
            raise ValueError("Blockchain name can't be empty")

        self._multichain_arg = ['multichain-cli', blockchain_name]
        self._create_arg = self._multichain_arg + ['create']
        self._create_stream_arg = self._create_arg + ['stream']
        self._get_streams_arg = self._multichain_arg + ['liststreams']
        self._subscribe_to_stream_arg = self._multichain_arg + ['subscribe']
        self._unsubscribe_from_stream_arg = self._multichain_arg + \
            ['unsubscribe']

    def create_stream(self, name: str, isOpen: bool):
        """
        Creates a new stream on the blockchain called name. 
        Pass the value "stream" in the type parameter. If open is true 
        then anyone with global send permissions can publish to the stream, 
        otherwise publishers must be explicitly granted per-stream write permissions. 
        Returns the txid of the transaction creating the stream.
        """
        try:
            name = name.strip()
            if not name:
                raise ValueError("Stream name can't be empty")

            args = self._create_stream_arg + [name, json.dumps(isOpen)]
            output = run(args, check=True, capture_output=True)

            return output.stdout.strip()
        except CalledProcessError as err:
            raise MultiChainError(err.stderr)
        except Exception as err:
            print(err)

    def get_streams(self, streams: list = None, verbose: bool = False, count: int = MAX_DATA_COUNT, start: int = -MAX_DATA_COUNT):
        """
        Returns information about streams created on the blockchain. Pass an array
        of stream name(s) to retrieve information about the stream(s), 
        or use the default value for all streams. Use count and start to retrieve part of the 
        list only, with negative start values (like the default) indicating the most recently 
        created streams. Extra fields are shown for streams to which this node has subscribed.
        """
        try:
            stream_selector = '*'
            if streams is not None:
                streams = [stream.strip()
                           for stream in streams if stream.strip()]
                if not streams:
                    raise ValueError("Stream names can't be empty")
                stream_selector = json.dumps(streams)

            args = self._get_streams_arg + [stream_selector, json.dumps(
                verbose), json.dumps(count), json.dumps(start)]
            streams = run(args, check=True, capture_output=True)
            return json.loads(streams.stdout)
        except CalledProcessError as err:
            raise MultiChainError(err.stderr)
        except Exception as err:
            print(err)

    def subscribe(self, streams: list, rescan: bool = False):
        """
        Instructs the node to start tracking one or more stream(s). 
        These are specified using an array of one or more items. 
        If rescan is true, the node will reindex all items from when the streams 
        were created, as well as those in other subscribed entities. 
        Returns True if successful.
        """
        try:
            streams = [stream.strip() for stream in streams if stream.strip()]
            if not streams:
                raise ValueError("Stream names can't be empty")

            args = self._subscribe_to_stream_arg + \
                [json.dumps(streams), json.dumps(rescan)]
            output = run(args, check=True, capture_output=True)

            # returns True if output is empty (meaning it was a success)
            #
            return not output.stdout.strip()
        except CalledProcessError as err:
            raise MultiChainError(err.stderr)
        except Exception as err:
            print(err)

    def unsubscribe(self, streams: list):
        """
        Instructs the node to stop tracking one or more stream(s). 
        Streams are specified using an array of one ore more items.
        """
        try:
            streams = [stream.strip() for stream in streams if stream.strip()]
            if not streams:
                raise ValueError("Stream names can't be empty")

            args = self._unsubscribe_from_stream_arg + [json.dumps(streams)]
            output = run(args, check=True, capture_output=True)

            # returns True if output is empty (meaning it was a success)
            #
            return not output.stdout.strip()
        except CalledProcessError as err:
            raise MultiChainError(err.stderr)
        except Exception as err:
            print(err)

    def resubscribe(self, streams: list):
        """
        Instructs the node to start tracking one or more stream(s). 
        These are specified using an array of one or more items. 
        The node will reindex all items from when the streams 
        were created, as well as those in other subscribed entities. 
        Returns True if successful.
        """
        try:
            streams = [stream.strip() for stream in streams if stream.strip()]
            if not streams:
                raise ValueError("Stream names can't be empty")

            return self.unsubscribe(streams) and self.subscribe(streams, True)
        except CalledProcessError as err:
            raise MultiChainError(err.stderr)
        except Exception as err:
            print(err)
