from subprocess import run, CalledProcessError
from app.models.exception.multichain_error import MultiChainError
import json


class DataStreamController:
    MAX_DATA_COUNT = 10
    MULTICHAIN_ARG = "multichain-cli"
    CREATE_ARG = "create"
    STREAM_ARG = "stream"
    GET_STREAMS_ARG = "liststreams"
    SUBSCRIBE_TO_STREAM_ARG = "subscribe"
    UNSUBSCRIBE_FROM_STREAM_ARG = "unsubscribe"
    DEFAULT_VERBOSE_VALUE = False
    DEFAULT_STREAM_COUNT_VALUE = MAX_DATA_COUNT
    DEFAULT_STREAM_START_VALUE = -MAX_DATA_COUNT
    DEFAULT_STREAMS_LIST_CONTENT = None
    DEFAULT_RESCAN_VALUE = False

    @staticmethod
    def create_stream(blockchain_name: str, stream_name: str, is_open: bool):
        """
        Creates a new stream on the blockchain called name. 
        Pass the value "stream" in the type parameter. If open is true 
        then anyone with global send permissions can publish to the stream, 
        otherwise publishers must be explicitly granted per-stream write permissions. 
        Returns the txid of the transaction creating the stream.
        """
        try:
            blockchain_name = blockchain_name.strip()
            if not blockchain_name:
                raise ValueError("Blockchain name can't be empty")

            stream_name = stream_name.strip()
            if not stream_name:
                raise ValueError("Stream name can't be empty")

            args = [
                DataStreamController.MULTICHAIN_ARG,
                blockchain_name,
                DataStreamController.CREATE_ARG,
                DataStreamController.STREAM_ARG,
                stream_name,
                json.dumps(is_open),
            ]
            output = run(args, check=True, capture_output=True)

            return output.stdout.strip()
        except CalledProcessError as err:
            raise MultiChainError(err.stderr)
        except Exception as err:
            raise err

    @staticmethod
    def get_streams(
        blockchain_name: str,
        streams: list = DEFAULT_STREAMS_LIST_CONTENT,
        verbose: bool = DEFAULT_VERBOSE_VALUE,
        count: int = DEFAULT_STREAM_COUNT_VALUE,
        start: int = DEFAULT_STREAM_START_VALUE,
    ):
        """
        Returns information about streams created on the blockchain. Pass an array
        of stream name(s) to retrieve information about the stream(s), 
        or use the default value for all streams. Use count and start to retrieve part of the 
        list only, with negative start values (like the default) indicating the most recently 
        created streams. Extra fields are shown for streams to which this node has subscribed.
        """
        try:
            blockchain_name = blockchain_name.strip()
            if not blockchain_name:
                raise ValueError("Blockchain name can't be empty")

            stream_selector = "*"
            if streams is not None:
                streams = [stream.strip() for stream in streams if stream.strip()]
                if not streams:
                    raise ValueError("Stream names can't be empty")
                stream_selector = json.dumps(streams)

            args = [
                DataStreamController.MULTICHAIN_ARG,
                blockchain_name,
                DataStreamController.GET_STREAMS_ARG,
                stream_selector,
                json.dumps(verbose),
                json.dumps(count),
                json.dumps(start),
            ]
            streams = run(args, check=True, capture_output=True)
            return json.loads(streams.stdout)
        except CalledProcessError as err:
            raise MultiChainError(err.stderr)
        except Exception as err:
            raise err

    @staticmethod
    def subscribe(blockchain_name: str, streams: list, rescan: bool = DEFAULT_RESCAN_VALUE):
        """
        Instructs the node to start tracking one or more stream(s). 
        These are specified using an array of one or more items. 
        If rescan is true, the node will reindex all items from when the streams 
        were created, as well as those in other subscribed entities. 
        Returns True if successful.
        """
        try:
            blockchain_name = blockchain_name.strip()
            if not blockchain_name:
                raise ValueError("Blockchain name can't be empty")

            streams = [stream.strip() for stream in streams if stream.strip()]
            if not streams:
                raise ValueError("Stream names can't be empty")

            args = [
                DataStreamController.MULTICHAIN_ARG,
                blockchain_name,
                DataStreamController.SUBSCRIBE_TO_STREAM_ARG,
                json.dumps(streams),
                json.dumps(rescan),
            ]
            output = run(args, check=True, capture_output=True)

            # returns True if output is empty (meaning it was a success)
            #
            return not output.stdout.strip()
        except CalledProcessError as err:
            raise MultiChainError(err.stderr)
        except Exception as err:
            raise err

    @staticmethod
    def unsubscribe(blockchain_name: str, streams: list):
        """
        Instructs the node to stop tracking one or more stream(s). 
        Streams are specified using an array of one ore more items.
        """
        try:
            blockchain_name = blockchain_name.strip()
            if not blockchain_name:
                raise ValueError("Blockchain name can't be empty")

            streams = [stream.strip() for stream in streams if stream.strip()]
            if not streams:
                raise ValueError("Stream names can't be empty")

            args = [
                DataStreamController.MULTICHAIN_ARG,
                blockchain_name,
                DataStreamController.UNSUBSCRIBE_FROM_STREAM_ARG,
                json.dumps(streams),
            ]
            output = run(args, check=True, capture_output=True)

            # returns True if output is empty (meaning it was a success)
            #
            return not output.stdout.strip()
        except CalledProcessError as err:
            raise MultiChainError(err.stderr)
        except Exception as err:
            raise err

    @staticmethod
    def resubscribe(blockchain_name: str, streams: list):
        """
        Instructs the node to start tracking one or more stream(s). 
        These are specified using an array of one or more items. 
        The node will reindex all items from when the streams 
        were created, as well as those in other subscribed entities. 
        Returns True if successful.
        """
        try:
            blockchain_name = blockchain_name.strip()
            if not blockchain_name:
                raise ValueError("Blockchain name can't be empty")

            streams = [stream.strip() for stream in streams if stream.strip()]
            if not streams:
                raise ValueError("Stream names can't be empty")

            return DataStreamController.unsubscribe(
                blockchain_name, streams
            ) and DataStreamController.subscribe(blockchain_name, streams, True)
        except CalledProcessError as err:
            raise MultiChainError(err.stderr)
        except Exception as err:
            raise err
