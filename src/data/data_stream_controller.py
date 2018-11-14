from plumbum import local, FG, BG, TF, RETCODE, ProcessExecutionError
import json


class DataStreamController:
    MAX_DATA_COUNT = 10

    def __init__(self):
        self._multichain = local['multichain-cli']['talos']
        self._create = self._multichain['create']
        self._create_stream = self._create['stream']
        self._get_streams = self._multichain['liststreams']
        self._subscribe_to_stream = self._multichain['subscribe']
        self._unsubscribe_from_stream = self._multichain['unsubscribe']

    def create_stream(self, name: str, isOpen: bool):
        """
        Creates a new stream on the blockchain called name. 
        Pass the value "stream" in the type parameter. If open is true 
        then anyone with global send permissions can publish to the stream, 
        otherwise publishers must be explicitly granted per-stream write permissions. 
        Returns the txid of the transaction creating the stream.
        """
        try:

            output = self._create_stream[name, json.dumps(isOpen)].run(retcode=0)

            return output[1].strip()
        except ProcessExecutionError as err:
            print(err.args[3])
        except Exception as err:
            print(err)

    def get_streams(self, streams: list = None, verbose: bool = False, count: int = MAX_DATA_COUNT, start: int = -MAX_DATA_COUNT):
        """
        Returns information about streams created on the blockchain. Pass an array
        of stream name(s) to retrieve information about the stream(s), 
        or * for all streams. Use count and start to retrieve part of the 
        list only, with negative start values (like the default) indicating the most recently 
        created streams. Extra fields are shown for streams to which this node has subscribed.
        """
        try:
            stream_selector = '*'
            if streams is not None:
                stream_selector = json.dumps(streams)

            streams = self._get_streams[stream_selector, json.dumps(
                verbose), json.dumps(count), json.dumps(start)].run(retcode=0)

            return streams[1].strip()
        except ProcessExecutionError as err:
            print(err.args[3])
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
            output = self._subscribe_to_stream[
                json.dumps(streams), json.dumps(rescan)].run(retcode=0)
            output = output[1].strip()
            
            if not output:
                return True
            else:
                return False
        except ProcessExecutionError as err:
            print(err.args[3])
        except Exception as err:
            print(err)

    def unsubscribe(self, streams: list):
        """
        Instructs the node to stop tracking one or more stream(s). 
        Streams are specified using an array of one ore more items.
        """
        try:
            output = self._unsubscribe_from_stream[json.dumps(
                streams)].run(retcode=0)
            output =  output[1].strip()

            if not output:
                return True
            else:
                return False
        except ProcessExecutionError as err:
            print(err.args[3])
        except Exception as err:
            print(err)
